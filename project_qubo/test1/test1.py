import networkx as nx
import random

def generate_random_graph(num_nodes, edge_prob):
    """
    Generate a random graph with a given number of nodes and edge probability.
    """
    return nx.erdos_renyi_graph(num_nodes, edge_prob)

# Example: Generate a graph with 10 nodes and 0.5 edge probability
random_graph = generate_random_graph(10, 0.5)

# Visualize the graph
import matplotlib.pyplot as plt
nx.draw(random_graph, with_labels=True)
plt.show()


import numpy as np

def create_qubo_matrix(graph, num_colors):
    """
    Create a QUBO matrix for the graph coloring problem.
    """
    num_nodes = len(graph.nodes)
    Q = np.zeros((num_nodes * num_colors, num_nodes * num_colors))

    # Constraint 1: Each vertex gets exactly one color
    for v in range(num_nodes):
        for c1 in range(num_colors):
            Q[v * num_colors + c1, v * num_colors + c1] -= 1
            for c2 in range(c1 + 1, num_colors):
                Q[v * num_colors + c1, v * num_colors + c2] += 2

    # Constraint 2: No two adjacent vertices share the same color
    for u, v in graph.edges:
        for c in range(num_colors):
            Q[u * num_colors + c, v * num_colors + c] += 2

    return Q

# Example: Generate QUBO for a graph with 3 colors
num_colors = 3
qubo_matrix = create_qubo_matrix(random_graph, num_colors)
print("QUBO Matrix:\n", qubo_matrix)


from qiskit import Aer, execute
from qiskit.optimization.applications.ising import max_cut
from qiskit.aqua.algorithms import QAOA
from qiskit.circuit.library import TwoLocal
from qiskit.aqua import QuantumInstance
from qiskit.aqua.components.optimizers import COBYLA

def solve_qubo_with_qaoa(Q):
    """
    Solve the QUBO problem using QAOA.
    """
    # Convert QUBO to Ising Hamiltonian
    qubit_op, offset = max_cut.get_operator(Q)

    # Define QAOA parameters
    optimizer = COBYLA(maxiter=100)
    quantum_instance = QuantumInstance(Aer.get_backend('qasm_simulator'))
    qaoa = QAOA(qubit_op, optimizer, quantum_instance=quantum_instance)

    # Solve the problem
    result = qaoa.run(quantum_instance)
    return result

# Solve the QUBO matrix
result = solve_qubo_with_qaoa(qubo_matrix)
print("QAOA Result:", result)


from qiskit import IBMQ

# Load IBM Quantum account
IBMQ.load_account()
provider = IBMQ.get_provider(hub='ibm-q')
backend = provider.get_backend('ibmq_manila')

quantum_instance = QuantumInstance(backend)
qaoa = QAOA(qubit_op, optimizer, quantum_instance=quantum_instance)

result = qaoa.run(quantum_instance)
print("Quantum Cloud Result:", result)




from itertools import product

def brute_force_solver(graph, num_colors):
    """
    Solve the graph coloring problem using brute force.
    """
    num_nodes = len(graph.nodes)
    min_colors = float('inf')
    best_solution = None

    # Generate all possible color combinations
    for colors in product(range(num_colors), repeat=num_nodes):
        valid = True
        for u, v in graph.edges:
            if colors[u] == colors[v]:
                valid = False
                break
        if valid:
            used_colors = len(set(colors))
            if used_colors < min_colors:
                min_colors = used_colors
                best_solution = colors

    return best_solution, min_colors

# Solve with brute force
solution, min_colors = brute_force_solver(random_graph, num_colors)
print("Brute Force Solution:", solution)
print("Minimum Colors:", min_colors)




def generate_graph_dataset(num_graphs, max_vertices, edge_prob):
    dataset = []
    for _ in range(num_graphs):
        num_nodes = random.randint(10, max_vertices)
        graph = generate_random_graph(num_nodes, edge_prob)
        dataset.append(graph)
    return dataset 

# Create dataset
dataset = generate_graph_dataset(10, 50, 0.3)

# Compare performance
for i, graph in enumerate(dataset):
    print(f"Graph {i+1}: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    brute_force_result = brute_force_solver(graph, num_colors)
    print("Brute Force Colors:", brute_force_result[1])
    # Add QAOA simulation and cloud runs here



from qiskit import IBMQ

# Save and load your IBMQ account
IBMQ.save_account('YOUR_API_TOKEN', overwrite=True)
IBMQ.load_account()


from qiskit import Aer, IBMQ
from qiskit.optimization.applications.ising import max_cut
from qiskit.aqua.algorithms import QAOA
from qiskit.aqua import QuantumInstance
from qiskit.aqua.components.optimizers import COBYLA

# Load IBM Quantum Account
IBMQ.load_account()
provider = IBMQ.get_provider(hub='ibm-q')
backend = provider.get_backend('ibmq_manila')  # Or other available quantum backends

def solve_with_ibm_cloud(qubo_matrix):
    qubit_op, _ = max_cut.get_operator(qubo_matrix)
    optimizer = COBYLA(maxiter=100)
    quantum_instance = QuantumInstance(backend, shots=1024)
    qaoa = QAOA(qubit_op, optimizer, quantum_instance=quantum_instance)
    result = qaoa.run(quantum_instance)
    return result

# Solve the QUBO using IBM Quantum
result = solve_with_ibm_cloud(qubo_matrix)
print("IBM Quantum Result:", result)



from dwave.system import DWaveSampler, EmbeddingComposite

def solve_with_dwave(qubo_matrix):
    sampler = EmbeddingComposite(DWaveSampler())  # Access D-Wave solver
    response = sampler.sample_qubo(qubo_matrix, num_reads=100)
    return response

# Solve the QUBO using D-Wave
dwave_result = solve_with_dwave(qubo_matrix)
print("D-Wave Result:", dwave_result)




import time
import matplotlib.pyplot as plt

def evaluate_and_plot(dataset, num_colors):
    brute_force_times = []
    qaoa_simulator_times = []
    cloud_times = []

    for graph in dataset:
        # Brute Force
        start = time.time()
        brute_force_solver(graph, num_colors)
        brute_force_times.append(time.time() - start)

        # Local QAOA Simulator
        start = time.time()
        solve_qubo_with_qaoa(create_qubo_matrix(graph, num_colors))
        qaoa_simulator_times.append(time.time() - start)

        # Cloud (e.g., IBM Quantum or D-Wave)
        start = time.time()
        solve_with_ibm_cloud(create_qubo_matrix(graph, num_colors))
        cloud_times.append(time.time() - start)

    # Plot runtime comparison
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(dataset)), brute_force_times, label="Brute Force")
    plt.plot(range(len(dataset)), qaoa_simulator_times, label="QAOA Simulator")
    plt.plot(range(len(dataset)), cloud_times, label="Quantum Cloud")
    plt.xlabel("Graph Index")
    plt.ylabel("Runtime (s)")
    plt.title("Runtime Comparison")
    plt.legend()
    plt.show()
