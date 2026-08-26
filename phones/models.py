from django.db import models
class Phone(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    image = models.URLField(max_length=500)
    release_date = models.DateField()
    lte_exists = models.BooleanField()
    slug = models.SlugField(max_length=255, unique=True)


    def __str__(self):
        return f"{self.name} - {self.price} ₽"