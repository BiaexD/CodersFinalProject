from django.shortcuts import render, get_object_or_404, redirect
from .models import Equipment, Category, Rental, RentalItem
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required



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
    equipment_list = Equipment.objects.filter(category=category)
    return render(request, 'rentals/category_detail.html', {
        'category': category,
        'equipment_list': equipment_list,
    })



def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total_price_per_day = 0
    total_deposit = 0

    for equipment_id, quantity in cart.items():
        try:
            equipment = Equipment.objects.get(pk=equipment_id)
            price = equipment.price_per_day * quantity
            deposit = equipment.deposit * quantity
            total_price_per_day += price
            total_deposit += deposit
            items.append({
                'equipment': equipment,
                'quantity': quantity,
                'price': price,
                'deposit': deposit,
            })
        except Equipment.DoesNotExist:
            continue

    context = {
        'items': items,
        'total_price_per_day': total_price_per_day,
        'total_deposit': total_deposit,
    }
    return render(request, 'cart.html', context)



def add_to_cart(request, equipment_id):
    # equipment = get_object_or_404(Equipment, pk=equipment_id)
    cart = request.session.get('cart', {})
    if str(equipment_id) in cart:
        cart[str(equipment_id)] += 1
    else:
        cart[str(equipment_id)] = 1

    request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER', 'home'))



def remove_from_cart(request, equipment_id):
    cart = request.session.get('cart', {})
    if str(equipment_id) in cart:
        del cart[str(equipment_id)]

    request.session['cart'] = cart
    return redirect('cart')



@require_POST
def increase_quantity(request, equipment_id):
    cart = request.session.get('cart', {})
    equipment_id = str(equipment_id)
    equipment = get_object_or_404(Equipment, pk=equipment_id)
    current_quantity = cart.get(str(equipment_id), 0)

    if current_quantity < equipment.quantity:
        cart[equipment.pk] = current_quantity + 1
    else:
        messages.error(request, f"Nie mamy więcej {equipment.name}...")
    # if str(equipment_id) in cart:
    #     cart[equipment_id] += 1

    request.session['cart'] = cart
    return redirect('cart')



@require_POST
def decrease_quantity(request, equipment_id):
    cart = request.session.get('cart', {})
    equipment_id = str(equipment_id)
    if str(equipment_id) in cart:
        if cart[equipment_id] > 1:
            cart[equipment_id] -= 1
        else:
            del cart[equipment_id]

    request.session['cart'] = cart
    return redirect('cart')



@require_http_methods(['GET', 'POST'])
def order_summary(request):
    cart = request.session.get('cart', {})
    items = []

    if request.method == "POST":
        for equipment_id, quantity in cart.items():
            equipment = Equipment.objects.get(pk=equipment_id)

            if equipment.quantity >= quantity:
                equipment.quantity -= quantity
                equipment.save()
            else:
                messages.error(request, f"Nie mamy wystarczajacej liczby: {equipment.name} na magazynie")
                return redirect('cart')
        request.session['cart'] = {}

        messages.success(request, "Zamowienie przeslano do realizacji")
        return redirect('home')

    else:
        for equipment_id, quantity in cart.items():
            equipment = Equipment.objects.get(pk=equipment_id)
            items.append({
                'equipment': equipment,
                'quantity': quantity,
            })

        return render(request, 'rentals/order_summary.html', {'items': items})