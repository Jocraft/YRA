from django.urls import path
from . import views

app_name = 'learning_methods'

urlpatterns = [
    path('', views.learning_methods, name='learning'),
    path('test/<int:student_id>/', views.fill_test, name='fill_test'),
    path('results/<int:student_id>/', views.results, name='results'),
    # New bulk upload route:
    path('bulk_upload/', views.bulk_upload, name='bulk_upload'),
]

