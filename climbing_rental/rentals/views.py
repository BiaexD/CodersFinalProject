from decimal import Decimal
from urllib import request

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .models import Equipment, Category, Rental, RentalItem, Cart, CartItem, UserProfile
from .forms import UserEditForm, UserProfileForm
from datetime import date
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
    categories = Category.objects.all()

    cart = get_active_cart(request.user)
    if not cart:
        messages.error(request, "Najpierw wybierz daty wypozyczenia sprzetu!")
        return redirect('select_dates')

    cart_count = cart.cartitem_set.count()

    available_equipment = []
    for equipment in Equipment.objects.filter(category=category):
        free = available_on_dates(equipment, request.user)
        if free > 0:
            available_equipment.append({
                'equipment': equipment,
                'available': free,
            })
    context = {
        'category': category,
        'categories': categories,
        'equipment_list': available_equipment,
        'cart': cart,
        'cart_count': cart_count,
        'active_cart': category,
    }

    return render(request, 'rentals/category_detail.html', context)



@login_required
def cart_view(request):
    cart = get_active_cart(request.user)
    items = []
    total_price_per_day = Decimal('0.00')
    total_deposit = Decimal('0.00')

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
@require_POST
def add_to_cart(request, equipment_id):
    cart = get_active_cart(request.user)
    if not cart:
        messages.error(request, "Najpierw wybierz daty wypozyczenia sprzetu!")
        return redirect('select_dates')

    equipment = get_object_or_404(Equipment, pk=equipment_id)
    free_to_add = available_on_dates(equipment, request.user)
    if free_to_add < 1:
        messages.error(request, f"Nie mozna dodac wiecej {equipment.name} w wybranym terminie")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        equipment=equipment,
        defaults={'quantity': 0}
    )

    cart_item.quantity += 1
    cart_item.save()

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
@require_POST
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

    free_to_add = available_on_dates(cart_item.equipment, request.user)
    if free_to_add < 1:
        messages.error(request, f"Nie mamy więcej {cart_item.equipment.name}...")
        return redirect('cart')

    cart_item.quantity += 1
    cart_item.save()

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
def order_categories(request):
    cart = get_active_cart(request.user)
    if not cart:
        messages.error(request, "Najpierw wybierz daty wypozyczenia sprzetu!")
        return redirect('select_dates')

    categories = Category.objects.all().order_by('name')

    return render(request, 'rentals/order_categories.html', {'categories': categories})



def available_on_dates(equipment, user):
    cart = get_active_cart(user)
    if not cart:
        return 0

    start = cart.start_date
    end = cart.end_date

    reserved_from_rentals = (
        RentalItem.objects.filter(
            equipment=equipment,
            rental__status__in=['pending', 'active'],
            rental__start_date__lte=end,
            rental__end_date__gte=start,
        ).aggregate(total=Sum('quantity'))['total'] or 0
    )

    in_my_cart_now = (
        CartItem.objects.filter(
            cart=cart,
            equipment=equipment,
        ).aggregate(total=Sum('quantity'))['total'] or 0
    )

    free = equipment.total_quantity - reserved_from_rentals - in_my_cart_now
    return max(0, free)



