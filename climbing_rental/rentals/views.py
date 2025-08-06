from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .models import Equipment, Category, Rental, RentalItem, Cart, CartItem
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Sum


def get_active_cart(user):
    return Cart.objects.filter(user=user, is_active=True).first()



def equipment_list(request):
    equipment = Equipment.objects.all()
    return render(request, 'rentals/equipment_list.html', {'equipment': equipment})



def equipment_detail(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    return render(request, 'rentals/equipment_detail.html', {'equipment': equipment})



def home(request):
    categories = Category.objects.all()
    return render(request, 'home.html', {'categories': categories})



def category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    try:
        cart = Cart.objects.get(user=request.user, is_active=True)
    except Cart.DoesNotExist:
        return redirect('select_dates')

    start_date = cart.start_date
    end_date = cart.end_date

    available_equipment = []
    for equipment in Equipment.objects.filter(category=category):
        already_reserved = (
            CartItem.objects.filter(
                equipment=equipment,
                cart__start_date__lte=end_date,
                cart__end_date__gte=start_date,
                cart__is_active=True
            )
            .aggregate(total=Sum('quantity'))['total'] or 0
        )

        left = equipment.quantity - already_reserved
        if left > 0:
            available_equipment.append({
                'equipment': equipment,
                'available': left,
            })
    context = {
        'category': category,
        'equipment_list': available_equipment,
        'cart': cart,
    }

    return render(request, 'rentals/category_detail.html', context)


@login_required
def cart_view(request):
    cart = get_active_cart(request.user)
    items = []
    total_price_per_day = 0
    total_deposit = 0

    if cart:
        for cart_item in cart.cartitem_set.select_related('equipment').all():
            price = cart_item.equipment.price_per_day * cart_item.quantity
            deposit = cart_item.equipment.deposit * cart_item.quantity
            total_price_per_day += price
            total_deposit += deposit
            items.append({
                'equipment': cart_item.equipment,
                'quantity': cart_item.quantity,
                'price': price,
                'deposit': deposit,
            })

    context = {
        'items': items,
        'total_price_per_day': total_price_per_day,
        'total_deposit': total_deposit,
    }
    return render(request, 'cart.html', context)


@login_required
def add_to_cart(request, equipment_id):
    cart = get_active_cart(request.user)
    if not cart:
        messages.error(request, "Najpierw wybierz daty wypozyczenia sprzetu!")
        return redirect('select_dates')

    equipment = get_object_or_404(Equipment, pk=equipment_id)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        equipment=equipment,
        defaults={'quantity': 0}
    )

    current_quantity = cart_item.quantity
    if current_quantity < equipment.quantity:
        cart_item.quantity += 1
        cart_item.save()
        # messages.success(request, f"Dodano {equipment.name} do koszyka")
    else:
        messages.error(request, f"Nie mozna dodac wiecej {equipment.name} w wybranym terminie")

    return redirect(request.META.get('HTTP_REFERER', 'home'))



def remove_from_cart(request, equipment_id):
    cart = get_active_cart(request.user)
    if not cart:
        messages.error(request, "Najpierw wybierz daty wypozyczenia sprzetu!")
        return redirect('select_dates')

    cart_item = CartItem.objects.filter(cart=cart, equipment_id=equipment_id).first()
    if cart_item:
        cart_item.delete()
        messages.success(request, f"Usunieto {cart_item.equipment.name} z koszyka.")
    return redirect('cart')



@login_required
@require_POST
def increase_quantity(request, equipment_id):
    cart = get_active_cart(request.user)
    if not cart:
        messages.error(request, "Najpierw wybierz daty wypozyczenia sprzetu!")
        return redirect('select_dates')

    cart_item = get_object_or_404(CartItem, cart=cart, equipment_id=equipment_id)

    if cart_item.quantity < cart_item.equipment.quantity:
        cart_item.quantity += 1
        cart_item.save()
    else:
        messages.error(request, f"Nie mamy więcej {cart_item.equipment.name}...")

    return redirect('cart')


@login_required
@require_POST
def decrease_quantity(request, equipment_id):
    cart = get_active_cart(request.user)
    if not cart:
        messages.error(request, "Najpierw wybierz daty wypozyczenia sprzetu!")
        return redirect('select_dates')

    cart_item = get_object_or_404(CartItem, cart=cart, equipment_id=equipment_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
        messages.success(request, f"Usunieto {cart_item.equipment.name} z koszyka.")

    return redirect('cart')



@login_required
def order_summary(request):
    try:
        cart = get_active_cart(request.user)
    except Cart.DoesNotExist:
        messages.error(request, "Najpierw wybierz daty wypozyczenia sprzetu!")
        return redirect('select_dates')

    items = CartItem.objects.filter(cart=cart)

    if request.method == 'POST':
        with transaction.atomic():
            for item in items:
                equipment = item.equipment
                reserved = (
                    CartItem.objects.filter(
                        equipment=equipment,
                        cart__is_active=True,
                        cart__start_date__lte=cart.end_date,
                        cart__end_date__gt=cart.start_date,
                    )
                    .exclude(cart=cart)
                    .aggregate(total=Sum('quantity'))['total'] or 0
                )
                available = equipment.quantity - reserved
                if item.quantity > available:
                    messages.error(request, f"Nie mamy wiecej {equipment.name}...")
                    return redirect('cart')

            for item in items:
                equipment = item.equipment
                equipment.quantity -= item.quantity
                equipment.save()

            cart.is_active = False
            cart.save()
            items.delete()

            messages.success(request, "Zamowienie zostalo wyslane do realizacji!")
            return redirect('order_complete')

    return render(request, 'rentals/order_summary.html', {'cart': cart, 'items': items})



def order_complete(request):
    return render(request, 'rentals/order_complete.html')



def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})



@login_required
def user_rentals(request):
    rentals = Rental.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'rentals/user_rentals.html', {'rentals': rentals})



@login_required
def user_panel(request):
    rentals = Rental.objects.filter(user=request.user)
    return render(request, 'rentals/user_panel.html', {'rentals': rentals})



@login_required
def select_dates(request):
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if not start_date or not end_date:
            messages.error(request, "Musisz wybrac obie daty!")
            return redirect('select_dates')
        if start_date > end_date:
            messages.error(request, "Data konca musi byc pozniej niz poczatek!")
            return redirect('select_dates')

        Cart.objects.filter(user=request.user, is_active=True).update(is_active=False)

        cart = Cart.objects.create(
            user=request.user,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        return redirect('home')

    return render(request, 'rentals/select_dates.html')



@login_required
def finish_rental(request, rental_id):
    rental = get_object_or_404(Rental, pk=rental_id, user=request.user)
    if rental.status != 'finished':
        rental.status = 'finished'
        rental.save()
        for item in rental.items.all():
            equipmnet = item.equipment
            equipmnet.quantity += item.quantity
            equipmnet.save()
        messages.success(request, "Wypozyczenie zostalo zakonczone, ilosc sprzetu w magazynie zostala uzupelniona")
    else:
        messages.info(request, "To wypozyczenie zostalo juz zakonczone")

    return redirect('user_panel')