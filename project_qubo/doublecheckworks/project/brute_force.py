import numpy as np
from itertools import product
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def validate_inputs(num_variables, cost_matrix):
    """
    Validate inputs to ensure compatibility.

    Args:
        num_variables (int): Number of binary variables.
        cost_matrix (np.ndarray): QUBO cost matrix.

    Raises:
        ValueError: If inputs are invalid.
    """
    if not isinstance(num_variables, int) or num_variables <= 0:
        raise ValueError("Number of variables must be a positive integer.")
    if not isinstance(cost_matrix, np.ndarray) or cost_matrix.shape != (num_variables, num_variables):
        raise ValueError("Cost matrix must be a square numpy array matching the number of variables.")

def preprocess_problem(num_variables, cost_matrix):
    """
    Preprocess the problem by validating inputs.

    Args:
        num_variables (int): Number of binary variables.
        cost_matrix (np.ndarray): QUBO cost matrix.

    Returns:
        tuple: Validated number of variables and cost matrix.
    """
    validate_inputs(num_variables, cost_matrix)
    return num_variables, cost_matrix

def generate_solutions(num_variables):
    """
    Generate all possible binary solutions for a given number of variables.

    Args:
        num_variables (int): Number of binary variables.

    Returns:
        list: All possible binary solutions.
    """
    return list(product([0, 1], repeat=num_variables))

def evaluate_solution(solution, cost_matrix):
    """
    Evaluate the cost of a solution using the QUBO matrix.

    Args:
        solution (tuple): Binary solution as a tuple.
        cost_matrix (np.ndarray): QUBO cost matrix.

    Returns:
        float: Cost of the solution.
    """
    solution_array = np.array(solution)
    return solution_array.T @ cost_matrix @ solution_array

def brute_force_solver(num_variables, cost_matrix):
    """
    Solve the QUBO problem using brute force.

    Args:
        num_variables (int): Number of binary variables.
        cost_matrix (np.ndarray): QUBO cost matrix.

    Returns:
        dict: Results including counts, most probable bitstring, validity, and expectation value.
    """
    solutions = generate_solutions(num_variables)
    optimal_solution = None
    optimal_cost = float("inf")
    counts = {}

    for solution in solutions:
        cost = evaluate_solution(solution, cost_matrix)
        # Assign inverse cost as a frequency-like metric for plotting purposes
        counts["".join(map(str, solution))] = 1 / (cost + 1e-6) if cost > 0 else 1

        if cost < optimal_cost:
            optimal_cost = cost
            optimal_solution = solution

    # Standardized result format
    expectation_value = optimal_cost  # Optimal cost represents the expectation value

    return {
        "counts": counts,
        "most_probable_bitstring": "".join(map(str, optimal_solution)),
        "is_valid": True,  # Brute force always finds a valid solution
        "expectation_value": expectation_value
    }
