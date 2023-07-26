from django.db import models


class Location(models.Model):
    address_name = models.CharField(
        max_length=255,
        unique=True)
    lat = models.FloatField()
    long = models.FloatField()
    created_at = models.DateTimeField(
        auto_now=True,
        db_index=True)


    @property
    def my_coordinates(self):
        return (self.long, self.lat)
