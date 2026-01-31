"""
Package MPVRP-CC Solver
Multi-Product Vehicle Routing Problem with Changeover Cost
"""

__version__ = "1.0.0"
__author__ = "Votre Équipe"

# Imports principaux
from models import (
    Instance, Solution, Vehicle, Depot, Garage, Station,
    VehicleRoute, MiniRoute, Delivery
)
from parser import parse_instance
from solver_simple import SimpleSolver
from solution_writer import write_solution, format_solution_summary
from validator import validate_solution
from api_client import MPVRPAPIClient, print_verification_result

__all__ = [
    'Instance', 'Solution', 'Vehicle', 'Depot', 'Garage', 'Station',
    'VehicleRoute', 'MiniRoute', 'Delivery',
    'parse_instance',
    'SimpleSolver',
    'write_solution', 'format_solution_summary',
    'validate_solution',
    'MPVRPAPIClient', 'print_verification_result'
]
