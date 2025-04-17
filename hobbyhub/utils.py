from django.contrib import messages


def alert(request, level, msg):
    {
        "success": messages.success,
        "info": messages.info,
        "warning": messages.warning,
        "error": messages.error
    }.get(level, messages.info)(request, msg)