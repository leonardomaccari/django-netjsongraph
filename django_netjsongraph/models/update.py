from django.db import models


class Update(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True,
                                     blank=False)

    def __str__(self):
        return 'update %s' % str(self.timestamp)
