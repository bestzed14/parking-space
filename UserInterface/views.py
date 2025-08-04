from django.shortcuts import render
from .models import ParkingLot , Reservation
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def dashboard_view(request):
    sort = request.GET.get('sort')
    parking_lots = ParkingLot.objects.all()

    if sort == 'distance':
        # ➤ 實作距離排序（可搭配 GeoDjango 或假資料）
        pass
    elif sort == 'price':
        parking_lots = parking_lots.order_by('price_per_hour')
    elif sort == 'vacancy':
        parking_lots = parking_lots.order_by('-available_slots')

    return render(request, 'dashboard.html', {
        'parking_lots': parking_lots
    })


@login_required
def reserve_parking_view(request, parking_id):
    lot = ParkingLot.objects.get(id=parking_id)
    if lot.available_slots > 0:
        Reservation.objects.create(user=request.user, parking_lot=lot)
        lot.available_slots -= 1
        lot.save()
        return render(request, 'message.html', {'msg': f'{lot.name} 預約成功！'})
    return render(request, 'message.html', {'msg': f'{lot.name} 沒有可預約的車位。'})
