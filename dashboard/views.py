from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404


from boxes.models import Box
from .forms import BoxForm


@staff_member_required
def box_admin(request):
    boxes = Box.objects.all().order_by('-shipping_date')
    return render(request, 'dashboard/box_manager.html', {'boxes':boxes, 'editing': False})


@staff_member_required
def add_box(request):
    if request.method == 'POST':
        form = BoxForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('box_admin')
    else:
        form = BoxForm()
    return render(request, 'dashboard/box.html', {'form':form})


@staff_member_required
def edit_box(request, box_id):
    box = get_object_or_404(Box, pk=box_id)
    if request.method == 'POST':
        form = BoxForm(request.POST, instance=box)
        if form.is_valid():
            form.save()
            return redirect('box_admin')
    else:
        form = BoxForm(instance=box)
    return render(request, 'dashboard/box.html', {'form': form, 'box_id': box_id, 'editing': True})


@staff_member_required
def delete_box(request, box_id):
    box = get_object_or_404(Box, pk=box_id)
    if request.method == 'POST':
        box.delete()
        return redirect('box_admin')
    return render(request, 'dashboard/delete_box.html', {'box_id': box_id})