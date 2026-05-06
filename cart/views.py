from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Cart, CartItem
from django.contrib import messages

def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    return cart

@require_POST
def cart_add(request, product_id):
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    
    if cart_item.quantity > product.stock:
        messages.error(request, f"Sorry, only {product.stock} units available.")
    else:
        cart_item.save()
        messages.success(request, f"{product.name} added to cart.")
        
    # Redirect back to the page the user came from (e.g. checkout or cart)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = get_cart(request)
    
    # Fetch relatable products (Recommendations)
    cart_categories = cart.items.values_list('product__category', flat=True)
    cart_product_ids = cart.items.values_list('product_id', flat=True)
    relatable_products = Product.objects.filter(
        category__in=cart_categories, 
        available=True
    ).exclude(id__in=cart_product_ids).distinct()[:3]

    if not relatable_products:
        relatable_products = Product.objects.filter(available=True).exclude(id__in=cart_product_ids).order_by('?')[:3]

    return render(request, 'cart/detail.html', {
        'cart': cart,
        'relatable_products': relatable_products
    })

def cart_remove(request, item_id):
    cart = get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart:cart_detail')

@require_POST
def cart_update(request, item_id):
    cart = get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > item.product.stock:
        messages.error(request, f"Only {item.product.stock} units available.")
    elif quantity > 0:
        item.quantity = quantity
        item.save()
        messages.success(request, "Cart updated.")
    else:
        item.delete()
        
    return redirect('cart:cart_detail')