@login_required
def order_summary(request):
    try:
        cart = get_active_cart(request.user)
    except Cart.DoesNotExist:
        messages.error(request, "Najpierw wybierz daty wypozyczenia sprzetu!")
        return redirect('select_dates')

    items = CartItem.objects.filter(cart=cart)

    total_price_per_day = sum(item.equipment.price_per_day * item.quantity for item in items)
    total_deposit = sum(item.equipment.deposit * item.quantity for item in items)
    rental_days = (cart.end_date - cart.start_date).days
    total_rental_price = total_price_per_day * rental_days
    total_cost = total_rental_price + total_deposit

    if request.method == 'POST':
        with transaction.atomic():
            for item in items:
                equipment = item.equipment
                reserved_from_rentals = (
                    RentalItem.objects.filter(
                        equipment=equipment,
                        rental__status__in=['pending', 'active'],
                        rental__start_date__lte=cart.end_date,
                        rental__end_date__gt=cart.start_date,
                    ).aggregate(total=Sum('quantity'))['total'] or 0
                )

                in_other_carts = (
                    CartItem.objects.filter(
                        equipment=equipment,
                        cart__is_active=True,
                        cart__start_date__lte=cart.end_date,
                        cart__end_date__gte=cart.start_date,
                    ).exclude(cart=cart)
                     .aggregate(total=Sum('quantity'))['total'] or 0
                )

                available_now = equipment.total_quantity - reserved_from_rentals - in_other_carts
                if item.quantity > available_now:
                    messages.error(request, f"Nie mamy wiecej {equipment.name}...")
                    return redirect('cart')

            rental = Rental.objects.create(
                user=request.user,
                start_date=cart.start_date,
                end_date=cart.end_date,
                status='pending' or 'active',
            )

            for item in items:
                RentalItem.objects.create(
                    rental=rental,
                    equipment=item.equipment,
                    quantity=item.quantity,
                )

            for item in items:
                equipment = item.equipment
                equipment.quantity -= item.quantity
                equipment.save()

            cart.is_active = False
            cart.save()
            items.delete()

            messages.success(request, "Zamowienie zostalo wyslane do realizacji!")
            return redirect('order_complete')

    return render(request, 'rentals/order_summary.html', {
        'cart': cart,
        'items': items,
        'total_price_per_day': total_price_per_day,
        'total_rental_price': total_rental_price,
        'total_deposit': total_deposit,
        'rental_days': rental_days,
        'total_cost': total_cost,
    })


@login_required
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
    today = date.today()
    is_edit_mode = request.GET.get('edit') == '1'

    if request.method == 'GET' and not is_edit_mode:
        if Cart.objects.filter(user=request.user, is_active=True).exists():
            return redirect('order_categories')

    if request.method == "POST":
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        def render_with_error(msg):
            messages.error(request, msg)
            return render(
                request,
                'rentals/select_dates.html', {
                    'today': today.isoformat(),
                    'start_value': start_date_str or '',
                    'end_value': end_date_str or '',
                }
            )

        if not start_date_str or not end_date_str:
            return render_with_error("Musisz wybrac obie daty!")
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)

        if start_date > end_date:
            return render_with_error("Data konca musi byc pozniej niz poczatek!")
        if start_date < today or end_date < today:
            return render_with_error("Wybrales date z przeszlosci")

        Cart.objects.filter(user=request.user, is_active=True).update(is_active=False)
        Cart.objects.create(
            user=request.user,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        return redirect('order_categories')

    return render(request, 'rentals/select_dates.html', {
        'today': today.isoformat(),
    })



@login_required
def finish_rental(request, rental_id):
    rental = get_object_or_404(Rental, pk=rental_id, user=request.user)
    if rental.status != 'finished':
        rental.status = 'finished'
        rental.save()
        messages.success(request, "Wypozyczenie zostalo zakonczone, ilosc sprzetu w magazynie zostala uzupelniona")
    else:
        messages.info(request, "To wypozyczenie zostalo juz zakonczone")

    return redirect('user_rentals')



@login_required
def rental_detail(request, rental_id):
    rental = get_object_or_404(Rental, pk=rental_id, user=request.user)
    items = rental.items.select_related("equipment").all()

    total_price_per_day = Decimal("0.00")
    total_deposit = Decimal("0.00")

    for item in items:
        total_price_per_day += item.equipment.price_per_day * item.quantity
        total_deposit += item.equipment.deposit * item.quantity

    total_price_total = total_price_per_day * rental.get_days_count()

    context = {
        "rental": rental,
        "items": items,
        "days_count": rental.get_days_count(),
        "total_price_per_day": total_price_per_day,
        "total_price_total": total_price_total,
        "total_deposit": total_deposit,
    }
    return render(request, 'rentals/rental_detail.html', context)



@login_required
def user_data(request):
    user_profile, create = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'rentals/user_data.html', {
        'user': request.user,
        'profile': user_profile,
    })



@login_required
def user_edit_data(request):
    user_profile, create = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_data')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)

    return render(request, 'rentals/user_edit_data.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })
