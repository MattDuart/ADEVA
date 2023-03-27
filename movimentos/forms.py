from django import forms
from django.core.exceptions import ValidationError

class MovimentoFormAdmin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MovimentoFormAdmin, self).__init__(*args, **kwargs)
        self.fields['tipo'].widget.attrs['class'] = 'select_tipo'
        self.fields['conta_origem'].widget.attrs['class'] = 'select_conta_origem'
        self.fields['conta_destino'].widget.attrs['class'] = 'select_conta_destino'
     #   self.fields['lcto_ref'].widget.attrs['class'] = 'select_lcto_ref'

    def clean(self):
        tipo = self.cleaned_data['tipo']
        conta_destino = self.cleaned_data['conta_destino']
        conta_origem = self.cleaned_data['conta_origem']
        lcto_ref = self.cleaned_data['lcto_ref']

        if tipo == 'SI':
            if conta_destino is None:
                raise ValidationError("Lançamento tipo saldo inicial exige uma conta destino.")
            if conta_origem is not None:
                raise ValidationError("Lançamento tipo saldo inicial não deve ter conta de origem")
        elif tipo == 'TR':
            if conta_destino is None or conta_origem is None:
                raise ValidationError("Lançamento tipo tranferência exige as contas de origem e destino.")
        elif tipo == 'PG':
            if conta_origem is None or lcto_ref is None:
                raise ValidationError("Lançamento tipo pagamento exige a conta de origem e o lançamento de referência.")
            if conta_destino is not None:
                raise ValidationError("Lançamento tipo pagamento não deve ter conta de destino")
     
        elif tipo == 'PR':
            if conta_destino is None or lcto_ref is None:
                raise ValidationError("Lançamento tipo recebimento exige a conta de destino e o lançamento de referência.")
            if conta_origem is not None:
                raise ValidationError("Lançamento tipo recebimento não deve ter valores de conta de origem")
   


class DateRangeForm(forms.Form):
    start_date = forms.DateField(label='Data de Início')
    end_date = forms.DateField(label='Data de Fim')