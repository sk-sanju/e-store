from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, AddressForm, UserSettingsForm
from .models import Address
from django.contrib import messages
from decimal import Decimal

# ... (other views)

@login_required
def setting(request):
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Account settings updated.")
            return redirect('accounts:profile')
    else:
        form = UserSettingsForm(instance=request.user)
    return render(request, 'accounts/settings.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('products:product_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('products:product_list')

@login_required
def profile(request):
    addresses = request.user.addresses.all()
    return render(request, 'accounts/profile.html', {'addresses': addresses})

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully.")
            return redirect('accounts:profile')
    else:
        form = AddressForm()
    return render(request, 'accounts/add_address.html', {'form': form})

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('accounts:profile')
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/add_address.html', {'form': form, 'edit': True})

import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def add_balance(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if not amount:
            messages.error(request, "Please enter an amount.")
            return render(request, 'accounts/add_balance.html')
            
        try:
            amount_decimal = Decimal(amount)
            if amount_decimal <= 0:
                raise ValueError
        except (ValueError, Decimal.InvalidOperation):
            messages.error(request, "Please enter a valid positive amount.")
            return render(request, 'accounts/add_balance.html')

        # Real-life Stripe Integration for Wallet
        success_url = request.build_absolute_uri(reverse('accounts:wallet_success')) + f'?amount={amount}'
        cancel_url = request.build_absolute_uri(reverse('accounts:profile'))
        
        session = stripe.checkout.Session.create(
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            line_items=[{
                'price_data': {
                    'unit_amount': int(amount_decimal * 100),
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Wallet Top-up',
                        'description': f'Adding ${amount} to your internal wallet balance.',
                    },
                },
                'quantity': 1,
            }]
        )
        return redirect(session.url, code=303)
        
    return render(request, 'accounts/add_balance.html')

@login_required
def wallet_success(request):
    amount = request.GET.get('amount')
    if amount:
        try:
            amount_decimal = Decimal(amount)
            user = request.user
            user.balance += amount_decimal
            user.save()
            messages.success(request, f"Successfully added ${amount} to your wallet!")
        except:
            messages.error(request, "There was an error updating your balance.")
    return redirect('accounts:profile')
