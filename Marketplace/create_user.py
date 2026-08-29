#!/usr/bin/env python
"""
Utilitaire pour créer des utilisateurs rapidement
Usage: python create_user.py <username> <email> <password> <role>
ou
python create_user.py  (mode interactif)
"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Marketplace.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_user_interactive():
    """Mode interactif pour créer un utilisateur"""
    print("=" * 60)
    print("CRÉATION D'UN NOUVEL UTILISATEUR")
    print("=" * 60)
    
    username = input("\nUsername: ").strip()
    if not username:
        print("❌ Username requis")
        return
    
    email = input("Email: ").strip()
    if not email:
        print("❌ Email requis")
        return
    
    password = input("Mot de passe: ").strip()
    if not password or len(password) < 8:
        print("❌ Mot de passe requis (minimum 8 caractères)")
        return
    
    first_name = input("Prénom (optionnel): ").strip() or ""
    last_name = input("Nom (optionnel): ").strip() or ""
    
    roles = [('CUSTOMER', 'Client'), ('VENDOR', 'Vendeur'), ('ADMIN', 'Administrateur')]
    print("\nRôles disponibles:")
    for i, (code, label) in enumerate(roles, 1):
        print(f"  {i}. {label} ({code})")
    
    role_choice = input("Sélectionnez le rôle (1-3) [1]: ").strip() or "1"
    try:
        role = roles[int(role_choice) - 1][0]
    except (ValueError, IndexError):
        role = 'CUSTOMER'
    
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        print("\n" + "=" * 60)
        print("✅ UTILISATEUR CRÉÉ AVEC SUCCÈS!")
        print("=" * 60)
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Rôle: {user.role}")
        print(f"ID: {user.id}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

def create_user_cli(username, email, password, role='CUSTOMER'):
    """Créer un utilisateur via arguments CLI"""
    try:
        if User.objects.filter(username=username).exists():
            print(f"❌ L'utilisateur '{username}' existe déjà")
            return False
        
        if User.objects.filter(email=email).exists():
            print(f"❌ L'email '{email}' est déjà utilisé")
            return False
        
        if len(password) < 8:
            print("❌ Le mot de passe doit faire au minimum 8 caractères")
            return False
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )
        
        print(f"✅ Utilisateur créé: {username} ({role})")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) < 4:
            print("Usage: python create_user.py <username> <email> <password> [role]")
            print("Rôles: CUSTOMER, VENDOR, ADMIN")
            sys.exit(1)
        
        username = sys.argv[1]
        email = sys.argv[2]
        password = sys.argv[3]
        role = sys.argv[4] if len(sys.argv) > 4 else 'CUSTOMER'
        
        create_user_cli(username, email, password, role)
    else:
        create_user_interactive()
