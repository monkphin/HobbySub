from django.shortcuts import render
from boxes.models import Box
from datetime import date

# Create your views here.

def home(request):

    box = Box.objects.filter(is_archived=False, shipping_date__lte=date.today()).order_by('-shipping_date').first()
    box_contents = box.contents.all() if box else []

    return render(request, 'home/index.html', {
                  'box': box,
                  'box_contents': box_contents,
                  })
