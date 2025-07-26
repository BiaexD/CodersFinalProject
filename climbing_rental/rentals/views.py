from django.shortcuts import render, get_object_or_404  #funkcja render laczy dane z szablonem HTML oraz zwraca odpowiedz HTTP
                                                        #funkcja get_object_or_404 - bezpiecznie pobiera objekt z bazy, zwroci 404 jezeli nie znajdzie
from .models import Equipment


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