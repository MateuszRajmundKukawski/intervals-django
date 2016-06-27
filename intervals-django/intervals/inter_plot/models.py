from django.db import models


class GpxData(models.Model):
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    gpx = models.TextField()
    description = models.CharField(max_length=200)

    def __str__(self):
        return '{} - {}'.format(self.description, self.pub_date)