"""
Client API MPVRP-CC - Version robuste
"""

import requests
from pathlib import Path
from typing import Union, Dict, Any, Optional


class MPVRPAPIClient:
    """Client pour l'API MPVRP-CC"""
    
    DEFAULT_URL = "https://mpvrp-cc.onrender.com"
    
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or self.DEFAULT_URL).rstrip('/')
    
    def health_check(self, timeout: int = 5) -> bool:
        """Vérifie si l'API est disponible"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=timeout
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def verify_solution(
        self,
        instance_path: Union[str, Path],
        solution_path: Union[str, Path],
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Vérifie une solution via l'API.
        
        Args:
            instance_path: Chemin vers le fichier instance
            solution_path: Chemin vers le fichier solution
            timeout: Timeout en secondes
        
        Returns:
            dict: Résultat de la vérification
                {
                    'feasible': bool,
                    'errors': List[str],
                    'metrics': dict
                }
        """
        instance_path = Path(instance_path)
        solution_path = Path(solution_path)
        
        if not instance_path.exists():
            return {
                'feasible': False,
                'errors': [f"Fichier instance introuvable: {instance_path}"],
                'metrics': {}
            }
        
        if not solution_path.exists():
            return {
                'feasible': False,
                'errors': [f"Fichier solution introuvable: {solution_path}"],
                'metrics': {}
            }
        
        try:
            with open(instance_path, 'rb') as f_inst, \
                 open(solution_path, 'rb') as f_sol:
                
                files = {
                    'instance_file': (instance_path.name, f_inst, 'application/octet-stream'),
                    'solution_file': (solution_path.name, f_sol, 'application/octet-stream')
                }
                
                response = requests.post(
                    f"{self.base_url}/model/verify",
                    files=files,
                    timeout=timeout
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'feasible': False,
                    'errors': [f"Erreur HTTP {response.status_code}: {response.text[:200]}"],
                    'metrics': {}
                }
        
        except requests.Timeout:
            return {
                'feasible': False,
                'errors': ["Timeout de l'API (> 60s)"],
                'metrics': {}
            }
        except requests.RequestException as e:
            return {
                'feasible': False,
                'errors': [f"Erreur de connexion: {str(e)}"],
                'metrics': {}
            }
        except Exception as e:
            return {
                'feasible': False,
                'errors': [f"Erreur inattendue: {str(e)}"],
                'metrics': {}
            }
    
    def generate_instance(
        self,
        params: Dict[str, Any],
        timeout: int = 30
    ) -> Optional[str]:
        """
        Génère une instance via l'API.
        
        Args:
            params: Paramètres de l'instance
            timeout: Timeout en secondes
        
        Returns:
            str: Contenu du fichier .dat ou None
        """
        try:
            response = requests.post(
                f"{self.base_url}/generator/generate",
                json=params,
                timeout=timeout
            )
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"Erreur génération: {response.status_code}")
                return None
        
        except requests.RequestException as e:
            print(f"Erreur connexion: {e}")
            return None


def print_verification_result(result: Dict[str, Any], verbose: bool = True):
    """
    Affiche le résultat de vérification de manière formatée.
    
    Args:
        result: Résultat de la vérification
        verbose: Afficher les détails
    """
    print("\n" + "=" * 70)
    print("RÉSULTAT DE VÉRIFICATION API")
    print("=" * 70)
    
    if result['feasible']:
        print("✅ SOLUTION VALIDE")
    else:
        print("❌ SOLUTION INVALIDE")
    
    # Erreurs
    if result.get('errors'):
        print(f"\nErreurs ({len(result['errors'])}):")
        for i, error in enumerate(result['errors'][:10], 1):
            print(f"  {i}. {error}")
        
        if len(result['errors']) > 10:
            print(f"  ... et {len(result['errors']) - 10} autres erreurs")
    
    # Métriques
    if result.get('metrics'):
        print("\nMétriques API:")
        metrics = result['metrics']
        
        print(f"  Distance totale     : {metrics.get('total_distance', 'N/A')}")
        print(f"  Coût transition     : {metrics.get('total_changeover_cost', 'N/A')}")
        print(f"  Véhicules utilisés  : {metrics.get('nb_vehicles_used', 'N/A')}")
        print(f"  Transitions         : {metrics.get('nb_product_changes', 'N/A')}")
        
        if 'total_distance' in metrics and 'total_changeover_cost' in metrics:
            total = metrics['total_distance'] + metrics['total_changeover_cost']
            print(f"  COÛT TOTAL          : {total:.2f}")
    
    print("=" * 70)
