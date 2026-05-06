from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from products.models import Product
from cart.models import Cart
from accounts.models import Address
from django.contrib import messages

@login_required
def order_create(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if cart.items.count() == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('products:product_list')
    
    addresses = request.user.addresses.all()
    if not addresses:
        messages.info(request, "Please add a shipping address first.")
        return redirect('accounts:add_address')

    # Fetch relatable products (Upselling)
    cart_categories = cart.items.values_list('product__category', flat=True)
    cart_product_ids = cart.items.values_list('product_id', flat=True)
    relatable_products = Product.objects.filter(
        category__in=cart_categories, 
        available=True
    ).exclude(id__in=cart_product_ids).distinct()[:3]

    # Fallback to general products if no relatable ones found
    if not relatable_products:
        relatable_products = Product.objects.filter(available=True).exclude(id__in=cart_product_ids).order_by('?')[:3]

    if request.method == 'POST':
        address_id = request.POST.get('address')
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        order = Order.objects.create(
            user=request.user,
            shipping_address=address,
            total_amount=cart.total_price
        )
        
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.discount_price if item.product.discount_price else item.product.price,
                quantity=item.quantity
            )
            # Update Stock
            item.product.stock -= item.quantity
            item.product.save()
            
        # Clear Cart
        cart.items.all().delete()
        
        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('payments:process', order_id=order.id)

    return render(request, 'orders/create.html', {
        'cart': cart,
        'addresses': addresses,
        'relatable_products': relatable_products
    })

@login_required
def order_history(request):
    orders = request.user.orders.all()
    return render(request, 'orders/history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})
