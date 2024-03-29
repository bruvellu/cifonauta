# Generated by Django 4.2.1 on 2023-11-09 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0165_person_user_cifonauta'),
    ]

    operations = [
        migrations.AddField(
            model_name='modifiedmedia',
            name='license',
            field=models.CharField(choices=[('cc0', 'CC0 (Domínio Público)'), ('cc_by', 'CC BY (Atribuição)'), ('cc_by_sa', 'CC BY-SA (Atribuição-CompartilhaIgual)'), ('cc_by_nd', 'CC BY-ND (Atribuição-SemDerivações)'), ('cc_by_nc', 'CC BY-NC (Atribuição-NãoComercial)'), ('cc_by_nc_sa', 'CC BY-NC-SA (AtribuiçãoNãoComercial-CompartilhaIgual)'), ('cc_by_nc_nd', 'CC BY-NC-ND (Atribuição-SemDerivações-SemDerivados)')], default='cc0', help_text='Tipo de licença da mídia.', max_length=60, verbose_name='Licença'),
        ),
    ]
