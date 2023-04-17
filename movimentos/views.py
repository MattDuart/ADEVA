# Create your views here.
from django.shortcuts import render
from .models import MovimentosCaixa, CentrosCustos, ItensOrcamento
from django.http import HttpResponse



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
    return render(request, 'fechamento.html')

