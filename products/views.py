from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Wishlist, Review
from .forms import ReviewForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    # Filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
        
    # Sorting
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created')
    
    popular_products = Product.objects.filter(available=True).order_by('-created')[:4]
    
    return render(request, 'products/list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'popular_products': popular_products,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    reviews = product.reviews.all()
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, "Please login to write a review.")
            return redirect('accounts:login')
            
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check if user already reviewed this product
            if Review.objects.filter(product=product, user=request.user).exists():
                messages.warning(request, "You have already reviewed this product.")
            else:
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, "Your review has been added.")
            return redirect(product.get_absolute_url())
    else:
        form = ReviewForm()
        
    return render(request, 'products/detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form
    })

def product_search(request):
    query = request.GET.get('q')
    products = Product.objects.all()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'products/list.html', {
        'products': products,
        'query': query
    })

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'products/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f"{product.name} added to your wishlist.")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")
    return redirect('products:wishlist')

@login_required
def remove_from_wishlist(request, wishlist_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    wishlist_item.delete()
    messages.success(request, "Item removed from wishlist.")
    return redirect('products:wishlist')

def about(request):
    return render(request, 'products/about.html')

def contact(request):
    if request.method == 'POST':
        messages.success(request, "Your message has been sent successfully! We'll get back to you soon.")
        return redirect('products:contact')
    return render(request, 'products/contact.html')

def privacy_policy(request):
    return render(request, 'products/privacy.html')

def return_policy(request):
    return render(request, 'products/returns.html')
