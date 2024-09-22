from django.urls import path
from . import views

urlpatterns = [
    path('', views.fit_view, name='fit'),
    
]