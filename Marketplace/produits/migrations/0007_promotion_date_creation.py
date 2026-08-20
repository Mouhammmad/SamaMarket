from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produits', '0006_alter_promotion_taux_remise'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotion',
            name='date_creation',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
