# Documentation API SamaMarket

## Base URL
```
http://127.0.0.1:8000/api/
```

## 🛍️ Endpoints Produits

### 1. Lister tous les produits (PUBLIC)
```
GET /api/produits/
```

**Paramètres de query:**
- `page` - Numéro de page (défaut: 1, 20 par page)
- `search` - Rechercher par nom, description ou catégorie
- `ordering` - Trier par: `prix`, `date_creation`, `nom` (préfixer avec `-` pour décroissant)
- `categorie` - Filtrer par catégorie
- `boutique` - Filtrer par nom de boutique
- `prix_min` - Prix minimum
- `prix_max` - Prix maximum

**Exemples:**
```bash
# Tous les produits, page 1
GET /api/produits/?page=1

# Rechercher des T-shirts
GET /api/produits/?search=T-shirt

# Produits entre 5000 et 15000 FCFA
GET /api/produits/?prix_min=5000&prix_max=15000

# Catégorie "Vêtements"
GET /api/produits/?categorie=Vêtements

# Produits d'une boutique, triés par prix décroissant
GET /api/produits/?boutique=SamaBoutique&ordering=-prix

# Combinaison: recherche + prix + tri
GET /api/produits/?search=shirt&prix_min=1000&prix_max=10000&ordering=prix
```

**Réponse:**
```json
{
  "count": 150,
  "next": "http://127.0.0.1:8000/api/produits/?page=2",
  "previous": null,
  "results": [
    {
      "id": 5,
      "nom": "T-shirt blanc",
      "description": "T-shirt en coton 100%",
      "prix": 8500,
      "stock": 50,
      "image": "/media/produits/tshirt.jpg",
      "categorie": {"id": 2, "nom": "Vêtements"},
      "boutique": {"id": 1, "nom": "SamaBoutique"},
      "date_creation": "2026-07-28T10:30:00Z"
    }
  ]
}
```

---

### 2. Détails d'un produit (PUBLIC)
```
GET /api/produits/{id}/
```

**Exemple:**
```bash
GET /api/produits/5/
```

---

### 3. Produits du vendeur (AUTHENTIFIÉ + VENDEUR)
```
GET /api/produits/vendeur/
```

**Paramètres:** Même que `GET /api/produits/`

**Authentification requise:**
```bash
Authorization: Bearer <JWT_TOKEN>
```

**Exemple:**
```bash
GET /api/produits/vendeur/?search=shirt&ordering=-date_creation
```

---

### 4. Créer un produit (AUTHENTIFIÉ + VENDEUR)
```
POST /api/produits/vendeur/
```

**Content-Type:** `multipart/form-data`

**Paramètres du body:**
```json
{
  "nom": "Pantalon noir",
  "description": "Pantalon en coton",
  "prix": 12000,
  "stock": 30,
  "categorie": 2,
  "image": <fichier>
}
```

**Exemple curl:**
```bash
curl -X POST http://127.0.0.1:8000/api/produits/vendeur/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "nom=Pantalon noir" \
  -F "description=Pantalon en coton" \
  -F "prix=12000" \
  -F "stock=30" \
  -F "categorie=2" \
  -F "image=@path/to/image.jpg"
```

---

### 5. Modifier un produit (AUTHENTIFIÉ + VENDEUR)
```
PATCH /api/produits/vendeur/{id}/
```

**Exemple:**
```bash
curl -X PATCH http://127.0.0.1:8000/api/produits/vendeur/5/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prix": 9500, "stock": 40}'
```

---

### 6. Supprimer un produit (AUTHENTIFIÉ + VENDEUR)
```
DELETE /api/produits/vendeur/{id}/
```

---

## 📁 Catégories

### Lister les catégories (PUBLIC)
```
GET /api/produits/categories/
```

**Réponse:**
```json
[
  {"id": 1, "nom": "Électronique", "image": "/media/categories/..."},
  {"id": 2, "nom": "Vêtements", "image": "/media/categories/..."}
]
```

---

## ❤️ Favoris

### Mes favoris (AUTHENTIFIÉ)
```
GET /api/produits/favoris/mes_favoris/
```

### Ajouter aux favoris (AUTHENTIFIÉ)
```
POST /api/produits/favoris/ajouter/
```

**Body:**
```json
{
  "produit": 5
}
```

### Retirer des favoris (AUTHENTIFIÉ)
```
DELETE /api/produits/favoris/supprimer/{id}/
```

---

## 📋 Avis

### Lister les avis d'un produit (PUBLIC)
```
GET /api/produits/avis/?produit=5
```

### Ajouter un avis (AUTHENTIFIÉ)
```
POST /api/produits/avis/
```

**Body:**
```json
{
  "produit": 5,
  "note": 5,
  "commentaire": "Excellent produit!"
}
```

