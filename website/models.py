from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings
from django.db import models
import os

from PIL import Image


class Ticket(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField(default=timezone.now)
    reply = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} by {self.user} - {self.time_created}'

    BOOK_COVER_SIZE = (260, 400)
    BOOK_COVER_WIDTH = 260
    BOOK_COVER_HEIGHT = 400
    BOOK_COVER_RATIO = BOOK_COVER_WIDTH / BOOK_COVER_HEIGHT  # 0.65

    def resize_cover(self):        
        image = Image.open(self.image)
        image_width, image_height = image.size
        image_ratio = image_width / image_height
        if image_ratio > self.BOOK_COVER_RATIO:
            needed_width = int(image_height * self.BOOK_COVER_RATIO)
            to_center = int((image_width - needed_width)/2)
            cropping = (to_center, 0, needed_width + to_center, image_height)

            image = image.crop(cropping)
            image = image.resize(self.BOOK_COVER_SIZE, Image.ANTIALIAS)
            image.save(self.image.path)

        elif image_ratio < self.BOOK_COVER_RATIO:
            needed_height = int(image_width / self.BOOK_COVER_RATIO)
            to_center = int((image_height - needed_height)/2)
            cropping = (0, to_center, image_width, needed_height + to_center)

            image = image.crop(cropping)
            image = image.resize(self.BOOK_COVER_SIZE, Image.ANTIALIAS)
            image.save(self.image.path)

        self.image.close()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.resize_cover()

    def delete(self, *args, **kwargs):
        os.remove(f".{self.image.url}")
        super().delete(*args, **kwargs)

    def delete_image(self, original_image):
        os.remove(f".{original_image.url}")


class Review(models.Model):
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)    
    headline = models.CharField(max_length=128)    
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=8192, blank=True)

    def __str__(self):
        return f'{self.headline} by {self.user} - {self.time_created}'

    def delete_image(self, original_image):
        os.remove(f".{original_image.url}")