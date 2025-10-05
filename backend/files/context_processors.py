from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .models import Document


def notifications(request):
    today = timezone.localdate()
    soon_qs = Document.objects.filter(expires_on__lte=today + timedelta(days=7),
                                      expires_on__gte=today)
    items = soon_qs.order_by('expires_on')[:5]
    cleared = request.session.get('notifications_cleared_on') == str(today)
    count = 0 if cleared else soon_qs.count()
    return {'notification_count': count, 'notification_items': items}


def branding(request):
    return {
        'BRAND_NAME': settings.BRAND_NAME,
        'BRAND_TAGLINE': settings.BRAND_TAGLINE,
        'BRAND_OWNER': settings.BRAND_OWNER,
        'BRAND_LOGO_PATH': settings.BRAND_LOGO_PATH,
    }
