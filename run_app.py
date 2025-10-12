#!/usr/bin/env python3
"""
Script de lancement de l'application Shiny.

Usage:
    python run_app.py
"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from shiny import run_app
    from app import app
    
    print("🚀 Lancement de l'application de modélisation fiscale...")
    print("📊 Interface disponible sur: http://localhost:8000")
    print("⏹️  Arrêter avec Ctrl+C")
    print("-" * 50)
    
    # Lancer l'application
    run_app(app, host="0.0.0.0", port=8000)
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("💡 Assurez-vous d'avoir installé les dépendances:")
    print("   pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Erreur lors du lancement: {e}")
    sys.exit(1)
