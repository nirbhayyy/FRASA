from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
class Review(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    text=models.TextField()
    prediction=models.CharField(max_length=20)
    confidance=models.FloatField(null=True)
    sentiments=models.CharField(max_length=10, null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]
    


class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics/', default='default.png')

    def __str__(self):
        return self.user.username
    


@receiver(post_save,sender=User)
def create_profile(sender,instance,created , **kwargs):
    if created:
        Profile.objects.create(user=instance)