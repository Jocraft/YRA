from django.urls import path
from . import views

urlpatterns = [
    path('', views.analyze, name='analysis'),  # Default view for /analysis
]