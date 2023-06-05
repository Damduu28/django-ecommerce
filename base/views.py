from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from .models import *
import json

# Create your views here.

from .forms import *

def homePage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    category = request.GET.get('category') if request.GET.get('category') != None else ''
    if request.user.is_authenticated:
        customer = request.user.customer
        order = Order.objects.filter(customer=customer, complete=False).first()
        orderItems = order.orderitem_set.all()
        orderItem_count = order.orderitem_set.count()
    
    items = Item.objects.filter(
        (Q(category__name__icontains=q)) |
        (Q(category__name__icontains=category) & Q(title__icontains=q))
    )
    categories = Category.objects.all()
    context = {
        'items': items,
        'order': order,
        'orderItems': orderItems,
        'categories': categories,
        'orderItem_count': orderItem_count,
    }
    return render(request, "base/home.html", context)
    
def storePage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    category = request.GET.get('category') if request.GET.get('category') != None else ''
    Laptop = request.GET.get('Laptop') if request.GET.get('Laptop') != None else ''
    Camera = request.GET.get('Camera') if request.GET.get('Camera') != None else ''
    Smartphones = request.GET.get('Smartphones') if request.GET.get('Smartphones') != None else ''
    if request.user.is_authenticated:
        customer = request.user.customer
        order = Order.objects.filter(customer=customer, complete=False).first()
        orderItems = order.orderitem_set.all()
        orderItem_count = order.orderitem_set.count()

    items = Item.objects.filter(
        (Q(category__name__icontains=q)) |
        (Q(category__name__icontains=category) & Q(title__icontains=q)) |
        (Q(category__active=True) | Q(category__active=False))
    )
    categories = Category.objects.all()
    context = {
        'items': items,
        'order': order,
        'orderItems': orderItems,
        'orderItem_count': orderItem_count,
        'categories': categories,
    }
    return render(request, "base/store.html", context)

def changeCategory(request):
    if request.method == "POST":
        active = request.POST.get('active')
        name = request.POST.get('name')
        category = Category.objects.get(name=name)
        if category.active == False:
            category.active = bool(active)
        else:
            category.active = False
        category.save()
        return redirect('store')

def productPage(request, slug):
    if request.user.is_authenticated:
        customer = request.user.customer
        order = Order.objects.filter(customer=customer, complete=False).first()
        orderItems = order.orderitem_set.all()
        orderItem_count = order.orderitem_set.count()
        
    item = get_object_or_404(Item, slug=slug)
    items = Item.objects.filter(category=item.category).exclude(slug=item.slug)[:4]
    
    print("Rating: ", item.get_item_rating)
    context = {
        "items": items, 
        "item": item,
        'orderItem_count': orderItem_count,
        }
    return render(request, "base/product.html", context)

def reviewProduct(request, slug):
    item = get_object_or_404(Item, slug=slug)
    if request.method == "POST":
        reviewProduct = ReviewProduct.objects.create(
            item=item,
            name = request.POST.get('name'),
            email = request.POST.get('email'),
            description = request.POST.get('description'),
            rate_count = request.POST.get('rating'),
        )
        
        return redirect('product', slug=item.slug)
    
def newsLetter(request):
    if request.method == "POST":
        email = request.POST.get('email')
        newsletter = NewsLetter.objects.create(
            email=email
        )
        messages.info(request, 'Your email is safe with us. Thank you')
        return redirect('home')
        
    
def cartPage(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order = Order.objects.filter(customer=customer, complete=False).first()
        orderItems = order.orderitem_set.all()
        orderItem_count = order.orderitem_set.count()
    context = {
        'order': order,
        'orderItems': orderItems,
        'couponform': CouponForm(),
        'orderItem_count': orderItem_count,
    }
    return render(request, "base/cart.html", context)

@require_POST
def applyCoupon(request):
    now = timezone.now()
    couponform = CouponForm(request.POST or None)
    if couponform.is_valid():
        code = couponform.cleaned_data.get('code')
        try:
            coupon = Coupon.objects.get(code__iexact=code, valid_from__lte=now, valid_to__gte=now)
        except Coupon.DoesNotExist:
            messages.info(request, 'This coupon does not exist.')
            return redirect('cart')
        
        if request.user.is_authenticated:
            customer = request.user.customer
            try:
                order = Order.objects.filter(customer=customer, complete=False).first()
            except:
                messages.info(request, 'You must place an order before you can apple for coupon.')
                return redirect('cart')
            
            coupon_use, created = CouponUse.objects.get_or_create(customer=customer, coupon=coupon)
            
            if order.coupon is None and coupon_use.use_count <= 4:
                if coupon_use.use_count == 4: 
                    messages.info(request, 'You have reach the limited use of this coupon(thus 4 time).')
                else:
                    order.coupon = coupon
                    order.save()
                    coupon_use.use_count = (coupon_use.use_count + 1)
                    coupon_use.save()
                    messages.success(request, "You coupon application have been recieved enjoy the discount.")
            else:
                messages.error(request, "You can only use the coupon per perchase.")
            return redirect('cart')        
        else:
            messages.info(request, 'Only for regular customers with an account. Thank You')
        return redirect('cart')



def checkoutPage(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order = Order.objects.filter(customer=customer, complete=False).first()
        orderItems = order.orderitem_set.all()
        orderItem_count = order.orderitem_set.count()
    context = {
        'order': order,
        'orderItems': orderItems,
        'orderItem_count': orderItem_count,
    }
    return render(request, "base/checkout.html", context)
    
def updateCart(request):
    data = json.loads(request.body)
    itemId = data['itemId']
    action = data['action']
    print("ItemId: ", itemId)
    print("Action: ", action)

    customer = request.user.customer
    item = Item.objects.get(id=itemId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, item=item)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if action == 'delete':
        orderItem.delete()
    elif orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Updating cart item....", safe=False)