from django.db.models.signals import post_save,post_delete
#I have used django user model to use post save, post delete.
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import PagarReceber, MovimentosCaixa, ArquivosContabeis


@receiver(post_save,sender=MovimentosCaixa)
def create_profile(sender,instance,created,**kwargs):
    if created:
        #write your logic here
        print("User Profile Created")
        
@receiver(post_delete,sender=MovimentosCaixa)
def delete_profile(sender,instance,*args,**kwargs):
    #write your login when user profile is deleted.
    print("User Profile Deleted")