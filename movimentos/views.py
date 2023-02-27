from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import MovimentosCaixa, CentrosCustos, ItensOrcamento

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

