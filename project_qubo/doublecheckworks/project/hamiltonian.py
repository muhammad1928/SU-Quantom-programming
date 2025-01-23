# hamiltonian.py
from qiskit.quantum_info import SparsePauliOp
import networkx as nx
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def validate_hamiltonian(hamiltonian, num_qubits):
    """
    Validate the Hamiltonian against the circuit's qubit count.
    """
    if hamiltonian.num_qubits != num_qubits:
        raise ValueError(f"Hamiltonian has {hamiltonian.num_qubits} qubits, "
                         f"but the circuit requires {num_qubits} qubits.")

def validate_graph(graph):
    """
    Ensure the input is a valid undirected graph.
    """
    if not isinstance(graph, nx.Graph):
        raise TypeError("Input must be a NetworkX graph.")
    if not nx.is_connected(graph):
        raise ValueError("Graph must be connected.")

def generate_pauli_string(num_qubits, indices):
    """
    Generate a Pauli string with 'Z' at specified indices.
    """
    return "".join(["Z" if i in indices else "I" for i in range(num_qubits)])

def qubo_to_hamiltonian(qubo_matrix, alpha=0):
    """
    Convert a QUBO matrix into a cost Hamiltonian for QAOA.
    """
    logging.info(f"Converting QUBO matrix of shape {qubo_matrix.shape} to Hamiltonian.")
    
    if not isinstance(qubo_matrix, np.ndarray):
        raise TypeError("Input must be a numpy.ndarray.")
    if qubo_matrix.shape[0] != qubo_matrix.shape[1]:
        raise ValueError("QUBO matrix must be square.")
    if not np.allclose(qubo_matrix, qubo_matrix.T):
        raise ValueError("QUBO matrix must be symmetric.")

    num_qubits = qubo_matrix.shape[0]
    terms = []

    for i in range(num_qubits):
        terms.append((generate_pauli_string(num_qubits, [i]), qubo_matrix[i, i]))

        for j in range(i + 1, num_qubits):
            if qubo_matrix[i, j] != 0:
                terms.append((generate_pauli_string(num_qubits, [i, j]), qubo_matrix[i, j]))

    hamiltonian = SparsePauliOp.from_list(terms)

    if alpha > 0:
        additional_terms = []
        for i in range(num_qubits):
            for j in range(i + 1, num_qubits):
                if qubo_matrix[i, j] == 0:
                    additional_terms.append((generate_pauli_string(num_qubits, [i, j]), alpha))
        if additional_terms:
            additional_hamiltonian = SparsePauliOp.from_list(additional_terms)
            hamiltonian += additional_hamiltonian

    return hamiltonian

def normalize_qubo(qubo_matrix):
    """
    Normalize QUBO matrix to the range [0, 1].
    """
    logging.info("Normalizing QUBO matrix.")
    qubo_min, qubo_max = qubo_matrix.min(), qubo_matrix.max()
    if qubo_max != qubo_min:
        return (qubo_matrix - qubo_min) / (qubo_max - qubo_min)
    return qubo_matrix

def create_hamiltonian(graph, alpha=0):
    """
    Create a Hamiltonian for the Max-Cut problem with optional additional edges.
    """
    logging.info("Creating Hamiltonian for the Max-Cut problem.")
    validate_graph(graph)

    adjacency_matrix = nx.adjacency_matrix(graph).toarray()
    qubo_matrix = -adjacency_matrix
    np.fill_diagonal(qubo_matrix, -qubo_matrix.sum(axis=1))
    normalized_qubo = normalize_qubo(qubo_matrix)

    return qubo_to_hamiltonian(normalized_qubo, alpha)
