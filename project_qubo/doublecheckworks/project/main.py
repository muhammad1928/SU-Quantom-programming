import networkx as nx
from hamiltonian import create_hamiltonian
from circuit_constructor import construct_qaoa_circuit_optimized
from optimize_qaoa import optimize_qaoa
from simulate_qaoa import simulate_qaoa
from brute_force import brute_force_solver
from simulate_on_IBM import run_on_ibm_quantum
from matplotlib import pyplot as plt

def display_results(simulation_result, simulation_type="Simulation", top_k=20):
    """
    Display the results from the simulation or IBM Quantum run.

    Args:
        simulation_result (dict): The result dictionary from the simulation or quantum job.
        simulation_type (str): A label for the type of simulation (e.g., "Simulation" or "IBM Quantum").
        top_k (int): The number of top solutions to display in the plot.
    """
    print(f"{simulation_type} Results:")
    print(f"Measurement Counts: {simulation_result['counts']}")
    print(f"Most Probable Bitstring: {simulation_result['most_probable_bitstring']}")
    print(f"Is Valid: {simulation_result['is_valid']}")
    print(f"Expectation Value: {simulation_result['expectation_value']}")
    print("---------------------------------------------------------------------")

    # Plot results
    bitstrings = list(simulation_result["counts"].keys())
    costs = list(simulation_result["counts"].values())  # These are costs, not frequencies

    # Sort by cost
    sorted_pairs = sorted(zip(bitstrings, costs), key=lambda x: x[1])[:20]  # Top 20 lowest costs
    bitstrings, costs = zip(*sorted_pairs)

    plt.figure(figsize=(10, 6))
    plt.bar(range(len(bitstrings)), costs, color='red', alpha=0.7)
    plt.xticks(range(len(bitstrings)), bitstrings, rotation=45, fontsize=10, ha='right')
    plt.xlabel("Bitstring", fontsize=12)
    plt.ylabel("Cost", fontsize=12)
    plt.title(f"{simulation_type} Results (Top-20 by Cost)", fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()



def main():
    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0)])

    hamiltonian = create_hamiltonian(graph, alpha=0.1)
    print(hamiltonian)
    circuit, parameters = construct_qaoa_circuit_optimized(hamiltonian, p=2, mixer_type="default")
    optimization_result = optimize_qaoa(hamiltonian, circuit, parameters)
    print("---------------------------------------------------------------------")

    # Brute Force solution
    cost_matrix = hamiltonian.to_matrix(sparse=False)  # Convert SparsePauliOp to matrix
    num_variables = cost_matrix.shape[0]
    simulation_result3 = brute_force_solver(num_variables, cost_matrix)
    display_results(simulation_result3, "Brute Force Solution")
    
    print("---------------------------------------------------------------------")

    # Local simulation
    simulation_result1 = simulate_qaoa(circuit, optimization_result, hamiltonian)
    display_results(simulation_result1, "Local Simulation")

    print("---------------------------------------------------------------------")

    # # IBM Quantum simulation
    # simulation_result2 = run_on_ibm_quantum(hamiltonian, circuit, optimization_result)
    # display_results(simulation_result2, "IBM Quantum Simulation")

if __name__ == "__main__":
    main()
