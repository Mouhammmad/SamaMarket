from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produits', '0005_produit_etat_produit_hauteur_produit_largeur_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promotion',
            name='taux_remise',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]