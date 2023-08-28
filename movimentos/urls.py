from django.urls import path
from . import views
from .models import MovimentosCaixa
from django.contrib import admin
from .views import ReciboPDF



app_name = 'movimentos'
 
urlpatterns = [
     path('', views.movimentos_caixa_list, name="movimentos_caixa_list"),
     path('fechamento/', views.fechamento_view, name='fechamento'),
     path('download/', views.view_download, name='download'),
     path('relatorio-fechamento/', views.rel_fechamento_view, name='relatorio_fechamento'),
     path('download-arquivos/', views.download_documentos, name='download_arquivos'),
     path('gerar-pdf/', ReciboPDF.as_view(), name='gerar-pdf'),
     path('gerar-excel/', views.gerar_excel, name='gerar-excel'),
     path('relatorio-detalhado/', views.rel_detalhado, name='relatorio_detalhado'),
     path('relatorio-final-detalhado/', views.rel_final_detalhado, name='relatorio_final_detalhado'),
     #path('test/', views.test_view, name='test'),
]

