#!/usr/bin/env python3
"""
Script de test pour vérifier la fonctionnalité admin
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from core.security import hash_password, verify_password, create_access_token
from datetime import datetime

def test_admin_functionality():
    """Test basique de la fonctionnalité admin"""
    print("🧪 Test de la fonctionnalité admin...")

    # Test du hashage de mot de passe
    password = "admin123"
    hashed = hash_password(password)
    assert verify_password(password, hashed), "Le hashage de mot de passe ne fonctionne pas"
    print("✅ Hashage de mot de passe OK")

    # Test de la création de token
    token = create_access_token({"sub": "admin@healthai.com", "role": "admin"})
    assert token, "La création de token ne fonctionne pas"
    print("✅ Création de token OK")

    print("🎉 Tous les tests de base sont passés!")

if __name__ == "__main__":
    test_admin_functionality()