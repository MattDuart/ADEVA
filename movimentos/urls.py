from django.urls import path
from . import views

app_name = 'movimentos'
 
urlpatterns = [
     path('', views.movimentos_caixa_list, name="movimentos_caixa_list"),
     path('fechamento/', views.fechamento_view, name='fechamento'),
     #path('test/', views.test_view, name='test'),
]