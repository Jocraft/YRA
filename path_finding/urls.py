from django.urls import path
from . import views

urlpatterns = [
    path('', views.path_finding_home, name='path_finding_home'),
    path('create_test_session/<int:student_id>/', views.create_test_session, name='create_test_session'),
    path('fill_test/<int:session_id>/', views.fill_test_view, name='fill_test'),
    path('generate_results/<int:session_id>/', views.generate_results_view, name='generate_results'),

    # Single-student upload
    path('upload_answers/<int:student_id>/', views.upload_answers_view, name='upload_answers'),

    # Bulk upload (no student selected)
    path('bulk_upload_answers/', views.upload_bulk_answers_view, name='upload_bulk_answers'),
    
    # NEW: delete all logs
    path('delete_logs/', views.delete_logs, name='delete_logs'),

]
