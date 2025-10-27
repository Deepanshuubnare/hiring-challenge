from django.urls import path
from app.api.viewsets.interaction import (
    RecentInteractionsView,
    TopContactsView,
    SpamReportStatsView
)

urlpatterns = [
    path('dashboard/recent', RecentInteractionsView.as_view(), name='dashboard-recent'),
    path('dashboard/top-contacts', TopContactsView.as_view(), name='dashboard-top-contacts'),
    path('dashboard/spam-stats', SpamReportStatsView.as_view(), name='dashboard-spam-stats'),
]
