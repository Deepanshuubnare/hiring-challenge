from django.urls import path
from app.api.viewsets.user import CreateUser
from app.api.router.user import urlpatterns as userAPI
from app.api.router.scam import urlpatterns as scamAPI
from app.api.router.search import urlpatterns as searchAPI
from app.api.router.contact import urlpatterns as contactAPI


api_urls = [
    *userAPI,
    *scamAPI,
    *searchAPI,
    *contactAPI,
]


from django.urls import path
from app.api.viewsets.user import CreateUser
from app.api.router.user import urlpatterns as userAPI
from app.api.router.scam import urlpatterns as scamAPI
from app.api.router.search import urlpatterns as searchAPI
from app.api.router.contact import urlpatterns as contactAPI
# --- Add this import ---
from app.api.router.interaction import urlpatterns as dashboardAPI


api_urls = [
    *userAPI,
    *scamAPI,
    *searchAPI,
    *contactAPI,
    *dashboardAPI, # <-- Add this line
]

