from django.shortcuts import render


def custom_staff_required(view_func):
    """
    Custom staff member required decorator.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
