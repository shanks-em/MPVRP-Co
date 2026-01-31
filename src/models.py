"""
Modèles de données MPVRP-CC - Version améliorée
Combine simplicité et robustesse
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import math


@dataclass
class Vehicle:
    """Véhicule de la flotte"""
    id: int
    capacity: int
    home_garage: int
    initial_product: int
    
    def __post_init__(self):
        """Validation des données"""
        if self.capacity <= 0:
            raise ValueError(f"Capacité invalide: {self.capacity}")
        if self.initial_product < 0:
            raise ValueError(f"Produit initial invalide: {self.initial_product}")


@dataclass
class Location:
    """Classe de base pour les localisations"""
    id: int
    x: float
    y: float
    
    def distance_to(self, other: 'Location') -> float:
        """Calcule la distance euclidienne"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class Depot(Location):
    """Dépôt (point de chargement)"""
    stocks: List[int] = field(default_factory=list)


@dataclass
class Garage(Location):
    """Garage (base des véhicules)"""
    pass


@dataclass
class Station(Location):
    """Station-service (client)"""
    demands: List[int] = field(default_factory=list)
    
    def total_demand(self) -> int:
        """Demande totale"""
        return sum(self.demands)


@dataclass
class Instance:
    """Instance complète du problème"""
    uuid: str
    nb_products: int
    nb_depots: int
    nb_garages: int
    nb_stations: int
    nb_vehicles: int
    transition_costs: List[List[float]]
    vehicles: List[Vehicle] = field(default_factory=list)
    depots: List[Depot] = field(default_factory=list)
    garages: List[Garage] = field(default_factory=list)
    stations: List[Station] = field(default_factory=list)
    
    def get_transition_cost(self, from_prod: int, to_prod: int) -> float:
        """Coût de changement de produit"""
        return self.transition_costs[from_prod][to_prod]
    
    def get_total_demand(self, product: int) -> int:
        """Demande totale pour un produit"""
        return sum(s.demands[product] for s in self.stations)
    
    def get_total_stock(self, product: int) -> int:
        """Stock total pour un produit"""
        return sum(d.stocks[product] for d in self.depots)
    
    def get_vehicle(self, vehicle_id: int) -> Vehicle:
        """Récupère un véhicule par ID"""
        return next((v for v in self.vehicles if v.id == vehicle_id), None)
    
    def get_depot(self, depot_id: int) -> Depot:
        """Récupère un dépôt par ID"""
        return next((d for d in self.depots if d.id == depot_id), None)
    
    def get_garage(self, garage_id: int) -> Garage:
        """Récupère un garage par ID"""
        return next((g for g in self.garages if g.id == garage_id), None)
    
    def get_station(self, station_id: int) -> Station:
        """Récupère une station par ID"""
        return next((s for s in self.stations if s.id == station_id), None)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Valide la cohérence de l'instance"""
        errors = []
        
        # Vérifier stocks vs demandes
        for p in range(self.nb_products):
            demand = self.get_total_demand(p)
            stock = self.get_total_stock(p)
            if stock < demand:
                errors.append(f"Produit {p}: stock {stock} < demande {demand}")
        
        # Vérifier garages des véhicules
        garage_ids = {g.id for g in self.garages}
        for v in self.vehicles:
            if v.home_garage not in garage_ids:
                errors.append(f"Véhicule {v.id}: garage {v.home_garage} inexistant")
        
        return len(errors) == 0, errors


@dataclass
class Delivery:
    """Une livraison"""
    station_id: int
    quantity: int


@dataclass
class MiniRoute:
    """Mini-route (un produit)"""
    product: int
    depot_id: int
    quantity_loaded: int
    deliveries: List[Delivery] = field(default_factory=list)
    
    def total_delivered(self) -> int:
        """Quantité totale livrée"""
        return sum(d.quantity for d in self.deliveries)
    
    def is_balanced(self) -> bool:
        """Vérifie chargé == livré"""
        return self.quantity_loaded == self.total_delivered()


@dataclass
class VehicleRoute:
    """Route complète d'un véhicule"""
    vehicle_id: int
    home_garage: int
    initial_product: int
    mini_routes: List[MiniRoute] = field(default_factory=list)
    total_distance: float = 0.0
    total_transition_cost: float = 0.0
    
    def nb_transitions(self) -> int:
        """Nombre de changements de produit"""
        if not self.mini_routes:
            return 0
        
        count = 0
        current = self.initial_product
        for mr in self.mini_routes:
            if mr.product != current:
                count += 1
                current = mr.product
        return count


@dataclass
class Solution:
    """Solution complète"""
    instance: Instance
    routes: List[VehicleRoute] = field(default_factory=list)
    resolution_time: float = 0.0
    processor: str = "Unknown"
    
    def total_distance(self) -> float:
        return sum(r.total_distance for r in self.routes)
    
    def total_transition_cost(self) -> float:
        return sum(r.total_transition_cost for r in self.routes)
    
    def total_cost(self) -> float:
        return self.total_distance() + self.total_transition_cost()
    
    def nb_vehicles_used(self) -> int:
        return sum(1 for r in self.routes if r.mini_routes)
    
    def total_transitions(self) -> int:
        return sum(r.nb_transitions() for r in self.routes)
