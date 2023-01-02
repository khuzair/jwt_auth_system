from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from enum import Enum
from PIL import Image, ImageOps
import os
import time
from io import BytesIO
from django.core.files.base import ContentFile

class MediaSize(Enum):
    #           size      base file name
    LARGE = ((1080, 768), 'large')
    MEDIUM = ((500,500), 'medium')
    THUMBNAIL = ((200, 300), 'thumbnail')


class UploadImage(models.Model):
    # The original image.
    original = models.ImageField(upload_to='original_pics/', blank=True)
    # Resized images...
    large = models.ImageField(upload_to='pictures/', blank=True)
    medium = models.ImageField(upload_to='pictures/', blank=True)
    thumbnail = models.ImageField(upload_to='pictures/', blank=True)
    grayscale = models.ImageField(upload_to='pictures/', blank=True)

    def resizeImg(self, img_size):
        img: Image.Image = Image.open(self.original)
        img.thumbnail(img_size, Image.ANTIALIAS)

        outputIO = BytesIO()
        img.save(outputIO, format=img.format, quality=60)

        return outputIO, img


    def handleResize(self, mediaSize: MediaSize):

        imgSize = mediaSize.value[0]
        imgName = mediaSize.value[1]

        outputIO, img = self.resizeImg(imgSize)

        return {
            'name': f'{imgSize}.{img.format}',
            'content': ContentFile(outputIO.getvalue()),
            'save': False,
        }

    def gray_scale_img(self):
        img: Image.Image = Image.open(self.original)
        new_img = img.convert('L')
        new_name = int(time.time())
        outputIO = BytesIO()
        new_img.save(outputIO, format=img.format, quality=60)
        # img.save('media\pictures\{}.jpeg'.format(new_name))
        return {
            'name': f'grayScale{new_name}.{img.format}',
            'content': ContentFile(outputIO.getvalue()),
            'save': False
        }


    def save(self, **kwargs):

        if not self.large:
            self.large.save(
                **self.handleResize(MediaSize.LARGE)
            )

        if not self.medium:
            self.medium.save(
                **self.handleResize(MediaSize.MEDIUM)
            )

        if not self.thumbnail:
            self.thumbnail.save(
                **self.handleResize(MediaSize.THUMBNAIL)
            )

        if not self.grayscale:
            self.grayscale.save(
                **self.gray_scale_img()
            )
            
            # og_image = Image.open(self.original)
            # # applying grayscale method
            # gray_image = ImageOps.grayscale(og_image)
            # gray_image.save("media\pictures\gray_scale.jpg")

        super().save(**kwargs)



# that class uses an email as the unique identifier instead of a username.
class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, password2=None):
        """
        Creates and saves a User with the given email, name, tc and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email)
        )

        user.set_password(password) # it will generate hash password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, name, tc and password.
        """
        user = self.create_user(
            email,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


# create custom user for api
class CustomUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = None

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


# generate token when user is created automatically
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_token_signal(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)