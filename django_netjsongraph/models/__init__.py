from .topology import BaseTopology
from .node import BaseNode
from .link import BaseLink
from .update import Update


class Topology(BaseTopology):
    class Meta(BaseTopology.Meta):
        abstract = False


class Node(BaseNode):
    pass


class Link(BaseLink):
    pass
