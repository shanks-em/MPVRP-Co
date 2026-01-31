"""
Modèle de solution MPVRP-CC
"""


class Solution:
    """Représente une solution au problème"""
    
    def __init__(self, instance):
        self.instance = instance
        self.routes = []
        
        self.total_distance = 0.0
        self.total_changeover_cost = 0.0
        self.nb_vehicles_used = 0
        self.nb_product_changes = 0
    
    def add_route(self, vehicle_id, mini_routes):
        """Ajoute la route d'un véhicule"""
        if mini_routes:
            self.routes.append({
                'vehicle_id': vehicle_id,
                'mini_routes': mini_routes
            })
    
    def calculate_metrics(self):
        """Calcule les métriques de la solution"""
        self.total_distance = 0.0
        self.total_changeover_cost = 0.0
        self.nb_vehicles_used = len(self.routes)
        self.nb_product_changes = 0
        
        for route in self.routes:
            vehicle = self._get_vehicle(route['vehicle_id'])
            garage = self._get_garage(vehicle['garage'])
            
            current_pos = garage
            prev_product = None
            
            for mini_route in route['mini_routes']:
                depot = self._get_depot(mini_route['depot_id'])
                self.total_distance += self.instance.distance(current_pos, depot)
                current_pos = depot
                
                if prev_product is not None and prev_product != mini_route['product']:
                    cost = self.instance.get_changeover_cost(prev_product, mini_route['product'])
                    self.total_changeover_cost += cost
                    self.nb_product_changes += 1
                
                prev_product = mini_route['product']
                
                for delivery in mini_route['deliveries']:
                    station = self._get_station(delivery['station_id'])
                    self.total_distance += self.instance.distance(current_pos, station)
                    current_pos = station
            
            self.total_distance += self.instance.distance(current_pos, garage)
        
        return self.total_distance + self.total_changeover_cost
    
    def export_to_file(self, filename):
        """Exporte la solution au format requis"""
        with open(filename, 'w') as f:
            for route in self.routes:
                vehicle_id = route['vehicle_id']
                vehicle = self._get_vehicle(vehicle_id)
                garage_id = vehicle['garage']
                
                line1 = f"{vehicle_id}: {garage_id}"
                line2 = f"{vehicle_id}:"
                
                cumulative_cost = 0.0
                prev_product = None
                
                for mini_route in route['mini_routes']:
                    line1 += f" - {mini_route['depot_id']} [{int(mini_route['loaded_qty'])}]"
                    
                    if prev_product is not None and prev_product != mini_route['product']:
                        cost = self.instance.get_changeover_cost(prev_product, mini_route['product'])
                        cumulative_cost += cost
                    
                    line2 += f" - {mini_route['product']}({cumulative_cost:.1f})"
                    prev_product = mini_route['product']
                    
                    for delivery in mini_route['deliveries']:
                        line1 += f" - {delivery['station_id']} ({int(delivery['quantity'])})"
                        line2 += f" - {mini_route['product']}({cumulative_cost:.1f})"
                
                line1 += f" - {garage_id}"
                
                f.write(line1 + "\n")
                f.write(line2 + "\n\n")
            
            f.write(f"{self.nb_vehicles_used}\n")
            f.write(f"{self.nb_product_changes}\n")
            f.write(f"{self.total_changeover_cost:.2f}\n")
            f.write(f"{self.total_distance:.2f}\n")
            f.write("Intel\n")
            f.write("0.0\n")
    
    def _get_vehicle(self, vehicle_id):
        for v in self.instance.vehicles:
	    if v['id'] == vehicle_id:
		return v
	return None
		    
    def _get_depot(self, depot_id):
	for d in self.instance.depots:
            if d['id'] == depot_id:
		return d
	return None
		    
    def _get_garage(self, garage_id):
	for g in self.instance.garages:
	    if g['id'] == garage_id:
		return g
	return None
		    
    def _get_station(self, station_id):
	for s in self.instance.stations:
	    if s['id'] == station_id:
		return s
	return None
