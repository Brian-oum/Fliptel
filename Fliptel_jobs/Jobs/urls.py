from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('view/<str:signed_job_id>/', views.view_job, name='view_job'),
]
