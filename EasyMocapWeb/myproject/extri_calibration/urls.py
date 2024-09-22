from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_extri_yml_view, name='get_extri_yml'),
]