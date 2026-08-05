import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
import django
django.setup()
from django.db import connection

cursor = connection.cursor()
cols = {row[1] for row in cursor.execute('PRAGMA table_info(produits_produit)')}
ops = [
    ("marque", 'ALTER TABLE produits_produit ADD COLUMN marque VARCHAR(100) NOT NULL DEFAULT ""'),
    ("sku", 'ALTER TABLE produits_produit ADD COLUMN sku VARCHAR(100) NOT NULL DEFAULT ""'),
    ("slug", 'ALTER TABLE produits_produit ADD COLUMN slug VARCHAR(50) NOT NULL DEFAULT ""'),
    ("etat", 'ALTER TABLE produits_produit ADD COLUMN etat VARCHAR(20) NOT NULL DEFAULT "neuf"'),
    ("poids", 'ALTER TABLE produits_produit ADD COLUMN poids decimal(8,2) NOT NULL DEFAULT 0'),
    ("largeur", 'ALTER TABLE produits_produit ADD COLUMN largeur decimal(8,2) NOT NULL DEFAULT 0'),
    ("hauteur", 'ALTER TABLE produits_produit ADD COLUMN hauteur decimal(8,2) NOT NULL DEFAULT 0'),
    ("longueur", 'ALTER TABLE produits_produit ADD COLUMN longueur decimal(8,2) NOT NULL DEFAULT 0'),
    ("mots_cles", 'ALTER TABLE produits_produit ADD COLUMN mots_cles VARCHAR(300) NOT NULL DEFAULT ""'),
]
for name, sql in ops:
    if name not in cols:
        cursor.execute(sql)
print('done')
