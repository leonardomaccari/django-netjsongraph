from django.db import models
from ..settings import UPDATE_HISTORY_LEN


class Update(models.Model):
    timestamp = models.DateTimeField(auto_now=True,
                                     blank=False)

    class Meta():
        ordering = ['timestamp']

    def __str__(self):
        return 'update %s' % str(self.timestamp)

    def cleanup(self):
        old_updates = Update.objects.all()
        if len(old_updates) < UPDATE_HISTORY_LEN or not UPDATE_HISTORY_LEN:
            return
        for up in old_updates[:len(old_updates) - UPDATE_HISTORY_LEN]:
            up.delete()

    def return_related_objects(self):
        """ for debug only """
        for i, u in enumerate(Update.objects.all()):
            print u.id,
            print len(u.link_set.all()),
            print len(u.node_set.all()),
            if i < len(Update.objects.all()) - UPDATE_HISTORY_LEN:
                print "*"
            else:
                print ""