---

## 🛒 Commandes

### Lister mes commandes (AUTHENTIFIÉ)
```
GET /api/commandes/
```

**Paramètres:**
- `page` - Pagination
- `ordering` - Trier par date: `date_creation`, `-date_creation`

### Créer une commande (AUTHENTIFIÉ)
```
POST /api/commandes/
```

**Body:**
```json
{
  "articles": [
    {"produit": 5, "quantite": 2},
    {"produit": 8, "quantite": 1}
  ],
  "adresse_livraison": "123 Rue de la Paix",
  "telephone": "+221771234567"
}
```

---

## 🏪 Boutiques

### Lister les boutiques (PUBLIC)
```
GET /api/boutiques/
```

### Détails d'une boutique (PUBLIC)
```
GET /api/boutiques/{id}/
```

### Ma boutique (AUTHENTIFIÉ + VENDEUR)
```
GET /api/boutiques/ma_boutique/
```

### Mettre à jour ma boutique (AUTHENTIFIÉ + VENDEUR)
```
PATCH /api/boutiques/ma_boutique/
```

**Body:**
```json
{
  "nom": "Nouvelle boutique",
  "description": "Description mise à jour",
  "ville": "Dakar"
}
```

---

## 🔐 Authentification

### Se connecter
```
POST /api/token/
```

**Body:**
```json
{
  "email": "vendeur@example.com",
  "password": "password123"
}
```

**Réponse:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "vendeur@example.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "role": "VENDOR"
  }
}
```

### Rafraîchir le token
```
POST /api/token/refresh/
```

**Body:**
```json
{
  "refresh": "YOUR_REFRESH_TOKEN"
}
```

---

## 📊 Dashboard Vendeur

### Statistiques vendeur (AUTHENTIFIÉ + VENDEUR)
```
GET /api/dashboard/vendeur/stats/
```

**Réponse:**
```json
{
  "total_produits": 15,
  "total_commandes": 42,
  "revenus_totaux": 850000,
  "commandes_en_attente": 3,
  "produits_rupture_stock": 2
}
```

---

## 📈 Pagination & Filtres

### Format de réponse paginée
```json
{
  "count": 150,           // Total d'items
  "next": "http://...",   // URL page suivante
  "previous": null,       // URL page précédente
  "results": [...]        // Données de la page actuelle
}
```

### Changer la taille des pages
```bash
# GET sur n'importe quel endpoint avec ?page=1
# La taille par défaut est 20, pour changer voir settings.py
```

---

## ❌ Codes d'erreur

| Code | Signification |
|------|---------------|
| 200 | OK - Succès |
| 201 | Created - Créé avec succès |
| 400 | Bad Request - Données invalides |
| 401 | Unauthorized - Authentification requise |
| 403 | Forbidden - Accès refusé (permissions) |
| 404 | Not Found - Ressource non trouvée |
| 500 | Server Error - Erreur serveur |

---

## 🧪 Exemples complets

### Workflow complet client

```bash
# 1. Se connecter
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"client@example.com","password":"pass"}'
# Récupère: access token

# 2. Voir les produits (PUBLIC, pas besoin d'auth)
curl http://127.0.0.1:8000/api/produits/?prix_min=1000&prix_max=50000

# 3. Ajouter aux favoris
curl -X POST http://127.0.0.1:8000/api/produits/favoris/ajouter/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"produit":5}'

# 4. Créer une commande
curl -X POST http://127.0.0.1:8000/api/commandes/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "articles": [{"produit":5,"quantite":2}],
    "adresse_livraison": "123 Rue",
    "telephone": "+221771234567"
  }'

# 5. Voir mes commandes
curl http://127.0.0.1:8000/api/commandes/ \
  -H "Authorization: Bearer TOKEN"
```

### Workflow complet vendeur

```bash
# 1. Se connecter (vendeur)
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"vendeur@example.com","password":"pass"}'

# 2. Voir mes produits
curl http://127.0.0.1:8000/api/produits/vendeur/ \
  -H "Authorization: Bearer TOKEN"

# 3. Ajouter un produit
curl -X POST http://127.0.0.1:8000/api/produits/vendeur/ \
  -H "Authorization: Bearer TOKEN" \
  -F "nom=T-shirt" \
  -F "description=Coton 100%" \
  -F "prix=8500" \
  -F "stock=50" \
  -F "categorie=2" \
  -F "image=@tshirt.jpg"

# 4. Voir les commandes de mes produits
curl http://127.0.0.1:8000/api/commandes/ \
  -H "Authorization: Bearer TOKEN"

# 5. Voir stats
curl http://127.0.0.1:8000/api/dashboard/vendeur/stats/ \
  -H "Authorization: Bearer TOKEN"
```

---

**Dernière mise à jour:** 2026-07-29
