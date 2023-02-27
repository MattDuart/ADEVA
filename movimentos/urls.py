from django.urls import path
from . import views

app_name = 'movimentos'
 
urlpatterns = [
    path('', views.movimentos_caixa_list, name="movimentos_caixa_list")
]