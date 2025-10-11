from django.db import models
from dateutil.relativedelta import relativedelta 
from datetime import date 

class Product_model(models.Model):
    # this contains all product model that our company manufecture 
    # like JF2 , JM1, JM2.. etc
    model_name = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self): 
        return self.model_name 
    
# Create your models here.
class Product(models.Model):
    # this table contain information of each models products
    product_model = models.ForeignKey(Product_model,on_delete=models.CASCADE,null=True,blank=True)
    product_code = models.CharField(max_length=50, unique=True)  # tail number 
    order_name = models.CharField(max_length=255)
    manufecturing_Date = models.DateField()
    is_sold = models.BooleanField(default=False)
    sold_date = models.DateField(null=True, blank = True) # ATP date 
    source_location = models.CharField(max_length=255, blank=True, null=True)
    army_command = models.CharField(max_length=255, blank=True, null=True)
    unit_name = models.CharField(max_length=250, blank=True, null=True)
    formation = models.CharField(max_length=250, blank=True, null=True)
    warranty_period = models.IntegerField(help_text="Warranty in months", default=24)

    def __str__(self):
        return f"{self.order_name} ({self.product_code})"
    
    @property
    def warranty_expiry_date(self):
        expiry = self.manufecturing_Date + relativedelta(months=self.warranty_period)
        return expiry

    @property
    def warranty_status(self): 
        return "Expired" if date.today() > self.warranty_expiry_date else "Active"

    