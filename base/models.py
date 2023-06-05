from decimal import Decimal
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.text import slugify
from uuid import uuid4
import os

# Create your models here.

SIZE_CHOICES = (
    ('X', 'X'),
    ('XL', 'XL'),
)

COLOR_CHOICES = (
    ('Red', 'Red'),
    ('Black', 'Black'),
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

def avatar_upload_path(instance, filename):
    upload_to = "profiles"
    ext = filename.split('.')[-1]
    
    if instance.pk:
        filename = "{}.{}".format(instance.pk, ext)
    else:
        filename = "{}.{}".format(uuid4().hex, ext)
    return os.path.join(upload_to, filename)

def image_upload_path(instance, filename):
    upload_to = "products"
    ext = filename.split('.')[-1]
    
    if instance.pk:
        filename = "{}.{}".format(instance.pk, ext)
    else:
        filename = "{}.{}".format(uuid4().hex, ext)
    return os.path.join(upload_to, filename)


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, max_length=254, null=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, default="avatar.png", null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name if self.name == '' else self.user.username
    
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.name
    
class Item(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    in_stock = models.IntegerField()
    discount_percent = models.IntegerField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    slug = models.SlugField(max_length=255)
    item_size = models.CharField(choices=SIZE_CHOICES, max_length=3, )
    item_color = models.CharField(choices=COLOR_CHOICES, max_length=10)
    image = models.ImageField(upload_to=image_upload_path)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product", kwargs={"slug": self.slug})

    @property
    def get_item_image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    @property
    def get_item_rating(self):
        total = 0
        itemratings = self.reviewproduct_set.all()
        total = sum([rate.rate_count for rate in itemratings])
        return total
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordere_date = models.DateTimeField(null=True)
    complete = models.BooleanField(default=False)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True)
    transaction_id = models.CharField(max_length=100, null=True)
    billing_addres = models.ForeignKey("Address", related_name="billing_addres", on_delete=models.SET_NULL, null=True, blank=True)
    shipping_addres = models.ForeignKey("Address", related_name="shipping_addres", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.id)        
    
    @property
    def get_cart_total(self):
        total = 0
        orderItem = self.orderitem_set.all()
        total = sum([item.get_final_total for item in orderItem])
        return total
    
    @property
    def get_coupon_discount(self):
        total = 0
        if self.coupon:
            total = self.get_cart_total * (self.coupon.discount / Decimal('100'))
        return total
    
    @property
    def get_finally_total(self):
        total = 0
        if self.coupon:
            total = self.get_cart_total - self.get_coupon_discount
        return total
    
    @property
    def get_quantity_total(self):
        total = 0
        orderItem = self.orderitem_set.all()
        total = sum([item.quantity for item in orderItem])
        return total
    
    
class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    ordered_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    @property
    def get_total(self):
        total = 0
        total = self.quantity * self.item.price
        return total

    @property
    def get_discount_price(self):
        total = 0
        if self.item.discount_percent:
            total = self.get_total * (self.item.discount_percent / Decimal('100') )
        return total
    
    @property
    def get_final_total(self):
        total = 0
        total = self.get_total - self.get_discount_price
        return total

class Coupon(models.Model):
    code = models.CharField(max_length=15)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField()

    def __str__(self):
        return self.code
    
class CouponUse(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    use_count = models.IntegerField(default=0)

class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=True)
    apartment = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    zipcode = models.CharField(max_length=200, null=True)
    telephone = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return str(self.id)

class NewsLetter(models.Model):
    email = models.EmailField(unique=True, max_length=255)
    
    def __str__(self):
        return self.email
    
    
class ReviewProduct(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=254, null=True)
    description = models.TextField(null=True)
    rate_count = models.IntegerField()
    
    def __str__(self):
        return self.item.title
    
    
    

