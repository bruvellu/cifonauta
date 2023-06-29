from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserCinonautaManager(BaseUserManager):
    def create_user(self, email, username, password):
        user = self.model(
            email = UserCinonautaManager.normalize_email(email),
            username = username,
        )
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email, username, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        u = self.create_user(email, username, password
                    )
        u.is_admin = True
        u.is_superuser = True
        u.is_staff = True
        u.save(using=self._db)
        return u


class UserCifonauta(AbstractUser):
    email = models.EmailField(verbose_name='Email', unique=True)
    username = models.CharField('Usuário', unique=True)
    orcid = models.CharField('Orcid', unique=True, default=None, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        # The user is identified by their email address
        return self.username

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


# Create your models here.
