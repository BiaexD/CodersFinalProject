from django.shortcuts import render, get_object_or_404, redirect  #funkcja render laczy dane z szablonem HTML oraz zwraca odpowiedz HTTP
                                                                  #funkcja get_object_or_404 - bezpiecznie pobiera objekt z bazy, zwroci 404 jezeli nie znajdzie
from .models import Equipment, Category
from django.views.decorators.http import require_POST



"""
equipment_list - przyjmuje argument request, ktory zawiera wszystkie dane o zadaniu HTTP(kto wyslal zapytanie i jaka metoda)

equipment - pobieramy wszystkie objekty Equipment z bazy, a 'objects.all() zwraca nam liste sprzetow.

zwracamy render - ktory robi trzy rzeczy na raz:
- szuka szablonu HTML o podanej sciezce
- do szablonu przekazuje slownik danych ({'eq...': eq...})
- tworzy odpowiedz HTTP i ja zwraca
"""
def equipment_list(request):
    equipment = Equipment.objects.all()
    return render(request, 'rentals/equipment_list.html', {'equipment': equipment})


"""
equipment_detail:
- przyjmuje argument request, ktory zawiera wszystkie dane o zadaniu HTTP(kto wyslal zapytanie i jaka metoda
- primary key - identyfikator sprzetu

equipment - django szuka sprzetu o danym "pk" w bazie:
- jezeli nie znajdzie wyswietli 404
- jezeli znajdzie przypisze do zmiennej equipment

return render:
- szuka szablonu HTML
- przekazujemy do niego zmienna equipment z calym objektem
- tworzy odpowiedz HTTP i ja zwraca
"""
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
    if str(equipment_id) in cart:
        cart[equipment_id] += 1

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
