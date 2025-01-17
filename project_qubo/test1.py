import numpy as np
import networkx as nx
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import EstimatorV2
from qiskit.quantum_info import SparsePauliOp
from qiskit.circuit import Parameter
from qiskit.visualization import plot_histogram
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Step 1: Convert QUBO matrix to cost Hamiltonian
def qubo_to_hamiltonian(qubo_matrix):
    """
    Convert a QUBO matrix into a cost Hamiltonian for QAOA.

    Parameters:
        qubo_matrix (numpy.ndarray): QUBO matrix.

    Returns:
        SparsePauliOp: Cost Hamiltonian as a Pauli operator.
    """
    n = qubo_matrix.shape[0]
    terms = []
    for i in range(n):
        pauli_string = ["I"] * n
        pauli_string[i] = "Z"
        terms.append(("".join(pauli_string), qubo_matrix[i, i]))
        for j in range(i + 1, n):
            if qubo_matrix[i, j] != 0:
                pauli_string[i] = "Z"
                pauli_string[j] = "Z"
                terms.append(("".join(pauli_string), qubo_matrix[i, j]))
                pauli_string[j] = "I"  # Reset to original state
    return SparsePauliOp.from_list(terms)

# Step 2: Construct QAOA Circuit
def construct_qaoa_circuit(hamiltonian, p):
    """
    Construct a parameterized QAOA circuit.

    Parameters:
        hamiltonian (SparsePauliOp): Cost Hamiltonian.
        p (int): Number of QAOA layers.

    Returns:
        QuantumCircuit: QAOA circuit.
        List[Parameter]: Parameters for the circuit.
    """
    num_qubits = hamiltonian.num_qubits
    beta = [Parameter(f"beta_{i}") for i in range(p)]
    gamma = [Parameter(f"gamma_{i}") for i in range(p)]

    circuit = QuantumCircuit(num_qubits)
    circuit.h(range(num_qubits))
    
    for layer in range(p):
        # Apply cost Hamiltonian
        for pauli_term, coeff in zip(hamiltonian.paulis, hamiltonian.coeffs):
            indices = [i for i, op in enumerate(pauli_term.to_label()) if op == "Z"]            
            if len(indices) == 1:
                circuit.rz(2 * gamma[layer] * coeff, indices[0])
            elif len(indices) == 2:
                circuit.cx(indices[0], indices[1])
                circuit.rz(2 * gamma[layer] * coeff, indices[1])
                circuit.cx(indices[0], indices[1])

        # Apply mixer Hamiltonian
        for qubit in range(num_qubits):
            circuit.rx(2 * beta[layer], qubit)

    return circuit, beta + gamma

# Step 3: Optimize Circuit Parameters
def optimize_qaoa(hamiltonian, circuit, parameters):
    """
    Optimize the QAOA circuit parameters to minimize the cost function.

    Parameters:
        hamiltonian (SparsePauliOp): Cost Hamiltonian.
        circuit (QuantumCircuit): QAOA circuit.
        parameters (List[Parameter]): Circuit parameters.

    Returns:
        dict: Optimal parameters and cost value.
    """
    estimator = EstimatorV2()

    def cost_function(params):
        pub = (circuit, hamiltonian, [params])
        result = estimator.run([pub]).result()
        cost = result[0].data.evs[0]
        return cost

    initial_params = np.random.uniform(0, 2 * np.pi, len(parameters))
    result = minimize(cost_function, initial_params, method="COBYLA")

    return {
        "optimal_params": result.x,
        "optimal_value": result.fun
    }

# Step 4: Simulate the Circuit and Extract Solution
def simulate_qaoa(circuit, parameters, backend=None, shots=1024):
    """
    Simulate the QAOA circuit and extract the solution bitstring.

    Parameters:
        circuit (QuantumCircuit): QAOA circuit.
        parameters (dict): Optimized parameters.
        backend (AerSimulator): Aer simulator backend.
        shots (int): Number of shots for the simulation.

    Returns:
        dict: Measurement results and the most probable bitstring.
    """
    if backend is None:
        backend = AerSimulator()

    bound_circuit = circuit.assign_parameters(parameters, inplace=False)
    bound_circuit.measure_all()

    transpiled_circuit = transpile(bound_circuit, backend)
    job = backend.run(transpiled_circuit, shots=shots)
    result = job.result()
    counts = result.get_counts()

    most_probable_bitstring = max(counts, key=counts.get)

    return {
        "counts": counts,
        "most_probable_bitstring": most_probable_bitstring
    }

# Step 5: Validation and Testing
def validate_solution(bitstring, graph):
    """
    Validate if the solution covers all edges in the graph.

    Parameters:
        bitstring (str): The bitstring representing the solution.
        graph (networkx.Graph): The input graph.

    Returns:
        bool: True if all edges are covered, False otherwise.
    """
    included_vertices = {i for i, bit in enumerate(bitstring) if bit == "1"}
    for u, v in graph.edges():
        if u not in included_vertices and v not in included_vertices:
            return False
    return True

# Example Workflow
def example_workflow():
    # Define a simple graph
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])

    # Convert graph to QUBO matrix
    qubo_matrix = np.array([
        [2, -1, -1],
        [-1, 2, -1],
        [-1, -1, 2]
    ])

    # Generate Hamiltonian and QAOA circuit
    hamiltonian = qubo_to_hamiltonian(qubo_matrix)
    circuit, parameters = construct_qaoa_circuit(hamiltonian, p=1)

    # Optimize parameters
    optimization_result = optimize_qaoa(hamiltonian, circuit, parameters)

    # Simulate QAOA and extract solution
    simulation_result = simulate_qaoa(
        circuit,
        {param: value for param, value in zip(parameters, optimization_result["optimal_params"])}
    )

    # Validate solution
    is_valid = validate_solution(simulation_result["most_probable_bitstring"], G)

    # Plot measurement results
    plot_histogram(simulation_result["counts"])
    plt.show()

    print("Most Probable Bitstring:", simulation_result["most_probable_bitstring"])
    print("Measurement Counts:", simulation_result["counts"])
    print("Is the solution valid?:", is_valid)

if __name__ == "__main__":
    example_workflow()
