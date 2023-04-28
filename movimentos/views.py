# Create your views here.
from django.shortcuts import render
from .models import MovimentosCaixa, CentrosCustos, ItensOrcamento
from django.http import HttpResponse
from django.contrib import admin


def movimentos_caixa_list(request):
    movimentos = MovimentosCaixa.objects.all()
    projetos = CentrosCustos.objects.all()
    orcementos = ItensOrcamento.objects.all()

    return render( request,
                  'movimento/lista.html',
                  {
                    'movimentos' : movimentos,
                    'projetos': projetos,
                    'orcamentos': orcementos
                  })


def fechamento_view(request):
    context = admin.site.each_context(request)
    # Add custom context data here
    return render(request, 'fechamento.html', context=context)

