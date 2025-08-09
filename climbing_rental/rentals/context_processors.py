from .models import Cart, CartItem

def cart_info(request):
    count = 0
    rental_period = None
    has_active_cart = False

    if not request.user.is_authenticated:
        return {
            'cart_count': count,
            'rental_period': rental_period,
            'has_active_cart': has_active_cart,
        }

    cart = Cart.objects.filter(user=request.user, is_active=True).first()
    if cart:
        count = CartItem.objects.filter(cart=cart).count()
        rental_period = {
            'start_date': cart.start_date,
            'end_date': cart.end_date,
        }
        has_active_cart = True

    return {
        'cart_count': count,
        'rental_period': rental_period,
        'has_active_cart': has_active_cart,
    }