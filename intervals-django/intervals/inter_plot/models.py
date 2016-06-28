from django.db import models


class GpxData(models.Model):
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    gpx = models.TextField()
    description = models.CharField(max_length=200)
    training_date = models.DateField()

    def __str__(self):
        return '{} - {}'.format(self.description, self.training_date)