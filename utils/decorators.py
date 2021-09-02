from rest_framework.response import Response
from rest_framework import status
from functools import wraps

def required_all_params(params_src='query_params', params=tuple()):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(instance, request, *arg, **kwargs):
            data = getattr(request, params_src)
            missing_params = [
                param
                for param in params
                if param not in data
            ]
            if missing_params:
                return Response({
                    'success': False,
                    'message': f'missing params: {", ".join(missing_params)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            return view_func(instance, request, *arg, **kwargs)
        return _wrapped_view
    return decorator

def required_any_params(params_src='query_params', params=tuple()):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(instance, request, *arg, **kwargs):
            data = getattr(request, params_src)
            matching_params = [
                param
                for param in params
                if param in data
            ]
            if not matching_params:
                return Response({
                    'success': False,
                    'message': f'All of required params are missing: {", ".join(params)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            return view_func(instance, request, *arg, **kwargs)
        return _wrapped_view
    return decorator
