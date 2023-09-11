from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from meta.models import Curadoria
from django.utils.translation import gettext_lazy as _

class UserCinonautaManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, username, password, idlattes, orcid):
        user = self.model(
            email = UserCinonautaManager.normalize_email(email),
            username = username,
            idlattes = idlattes,
            orcid = orcid,
            first_name = first_name,
            last_name = last_name,
        )
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, last_name, email, username, idlattes, orcid, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        u = self.create_user(email, first_name, last_name, username, password, idlattes, orcid
                    )
        u.is_admin = True
        u.is_superuser = True
        u.is_staff = True
        u.save(using=self._db)
        return u


class UserCifonauta(AbstractUser):

    first_name = models.CharField('Primeiro Nome', null=True, max_length=50)
    last_name = models.CharField('Último Nome', null=True, max_length=50)
    email = models.EmailField(verbose_name='Email', unique=True)
    username = models.CharField('Usuário', unique=True)

    orcid = models.CharField('Orcid', null=True, max_length=16)
    idlattes = models.CharField('IDLattes', blank=True, null=True, max_length=16)

    is_author = models.BooleanField('Autor', default=False,
            help_text='Informa se o usuário é autor.')

    specialist_of = models.ManyToManyField(Curadoria, related_name='specialist_of', blank=True,
            verbose_name=_('especialista de'), help_text='Mostra de quais curadorias o usuário é especialista.')
    curator_of = models.ManyToManyField(Curadoria, related_name='curator_of', blank=True,
            verbose_name=_('curador de'), help_text='Mostra de quais curadorias o usuário é curador.')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['orcid', 'idlattes', 'first_name', 'last_name', 'email']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_full_name(self):
        # The user is identified by their email address
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

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
