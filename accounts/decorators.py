from django.shortcuts import redirect

def user_type_required(required_type):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.user_type == required_type:
                return view_func(request, *args, **kwargs)
            return redirect('home')  # or 'login', or a custom "unauthorized" view
        return _wrapped_view
    return decorator
