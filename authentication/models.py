from django.contrib.auth.models import User
from django.conf import settings
from django.db import models

from PIL import Image, ImageOps

import os


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(default="profile_pics/default.png", upload_to="profile_pics/")
    follows = models.ManyToManyField("self",
                                     related_name="followed_by",
                                     symmetrical=False,
                                     blank=True)

    # Shows the name of the user in the "Profiles" admin page
    def __str__(self):
        return self.user.username
    
    def profile_photo_path():
        """ Defines the path for the profile pictures """
        parent_dir = "../"
        default_pic = "profile_pics/default.png"
        pathtest = os.path.join(parent_dir, os.path.dirname(default_pic))
        return pathtest

    def save(self, *args, **kwargs):
        """ Saves the uploaded profile picture by resizing
        and, if needed, cropping it. """
        if self.profile_photo.url != "default.png":
            super().save()

            img = ImageOps.fit(
                Image.open(self.profile_photo.path),
                (100, 100),
                method=3,
                centering=(0.5, 0.5)
            )

            img.save(self.profile_photo.path)


class UserFollow(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )
    followed_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followed_by'
    )

    def __str__(self):
        return f"{self.user.username} -> {self.followed_user.username}"

    class Meta:
        unique_together = ('user', 'followed_user')