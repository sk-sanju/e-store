from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Order
from django.contrib import messages
import stripe
from django.conf import settings
from django.db.models import F
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

def payment_process(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        user = request.user
        
        if payment_method == 'Wallet':
            if user.balance >= order.total_amount:
                user.balance = F('balance') - order.total_amount
                user.save()
                user.refresh_from_db()
                
                order.paid = True
                order.status = 'Processing'
                order.payment_method = 'Wallet'
                order.save()
                
                messages.success(request, f"Payment successful using Wallet! Remaining balance: ${user.balance}")
                return redirect('payments:done')
            else:
                messages.error(request, "Insufficient wallet balance.")
                return redirect('payments:process', order_id=order.id)
        
        # Real-life Stripe Integration
        success_url = request.build_absolute_uri(reverse('payments:done')) + f'?order_id={order.id}'
        cancel_url = request.build_absolute_uri(reverse('payments:canceled'))
        
        # Stripe Checkout Session
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        
        # Add order items to Stripe
        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.price * 100),
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                    },
                },
                'quantity': item.quantity,
            })
            
        session = stripe.checkout.Session.create(**session_data)
        
        # Set payment method temporarily and redirect to Stripe
        order.payment_method = payment_method
        order.save()
        
        return redirect(session.url, code=303)
        
    return render(request, 'payments/process.html', {'order': order, 'stripe_public_key': settings.STRIPE_PUBLIC_KEY})

def payment_done(request):
    order_id = request.GET.get('order_id')
    if order_id:
        order = get_object_or_404(Order, id=order_id)
        order.paid = True
        order.status = 'Processing'
        order.save()
        messages.success(request, f"Order #{order.id} payment confirmed!")
    return render(request, 'payments/done.html')

def payment_canceled(request):
    return render(request, 'payments/canceled.html')
