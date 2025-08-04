from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ParkingLot
from django.contrib import messages
from UserInterface.models import Reservation
# Create your views here.


@login_required
def owner_dashboard(request):
    lots = ParkingLot.objects.filter(owner=request.user)
    return render(request, 'owner_dashboard.html', {'lots': lots})


@login_required
def add_parking(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        ParkingLot.objects.create(
            owner=request.user,
            name=request.POST['name'],
            floor=request.POST['floor'],
            total_slots=request.POST['total'],
            available_slots=request.POST['available'],
            location=request.POST['location'],
            image=image
        )
        return redirect('owner_dashboard')
    return render(request, 'parking_form.html', {'action': '新增'})


@login_required
def edit_parking(request, pk):
    lot = get_object_or_404(ParkingLot, pk=pk, owner=request.user)
    image = request.FILES.get('image')
    if request.method == 'POST':
        lot.image = image
        lot.name = request.POST['name']
        lot.floor = request.POST['floor']
        lot.total_slots = request.POST['total']
        lot.available_slots = request.POST['available']
        lot.location = request.POST['location']
        lot.save()
        return redirect('owner_dashboard')
    return render(request, 'parking_form.html', {'action': '編輯', 'lot': lot})


@login_required
def delete_parking(request, pk):
    lot = get_object_or_404(ParkingLot, pk=pk, owner=request.user)
    lot.delete()
    return redirect('owner_dashboard')


@login_required
def manage_parking(request, pk):
    lot = get_object_or_404(ParkingLot, pk=pk, owner=request.user)
    return render(request, 'manage_parking.html', {'lot': lot})