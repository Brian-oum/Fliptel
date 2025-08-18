from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('faculty/<str:faculty>/', views.job_list, name='jobs_by_faculty'),
]
