from rest_framework.routers import DefaultRouter
from .views import BankViewSet, BankAccountViewSet

router = DefaultRouter()
router.register(r"banks", BankViewSet)
router.register(r"bank-accounts", BankAccountViewSet)

urlpatterns = router.urls
