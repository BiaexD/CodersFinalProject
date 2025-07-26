from django.shortcuts import render #funkcja render laczy dane z szablonem HTML oraz zwraca odpowiedz HTTP
from .models import Equipment


"""
equipment_list przyjmuje argument request, ktory zawiera wszystkie dane o zadaniu HTTP(kto wyslal zapytanie i jaka metoda)

equipment - pobieramy wszystkie objekty Equipment z bazy, a 'objects.all() zwraca nam liste sprzetow.

zwracamy render - ktory robi trzy rzeczy na raz:
- szuka szablonu HTML o podanej sciezce
- do szablonu przekazuje slownik danych ({'eq...': eq...})
- tworzy odpowiedz HTTP i ja zwraca
"""
def equipment_list(request):
    equipment = Equipment.objects.all()
    return render(request, 'rentals/equipment_list.html', {'equipment': equipment})


