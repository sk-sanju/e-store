from .models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            return {'cart_count': 0}
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    
    return {'cart_count': cart.item_count}
