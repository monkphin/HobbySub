"""
Views for displaying archived subscription boxes and individual box details.
"""

import logging

# Django/External Imports
from django.shortcuts import get_object_or_404, render

# Local Imports
from boxes.models import Box

logger = logging.getLogger(__name__)


def past_boxes(request):
    """
    View to display a list of all archived boxes, ordered by most recent
    shipping date.
    """
    past_boxes = (
        Box.objects
        .filter(is_archived=True)
        .order_by('-shipping_date')
    )
    logger.info(
        f"{request.user} viewed archived boxes page — "
        f"{past_boxes.count()} boxes found"
    )
    return render(request, 'boxes/past_boxes.html', {'past_boxes': past_boxes})


def box_detail(request, slug):
    """
    View to display details of a single box based on its slug.
    """
    box = get_object_or_404(Box, slug=slug)
    logger.info(
        f"{request.user} viewed box detail page for: {box.name} (slug: {slug})"
    )
    return render(request, 'boxes/box_detail.html', {'box': box})
