import json
from collections import OrderedDict

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.module_loading import import_string
from django.utils.functional import cached_property

from rest_framework.utils.encoders import JSONEncoder
from netdiff import diff, NetJsonParser

from ..base import TimeStampedEditableModel
from ..settings import PARSERS
from ..settings import UPDATE_HISTORY_LEN
from ..contextmanagers import log_on_fail


@python_2_unicode_compatible
class BaseTopology(TimeStampedEditableModel):
    label = models.CharField(_('label'), max_length=64)
    parser = models.CharField(_('format'),
                              choices=PARSERS,
                              max_length=128,
                              help_text=_('Select topology format'))
    url = models.URLField(_('url'), help_text=_('Topology data will be fetched from this URL'))

    # the following fields will be filled automatically
    protocol = models.CharField(_('protocol'), max_length=64, blank=True)
    version = models.CharField(_('version'), max_length=24, blank=True)
    revision = models.CharField(_('revision'), max_length=64, blank=True)
    metric = models.CharField(_('metric'), max_length=24, blank=True)

    class Meta:
        verbose_name_plural = _('topologies')
        abstract = True

    def __str__(self):
        return '{0} - {1}'.format(self.label, self.get_parser_display())

    @cached_property
    def parser_class(self):
        return import_string(self.parser)

    @property
    def latest(self):
        return self.parser_class(self.url, timeout=5)

    def diff(self):
        """ shortcut to netdiff.diff """
        latest = self.latest
        if UPDATE_HISTORY_LEN:
            current = NetJsonParser(
                OrderedDict((
                            ('type', 'NetworkGraph'),
                            ('protocol', self.parser_class.protocol),
                            ('version', self.parser_class.version),
                            ('metric', self.parser_class.metric),
                            ('label', self.label),
                            ('id', str(self.id)),
                            ('parser', self.parser),
                            ('created', self.created),
                            ('modified', self.modified),
                            ('nodes', []),
                            ('links', [])
                            ))
                )
        else:
            current = NetJsonParser(self.json(dict=True))
        return diff(current, latest)

    def json(self, dict=False, **kwargs):
        """ returns a dict that represents a NetJSON NetworkGraph object """
        nodes = []
        links = []
        # populate graph
        from . import Update  # avoid circular dependency
        latest_update = Update.objects.latest('timestamp')
        for link in self.link_set.select_related('source', 'target').\
                filter(update_id=latest_update):
            links.append(link.json(dict=True))
        for node in self.node_set.all().filter(update_id=latest_update):
            nodes.append(node.json(dict=True))
        netjson = OrderedDict((
            ('type', 'NetworkGraph'),
            ('protocol', self.parser_class.protocol),
            ('version', self.parser_class.version),
            ('metric', self.parser_class.metric),
            ('label', self.label),
            ('id', str(self.id)),
            ('parser', self.parser),
            ('created', self.created),
            ('modified', self.modified),
            ('nodes', nodes),
            ('links', links)
        ))
        if dict:
            return netjson
        return json.dumps(netjson, cls=JSONEncoder, **kwargs)

    def update(self):
        """
        Updates topology
        Links are not deleted straightaway but set as "down"
        """
        from . import Link, Node, Update  # avoid circular dependency
        u = None
        last_update = Update.objects.last()
        store_new = UPDATE_HISTORY_LEN
        if last_update:
            if store_new:
                u = Update()
                u.save()
            else:
                u = last_update
        else:
            u = Update()
        u.save()

        diff = self.diff()

        status = {
            'added': 'up',
            'removed': 'down',
            'changed': 'up'
        }
        action = {
            'added': 'add',
            'changed': 'change',
            'removed': 'remove'
        }

        try:
            added_nodes = diff['added']['nodes']
        except TypeError:
            added_nodes = []

        for node_dict in added_nodes:
            if not store_new:
                node = Node.count_address(node_dict['id'])
                if node:  # pragma no cover
                    continue
            addresses = '{0};'.format(node_dict['id'])
            addresses += ';'.join(node_dict.get('local_addresses', []))
            properties = node_dict.get('properties', {})
            node = Node(addresses=addresses,
                        properties=properties,
                        topology=self, update=u)
            node.full_clean()
            node.save()

        for section, graph in sorted(diff.items()):
            # if graph is empty skip to next one
            if not graph:
                continue
            for link_dict in graph['links']:
                changed = False
                link = Link.get_from_nodes(link_dict['source'],
                                           link_dict['target'])
                if not link or store_new:
                    source = Node.get_from_address_and_update(
                        link_dict['source'], u.id)
                    target = Node.get_from_address_and_update(
                        link_dict['target'], u.id)
                    link = Link(source=source,
                                target=target,
                                cost=link_dict['cost'],
                                properties=link_dict.get('properties', {}),
                                topology=self, update=u)
                    changed = True
                # links in changed and removed sections
                # are always changing therefore needs to be saved
                if section in ['changed', 'removed']:
                    link.status = status[section]
                    link.cost = link_dict['cost']
                    changed = True
                # perform writes only if needed
                if changed:
                    with log_on_fail(action[section], link):
                        link.full_clean()
                        link.save()
        if store_new:
            Update().cleanup()
