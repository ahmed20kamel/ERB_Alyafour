from django.urls import path
from .views import (
        TenderCreateAPI, TenderListAPI, TenderDetailAPI,
        TenderAnswersAPI, TenderSubmitAPI,
        TenderApproveAPI, TenderRejectAPI,
        TenderOverridesAPI
    )

urlpatterns = [
        path("tenders", TenderCreateAPI.as_view()),                   # POST (create)
        path("tenders/list", TenderListAPI.as_view()),               # GET list
        path("tenders/<int:pk>", TenderDetailAPI.as_view()),         # GET detail
        path("tenders/<int:pk>/answers", TenderAnswersAPI.as_view()),# POST upsert answers + files
        path("tenders/<int:pk>/submit", TenderSubmitAPI.as_view()),  # POST submit
        path("tenders/<int:pk>/approve", TenderApproveAPI.as_view()),# POST approve
        path("tenders/<int:pk>/reject", TenderRejectAPI.as_view()),  # POST reject
        path("tenders/<int:pk>/overrides", TenderOverridesAPI.as_view()), # POST admin: overrides/custom fields + rebuild
    ]
