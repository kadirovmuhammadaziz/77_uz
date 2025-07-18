from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .models import Setting


class MaintenanceModeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            return None

        try:
            settings = Setting.get_settings()
            if settings.maintenance_mode:
                return JsonResponse({
                    'error': 'Site is under maintenance',
                    'message': 'Please try again later'
                }, status=503)
        except:
            pass

        return None