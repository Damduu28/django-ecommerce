from django.contrib import admin

# Register your models here.

from .models import *

class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title", )}
    
    
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'valid_from', 'valid_to', 'discount']
    
    
class CouponUseAdmin(admin.ModelAdmin):
    list_display = ['customer', 'coupon', 'use_count']
    
    


admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Address)
admin.site.register(NewsLetter)
admin.site.register(ReviewProduct)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(CouponUse, CouponUseAdmin)
