from django.shortcuts import render, get_object_or_404
from boxes.models import Box

def past_boxes(request):
    past_boxes = Box.objects.filter(is_archived=True).order_by('-shipping_date')
    return render(request, 'home/past_boxes.html', {'past_boxes': past_boxes})


def box_detail(request, slug):
    box = get_object_or_404(Box, slug=slug)
    return render(request, 'home/box_detail.html', {'box':box})