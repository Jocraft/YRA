# filepath: /path/to/your/project/path_finding/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.path_finding_home, name='path_finding_home'),
    path('create_test_session/<int:student_id>/', views.create_test_session, name='create_test_session'),
    path('fill_test/<int:session_id>/', views.fill_test_view, name='fill_test'),
    path('generate_results/<int:session_id>/', views.generate_results_view, name='generate_results'),
]