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
    tail_number = models.CharField(max_length=50, unique=True)  # tail number 
    contract_number = models.CharField(max_length=255)
    active_status = models.BooleanField(default=False)
    delivery_date = models.DateField(null=True, blank = True) # ATP date 
    delivery_location = models.CharField(max_length=255, blank=True, null=True)
    current_location = models.CharField(max_length=255, blank=True, null=True)
    army_command = models.CharField(max_length=255, blank=True, null=True)
    unit_name = models.CharField(max_length=250, blank=True, null=True)
    formation = models.CharField(max_length=250, blank=True, null=True)
    warranty_period = models.IntegerField(help_text="Warranty in months", default=24)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.contract_number} ({self.tail_number})"
    
    @property
    def warranty_expiry_date(self):
        if not self.delivery_date:
            return None
        return self.delivery_date + relativedelta(months=self.warranty_period)

    @property
    def warranty_status(self):
        if not self.delivery_date:
            return "Not Started"
        return "Expired" if date.today() > self.warranty_expiry_date else "Active"
    
    def save(self, *args, **kwargs):
        if self.tail_number:
            self.tail_number = self.tail_number.upper()  # Convert to uppercase before saving
        super().save(*args, **kwargs)

    