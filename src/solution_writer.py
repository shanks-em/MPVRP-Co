"""
Export de solutions au format .dat
Format conforme aux spécifications MPVRP-CC
"""

from pathlib import Path
from typing import Union
from models import Solution


def write_solution(solution: Solution, filepath: Union[str, Path]):
    """
    Écrit une solution au format .dat requis.
    
    Format:
    - Bloc de 2 lignes par véhicule utilisé
    - Ligne vide entre véhicules
    - 6 lignes de métriques finales
    
    Args:
        solution: La solution à écrire
        filepath: Chemin du fichier de sortie
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    lines = []
    
    # Routes des véhicules
    for route in solution.routes:
        if not route.mini_routes:
            continue  # Véhicule non utilisé
        
        # Ligne 1: Séquence de visites
        sequence = []
        sequence.append(str(route.home_garage))  # Garage départ
        
        for mini_route in route.mini_routes:
            # Dépôt avec quantité chargée
            sequence.append(f"{mini_route.depot_id} [{mini_route.quantity_loaded}]")
            
            # Stations avec quantités livrées
            for delivery in mini_route.deliveries:
                sequence.append(f"{delivery.station_id} ({delivery.quantity})")
        
        sequence.append(str(route.home_garage))  # Retour garage
        
        line1 = f"{route.vehicle_id}: " + " - ".join(sequence)
        
        # Ligne 2: Produits et coûts cumulés
        products = []
        cumulative_cost = 0.0
        current_product = route.initial_product
        
        # Produit au garage de départ
        products.append(f"{current_product}({cumulative_cost:.1f})")
        
        for mini_route in route.mini_routes:
            # Changement de produit ?
            if mini_route.product != current_product:
                transition = solution.instance.get_transition_cost(
                    current_product, 
                    mini_route.product
                )
                cumulative_cost += transition
                current_product = mini_route.product
            
            # Produit au dépôt
            products.append(f"{current_product}({cumulative_cost:.1f})")
            
            # Produit à chaque station
            for _ in mini_route.deliveries:
                products.append(f"{current_product}({cumulative_cost:.1f})")
        
        # Produit au retour garage
        products.append(f"{current_product}({cumulative_cost:.1f})")
        
        line2 = f"{route.vehicle_id}: " + " - ".join(products)
        
        lines.append(line1)
        lines.append(line2)
        lines.append("")  # Ligne vide
    
    # Métriques globales (6 lignes)
    lines.append(str(solution.nb_vehicles_used()))
    lines.append(str(solution.total_transitions()))
    lines.append(f"{solution.total_transition_cost():.1f}")
    lines.append(f"{solution.total_distance():.1f}")
    lines.append(solution.processor)
    lines.append(f"{solution.resolution_time:.2f}")
    
    # Écrire le fichier
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))


def format_solution_summary(solution: Solution) -> str:
    """
    Formate un résumé de la solution pour affichage console.
    
    Args:
        solution: La solution
    
    Returns:
        str: Résumé formaté
    """
    lines = []
    
    lines.append("=" * 70)
    lines.append("SOLUTION MPVRP-CC")
    lines.append("=" * 70)
    
    # Résumé global
    lines.append(f"\nVéhicules utilisés    : {solution.nb_vehicles_used()}/{solution.instance.nb_vehicles}")
    lines.append(f"Distance totale       : {solution.total_distance():.2f}")
    lines.append(f"Coût transition       : {solution.total_transition_cost():.2f}")
    lines.append(f"Nombre transitions    : {solution.total_transitions()}")
    lines.append(f"COÛT TOTAL            : {solution.total_cost():.2f}")
    lines.append(f"Temps de résolution   : {solution.resolution_time:.2f}s")
    
    # Détails par véhicule
    for route in solution.routes:
        if not route.mini_routes:
            continue
        
        lines.append(f"\n{'-' * 70}")
        lines.append(f"Véhicule {route.vehicle_id} (Garage {route.home_garage})")
        lines.append(f"{'-' * 70}")
        lines.append(f"Distance   : {route.total_distance:.2f}")
        lines.append(f"Transition : {route.total_transition_cost:.2f}")
        lines.append(f"Mini-routes: {len(route.mini_routes)}")
        
        for i, mr in enumerate(route.mini_routes, 1):
            lines.append(f"\n  Mini-route {i}:")
            lines.append(f"    Produit    : {mr.product + 1}")
            lines.append(f"    Dépôt      : {mr.depot_id}")
            lines.append(f"    Chargé     : {mr.quantity_loaded}")
            lines.append(f"    Livraisons : {len(mr.deliveries)}")
            
            for delivery in mr.deliveries:
                lines.append(f"      → Station {delivery.station_id}: {delivery.quantity}")
    
    lines.append("\n" + "=" * 70)
    
    return '\n'.join(lines)
