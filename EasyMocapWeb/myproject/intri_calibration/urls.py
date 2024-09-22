from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_intri_yml, name='get_intri_yml'),
    
]