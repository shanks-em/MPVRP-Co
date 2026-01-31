"""
Solveur glouton amélioré avec gestion des stocks
"""

import time
import platform
from typing import Dict, Optional
from models import Instance, Solution, VehicleRoute, MiniRoute, Delivery, Station, Location, Depot


class SimpleSolver:
    """Solveur glouton optimisé avec gestion des stocks"""
    
    def __init__(self, instance: Instance, changeover_weight: float = 0.5):
        self.instance = instance
        self.changeover_weight = changeover_weight
        
        # Demandes restantes par station
        self.remaining_demand = {}
        for s in instance.stations:
            self.remaining_demand[s.id] = list(s.demands)
        
        # NOUVEAU: Stocks restants par dépôt
        self.remaining_stock = {}
        for d in instance.depots:
            self.remaining_stock[d.id] = list(d.stocks)
    
    def solve(self) -> Solution:
        """Résout l'instance"""
        start = time.time()
        
        solution = Solution(
            instance=self.instance,
            processor=platform.processor() or "Unknown"
        )
        
        # Créer les routes
        for vehicle in self.instance.vehicles:
            route = self._build_route(vehicle)
            solution.routes.append(route)
            
            if not self._has_remaining_demand():
                break
        
        # Calculer métriques
        self._compute_metrics(solution)
        solution.resolution_time = time.time() - start
        
        return solution
    
    def _build_route(self, vehicle) -> VehicleRoute:
        """Construit la route d'un véhicule"""
        route = VehicleRoute(
            vehicle_id=vehicle.id,
            home_garage=vehicle.home_garage,
            initial_product=vehicle.initial_product - 1
        )
        
        garage = self.instance.get_garage(vehicle.home_garage)
        current_pos = garage
        current_product = vehicle.initial_product - 1
        
        max_iter = 100
        for _ in range(max_iter):
            if not self._has_remaining_demand():
                break
            
            # Choisir produit
            product = self._select_product(current_pos, current_product, vehicle.capacity)
            if product is None:
                break
            
            # Créer mini-route
            mini_route = self._build_mini_route(vehicle, product, current_pos)
            if not mini_route or not mini_route.deliveries:
                break
            
            route.mini_routes.append(mini_route)
            current_product = product
            
            # Mise à jour position
            last_delivery = mini_route.deliveries[-1]
            current_pos = self.instance.get_station(last_delivery.station_id)
        
        return route
    
    def _select_product(self, pos, current_product, capacity):
        """Sélectionne le meilleur produit"""
        best_product = None
        best_score = float('inf')
        
        for p in range(self.instance.nb_products):
            if not self._has_demand_for_product(p):
                continue
            
            # NOUVEAU: Vérifier qu'il y a du stock disponible
            if not self._has_stock_for_product(p):
                continue
            
            # Distance moyenne
            avg_dist = self._avg_distance_to_product(pos, p)
            if avg_dist == float('inf'):
                continue
            
            # Coût changeover
            changeover = 0.0
            if p != current_product:
                changeover = self.instance.get_transition_cost(current_product, p)
            
            # Score
            score = avg_dist + self.changeover_weight * changeover
            
            if score < best_score:
                best_score = score
                best_product = p
        
        return best_product
    
    def _build_mini_route(self, vehicle, product, current_pos):
        """Construit une mini-route"""
        # NOUVEAU: Choisir dépôt avec stock disponible
        depot = self._best_depot_with_stock(current_pos, product)
        if not depot:
            return None
        
        mini_route = MiniRoute(
            product=product,
            depot_id=depot.id,
            quantity_loaded=0
        )
        
        pos = depot
        
        # NOUVEAU: Capacité limitée par le stock disponible
        available_stock = self.remaining_stock[depot.id][product]
        capacity = min(vehicle.capacity, available_stock)
        
        if capacity <= 0:
            return None
        
        visited = set()
        
        while capacity > 0:
            station = self._closest_station_with_demand(pos, product, visited)
            if not station:
                break
            
            visited.add(station.id)
            demand = self.remaining_demand[station.id][product]
            
            if demand == 0:
                continue
            
            # Livrer ce qu'on peut
            to_deliver = min(demand, capacity)
            
            mini_route.deliveries.append(Delivery(station.id, to_deliver))
            mini_route.quantity_loaded += to_deliver
            
            # Mettre à jour demande
            self.remaining_demand[station.id][product] -= to_deliver
            capacity -= to_deliver
            pos = station
        
        # NOUVEAU: Mettre à jour le stock du dépôt
        if mini_route.quantity_loaded > 0:
            self.remaining_stock[depot.id][product] -= mini_route.quantity_loaded
        
        return mini_route
    
    def _has_remaining_demand(self) -> bool:
        """Y a-t-il encore de la demande?"""
        for demands in self.remaining_demand.values():
            if sum(demands) > 0:
                return True
        return False
    
    def _has_demand_for_product(self, product: int) -> bool:
        """Y a-t-il de la demande pour ce produit?"""
        for demands in self.remaining_demand.values():
            if demands[product] > 0:
                return True
        return False
    
    def _has_stock_for_product(self, product: int) -> bool:
        """Y a-t-il du stock disponible pour ce produit?"""
        for stocks in self.remaining_stock.values():
            if stocks[product] > 0:
                return True
        return False
    
    def _avg_distance_to_product(self, pos: Location, product: int) -> float:
        """Distance moyenne aux stations demandant ce produit"""
        distances = []
        for station in self.instance.stations:
            if self.remaining_demand[station.id][product] > 0:
                distances.append(pos.distance_to(station))
        
        return sum(distances) / len(distances) if distances else float('inf')
    
    def _closest_depot(self, pos: Location) -> Optional[Depot]:
        """Dépôt le plus proche"""
        if not self.instance.depots:
            return None
        
        return min(self.instance.depots, key=lambda d: pos.distance_to(d))
    
    def _best_depot_with_stock(self, pos: Location, product: int) -> Optional[Depot]:
        """Meilleur dépôt avec stock disponible pour le produit"""
        candidates = [
            d for d in self.instance.depots
            if self.remaining_stock[d.id][product] > 0
        ]
        
        if not candidates:
            return None
        
        # Choisir le dépôt avec le meilleur ratio stock/distance
        def score(depot):
            distance = pos.distance_to(depot)
            stock = self.remaining_stock[depot.id][product]
            # Plus de stock et moins de distance = meilleur score
            return distance / max(stock, 1)
        
        return min(candidates, key=score)
    
    def _closest_station_with_demand(self, pos: Location, product: int, visited: set):
        """Station la plus proche avec demande pour le produit"""
        candidates = [
            s for s in self.instance.stations
            if s.id not in visited and self.remaining_demand[s.id][product] > 0
        ]
        
        if not candidates:
            return None
        
        return min(candidates, key=lambda s: pos.distance_to(s))
    
    def _compute_metrics(self, solution: Solution):
        """Calcule les métriques de la solution"""
        for route in solution.routes:
            if not route.mini_routes:
                continue
            
            # Calculer distance et coût transition
            garage = self.instance.get_garage(route.home_garage)
            current_pos = garage
            current_product = route.initial_product
            
            total_distance = 0.0
            total_transition = 0.0
            
            for mini_route in route.mini_routes:
                # Distance garage -> dépôt
                depot = self.instance.get_depot(mini_route.depot_id)
                total_distance += current_pos.distance_to(depot)
                current_pos = depot
                
                # Coût transition
                if mini_route.product != current_product:
                    total_transition += self.instance.get_transition_cost(
                        current_product, mini_route.product
                    )
                    current_product = mini_route.product
                
                # Distance dépôt -> stations
                for delivery in mini_route.deliveries:
                    station = self.instance.get_station(delivery.station_id)
                    total_distance += current_pos.distance_to(station)
                    current_pos = station
            
            # Distance retour garage
            total_distance += current_pos.distance_to(garage)
            
            route.total_distance = total_distance
            route.total_transition_cost = total_transition
