from django.urls import path
from . import views
from .models import MovimentosCaixa
from django.contrib import admin
from . import views


app_name = 'movimentos'
 
urlpatterns = [
     path('', views.movimentos_caixa_list, name="movimentos_caixa_list"),
     path('fechamento/', views.fechamento_view, name='fechamento'),
     path('relatorio-fechamento/', views.rel_fechamento_view, name='relatorio_fechamento'),
     path('gerar-pdf/', views.gerar_pdf, name='gerar-pdf'),
     path('gerar-excel/', views.gerar_excel, name='gerar-excel')
     #path('test/', views.test_view, name='test'),
]

