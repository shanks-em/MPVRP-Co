"""
Test de l'API de validation
"""

import sys
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from api_client import MPVRPAPIClient, print_verification_result


def test_api():
    """Teste la connexion et la validation API"""
    
    print("="*70)
    print("TEST API MPVRP-CC")
    print("="*70)
    
    # 1. Test connexion
    print("\n1. Test de connexion...")
    client = MPVRPAPIClient()
    
    if client.health_check():
        print("   ✅ API disponible")
    else:
        print("   ❌ API indisponible")
        print("   URL:", client.base_url)
        return
    
    # 2. Test validation (si vous avez des fichiers)
    instance_folder = Path("instances/small")
    
    if instance_folder.exists():
        instances = list(instance_folder.glob("*.dat"))
        
        if instances:
            print(f"\n2. Test validation avec {instances[0].name}...")
            
            # Il faut d'abord une solution
            # On va en créer une simple pour tester
            
            print("   📝 Créez d'abord une solution avec:")
            print(f"      python3 main.py {instances[0]}")
            print("\n   Puis testez la validation avec:")
            print(f"      python3 test_validation.py {instances[0]} solutions/Sol_{instances[0].name}")
        else:
            print("\n2. Aucune instance trouvée")
            print("   Générez des instances avec:")
            print("      python3 scripts/generate_instances.py")
    else:
        print("\n2. Dossier instances/ introuvable")
        print("   Créez-le et ajoutez des fichiers .dat")
    
    print("\n" + "="*70)


if name == "__main__":
    test_api()
