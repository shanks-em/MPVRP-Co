"""
Validation locale des solutions
Vérifie toutes les contraintes avant envoi à l'API
"""

from typing import Tuple, List
from models import Solution, Instance


class SolutionValidator:
    """Validateur de solutions MPVRP-CC"""
    
    def __init__(self, solution: Solution):
        self.solution = solution
        self.instance = solution.instance
        self.errors = []
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Valide la solution complète.
        
        Returns:
            (bool, List[str]): (est_valide, liste_erreurs)
        """
        self.errors = []
        
        # 1. Vérifier que toutes les demandes sont satisfaites
        self._check_demands_satisfied()
        
        # 2. Vérifier les capacités
        self._check_capacities()
        
        # 3. Vérifier l'équilibre chargé/livré
        self._check_balance()
        
        # 4. Vérifier les retours aux garages
        self._check_garage_returns()
        
        # 5. Vérifier les produits initiaux
        self._check_initial_products()
        
        return len(self.errors) == 0, self.errors
    
    def _check_demands_satisfied(self):
        """Vérifie que toutes les demandes sont satisfaites"""
        # Calculer ce qui a été livré
        delivered = {}
        for station in self.instance.stations:
            delivered[station.id] = [0] * self.instance.nb_products
        
        for route in self.solution.routes:
            for mini_route in route.mini_routes:
                for delivery in mini_route.deliveries:
                    delivered[delivery.station_id][mini_route.product] += delivery.quantity
        
        # Comparer avec les demandes
        for station in self.instance.stations:
            for p in range(self.instance.nb_products):
                expected = station.demands[p]
                actual = delivered[station.id][p]
                
                if abs(expected - actual) > 0.01:  # Tolérance pour erreurs d'arrondi
                    self.errors.append(
                        f"Station {station.id}, Produit {p+1}: "
                        f"demandé {expected}, livré {actual}"
                    )
    
    def _check_capacities(self):
        """Vérifie que les capacités des véhicules sont respectées"""
        for route in self.solution.routes:
            vehicle = self.instance.get_vehicle(route.vehicle_id)
            
            for i, mini_route in enumerate(route.mini_routes):
                if mini_route.quantity_loaded > vehicle.capacity:
                    self.errors.append(
                        f"Véhicule {vehicle.id}, Mini-route {i+1}: "
                        f"capacité dépassée ({mini_route.quantity_loaded} > {vehicle.capacity})"
                    )
    
    def _check_balance(self):
        """Vérifie que chargé == livré pour chaque mini-route"""
        for route in self.solution.routes:
            for i, mini_route in enumerate(route.mini_routes):
                loaded = mini_route.quantity_loaded
                delivered = mini_route.total_delivered()
                
                if abs(loaded - delivered) > 0.01:
                    self.errors.append(
                        f"Véhicule {route.vehicle_id}, Mini-route {i+1}: "
                        f"déséquilibre (chargé {loaded}, livré {delivered})"
                    )
    
    def _check_garage_returns(self):
        """Vérifie que chaque véhicule retourne à son garage"""
        for route in self.solution.routes:
            vehicle = self.instance.get_vehicle(route.vehicle_id)
            
            if route.home_garage != vehicle.home_garage:
                self.errors.append(
                    f"Véhicule {vehicle.id}: "
                    f"ne retourne pas à son garage {vehicle.home_garage}"
                )
    
    def _check_initial_products(self):
        """Vérifie que les produits initiaux sont corrects"""
        for route in self.solution.routes:
            vehicle = self.instance.get_vehicle(route.vehicle_id)
            expected = vehicle.initial_product - 1  # 0-indexed
            
            if route.initial_product != expected:
                self.errors.append(
                    f"Véhicule {vehicle.id}: "
                    f"produit initial incorrect ({route.initial_product} != {expected})"
                )


def validate_solution(solution: Solution) -> Tuple[bool, List[str]]:
    """
    Fonction utilitaire pour valider une solution.
    
    Args:
        solution: La solution à valider
    
    Returns:
        (bool, List[str]): (est_valide, erreurs)
    """
    validator = SolutionValidator(solution)
    return validator.validate()
