# files/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    DocumentViewSet, CategoryViewSet,
    FilesDashboardView,
    export_csv_api, export_xlsx_api, import_template_api, import_xlsx_api,
)

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    # Router endpoints
    path('', include(router.urls)),

    # Extra API endpoints
    path('dashboard/', FilesDashboardView.as_view(), name='files-dashboard'),
    path('export/csv/', export_csv_api, name='files-export-csv'),
    path('export/xlsx/', export_xlsx_api, name='files-export-xlsx'),
    path('import/template/', import_template_api, name='files-import-template'),
    path("import/", import_xlsx_api, name="files-import-xlsx"),
]
