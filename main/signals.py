import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Post

@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """
    При сохранении User используем get_or_create.
    Если пользователь создан с нуля — профиль создается.
    Если старый пользователь без профиля просто обновился — профиль автоматически добавится.
    """
    profile, _ = Profile.objects.get_or_create(user=instance)
    profile.save()


@receiver(post_delete, sender=Post)
def     auto_delete_file_on_post_delete(sender, instance, **kwargs):
    """
    Автоматически удаляет изображение с диска при удалении объекта Post.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)  