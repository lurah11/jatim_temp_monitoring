from django.db import models

# Create your models here.
class City(models.Model): 
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude= models.FloatField()
    code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.id}--{self.name}"
    
class Temp(models.Model): 
    city = models.ForeignKey(City,on_delete=models.CASCADE)
    date = models.DateField()
    tmax = models.FloatField()
    tmin = models.FloatField()
    humax = models.FloatField()
    humin = models.FloatField()

    def __str__(self): 
        return f"{self.id}-{self.city.name}--{self.date}"