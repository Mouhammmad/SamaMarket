from django.db import migrations


def archive_test_products(apps, schema_editor):
    Produit = apps.get_model('produits', 'Produit')
    Produit.objects.filter(
        categorie__nom__iexact='Categorie test',
        nom__in=['huile de serpent', 'Produit test'],
    ).update(est_actif=False)


class Migration(migrations.Migration):
    dependencies = [
        ('produits', '0009_migrate_images_cloudinary'),
    ]

    operations = [
        migrations.RunPython(archive_test_products, migrations.RunPython.noop),
    ]
