from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ParametresPlateforme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_plateforme', models.CharField(default='SAMA MARKET', max_length=150)),
                ('email_contact', models.EmailField(blank=True, default='', max_length=254)),
                ('description', models.TextField(blank=True, default='')),
                ('validation_vendeurs', models.BooleanField(default=True)),
                ('notifications_commandes', models.BooleanField(default=True)),
                ('notifications_vendeurs', models.BooleanField(default=True)),
                ('notifications_systeme', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Paramètres de la plateforme',
                'verbose_name_plural': 'Paramètres de la plateforme',
            },
        ),
    ]