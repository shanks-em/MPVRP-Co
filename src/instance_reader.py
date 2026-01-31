"""
Lecteur d'instances MPVRP-CC
"""

import math


class Instance:
    """Représente une instance du problème MPVRP-CC"""
    
    def __init__(self, filename):
        self.filename = filename
        self._read_file(filename)
    
    def _read_file(self, filename):
        """Lit et parse un fichier d'instance"""
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        idx = 0
        
        # UUID
        self.uuid = lines[idx].replace('#', '').strip()
        idx += 1
        
        # Paramètres globaux
        params = list(map(int, lines[idx].split()))
        self.nb_products = params[0]
        self.nb_depots = params[1]
        self.nb_garages = params[2]
        self.nb_stations = params[3]
        self.nb_vehicles = params[4]
        idx += 1
        
        # Matrice de transition
        self.transition_costs = []
        for i in range(self.nb_products):
            row = list(map(float, lines[idx].split()))
            self.transition_costs.append(row)
            idx += 1
        
        # Véhicules
        self.vehicles = []
        for i in range(self.nb_vehicles):
            parts = list(map(int, lines[idx].split()))
            self.vehicles.append({
                'id': parts[0],
                'capacity': parts[1],
                'garage': parts[2],
                'initial_product': parts[3]
            })
            idx += 1
        
        # Dépôts
        self.depots = []
        for i in range(self.nb_depots):
            parts = lines[idx].split()
            self.depots.append({
                'id': int(parts[0]),
                'x': float(parts[1]),
                'y': float(parts[2]),
                'stock': [float(parts[3 + j]) for j in range(self.nb_products)]
            })
            idx += 1
        
        # Garages
        self.garages = []
        for i in range(self.nb_garages):
            parts = lines[idx].split()
            self.garages.append({
                'id': int(parts[0]),
                'x': float(parts[1]),
                'y': float(parts[2])
            })
            idx += 1
        
        # Stations
        self.stations = []
        for i in range(self.nb_stations):
            parts = lines[idx].split()
            self.stations.append({
                'id': int(parts[0]),
                'x': float(parts[1]),
                'y': float(parts[2]),
                'demand': [float(parts[3 + j]) for j in range(self.nb_products)]
            })
            idx += 1
    
    def distance(self, point1, point2):
        """Calcule la distance euclidienne entre deux points"""
        return math.sqrt((point1['x'] - point2['x'])**2 + 
                        (point1['y'] - point2['y'])**2)
    
    def get_changeover_cost(self, from_product, to_product):
        """Retourne le coût de changement de produit"""
        return self.transition_costs[from_product][to_product]
    
    def print_summary(self):
        """Affiche un résumé de l'instance"""
        print(f"\n{'='*60}")
        print(f"Instance: {self.filename}")
        print(f"{'='*60}")
        print(f"Produits  : {self.nb_products}")
        print(f"Dépôts    : {self.nb_depots}")
        print(f"Garages   : {self.nb_garages}")
        print(f"Stations  : {self.nb_stations}")
        print(f"Véhicules : {self.nb_vehicles}")
        print(f"{'='*60}\n")
