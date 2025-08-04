from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import LicensePlate, CreditCard
from django.contrib.auth.models import User
# Create your views here.
@login_required
def member_center_view(request):
    plates = LicensePlate.objects.filter(user=request.user)
    card = CreditCard.objects.filter(user=request.user).first()
    return render(request, 'member.html', {'plates': plates, 'card': card})


@login_required
def add_plate_view(request):
    if request.method == 'POST':
        plate = request.POST.get('plate')
        LicensePlate.objects.create(user=request.user, plate_number=plate)
        return redirect('member_center')
    return render(request, 'plate_form.html', {'action': '新增'})


@login_required
def edit_plate_view(request, plate_id):
    plate = get_object_or_404(LicensePlate, id=plate_id, user=request.user)
    if request.method == 'POST':
        plate.plate_number = request.POST.get('plate')
        plate.save()
        return redirect('member_center')
    return render(request, 'plate_form.html', {'plate': plate, 'action': '編輯'})


@login_required
def delete_plate_view(request, plate_id):
    plate = get_object_or_404(LicensePlate, id=plate_id, user=request.user)
    plate.delete()
    return redirect('member_center')


@login_required
def edit_card_view(request):
    card = CreditCard.objects.filter(user=request.user).first()
    if request.method == 'POST':
        number = request.POST.get('card')
        if card:
            card.card_number = number
            card.save()
        else:
            CreditCard.objects.create(user=request.user, card_number=number)
        return redirect('member_center')
    return render(request, 'card_form.html', {'card': card})