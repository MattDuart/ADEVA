from django.db.models.signals import post_save,post_delete, pre_save
#I have used django user model to use post save, post delete.
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import PagarReceber, MovimentosCaixa, ArquivosContabeis




@receiver(pre_save,sender=MovimentosCaixa)
def update_verification(sender, instance, **kwargs):
    instance.new_value = -1
    try:
        old_instance = MovimentosCaixa.objects.get(id=instance.id)
        lcto = old_instance.lcto_ref
        
        if(lcto):
            valor = old_instance.valor
            valor_anterior = lcto.valor_pago
            lcto.valor_pago = valor_anterior - valor
            if(lcto.valor_pago >= lcto.valor_docto):
                lcto.status = 'TP'
            elif(lcto.valor_pago < lcto.valor_docto and lcto.valor_pago > 0):
               lcto.status = 'PP'
            else:
                lcto.valor_pago = 0
                lcto.status = 'AB'
            lcto.save()
            instance.new_value = lcto.valor_pago
            
                



    except MovimentosCaixa.DoesNotExist:  # to handle initial object creation
        return None  # just exiting from signal    
            



@receiver(post_save,sender=MovimentosCaixa)
def set_pagar_receber(sender,instance,created,**kwargs):
    if (instance.tipo in ['PG', 'PR']):
        lcto = instance.lcto_ref
        valor = instance.valor
        valor_anterior = lcto.valor_pago
        if (instance.new_value >= 0):
            valor_anterior = instance.new_value
        lcto.valor_pago = valor_anterior + valor
        if(lcto.valor_pago >= lcto.valor_docto):
            lcto.status = 'TP'
        elif(lcto.valor_pago < lcto.valor_docto and lcto.valor_pago > 0):
            lcto.status = 'PP'
        else:
            lcto.status = 'AB'
        lcto.save()
            
@receiver(post_delete,sender=MovimentosCaixa)
def delete_profile(sender,instance,*args,**kwargs):
    if (instance.tipo in ['PG', 'PR']):
            lcto = instance.lcto_ref
            if(lcto):
                valor = instance.valor
                valor_anterior = lcto.valor_pago
                lcto.valor_pago = valor_anterior - valor
                if(lcto.valor_pago >= lcto.valor_docto):
                    lcto.status = 'TP'
                elif(lcto.valor_pago < lcto.valor_docto and lcto.valor_pago > 0):
                    lcto.status = 'PP'
                else:
                    lcto.status = 'AB'
        
                lcto.save()
            