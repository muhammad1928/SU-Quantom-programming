#circuit_constructor.py
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
import hamiltonian as hmltn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


def apply_single_qubit_term(circuit, parameter, coeff, qubit):
    """
    Apply a single-qubit Z term to the circuit.
    """
    circuit.rz(2 * parameter * coeff, qubit)

def apply_two_qubit_term(circuit, parameter, coeff, qubits):
    """
    Apply a two-qubit ZZ term to the circuit.
    """
    circuit.cx(qubits[0], qubits[1])
    circuit.rz(2 * parameter * coeff, qubits[1])
    circuit.cx(qubits[0], qubits[1])

def apply_cost_terms_optimized(circuit, hamiltonian, parameters, layer):
    """
    Optimized application of cost Hamiltonian terms to the circuit.
    """
    logging.info(f"Applying cost terms for layer {layer + 1}")
    for pauli_term, coeff in zip(hamiltonian.paulis, hamiltonian.coeffs):
        indices = [i for i, op in enumerate(pauli_term.to_label()) if op == "Z"]
        if len(indices) == 1:
            apply_single_qubit_term(circuit, parameters[layer], coeff, indices[0])
        elif len(indices) == 2:
            apply_two_qubit_term(circuit, parameters[layer], coeff, indices)

def apply_dynamic_mixer(circuit, parameters, layer, mixer_type="default", custom_mixer=None):
    """
    Apply a dynamic mixer Hamiltonian to the circuit.
    """
    logging.info(f"Applying {mixer_type} mixer for layer {layer + 1}")
    if mixer_type == "default":
        for qubit in range(circuit.num_qubits):
            circuit.rx(2 * parameters[layer], qubit)
    elif mixer_type == "xy":
        for i in range(circuit.num_qubits - 1):
            circuit.rxx(2 * parameters[layer], i, i + 1)
    elif mixer_type == "custom" and custom_mixer:
        custom_mixer(circuit, parameters[layer])
    else:
        raise ValueError(f"Unsupported mixer type: {mixer_type}")

def construct_qaoa_circuit_optimized(hamiltonian, p, mixer_type="default", custom_mixer=None):
    """
    Construct an optimized parameterized QAOA circuit.
    
    Args:
        hamiltonian (SparsePauliOp): The cost Hamiltonian for the QAOA problem.
        p (int): Number of QAOA layers.
        mixer_type (str): Type of mixer to use ("default", "xy", or "custom").
        custom_mixer (callable, optional): Custom mixer function.

    Returns:
        QuantumCircuit: The constructed QAOA circuit.
        list[Parameter]: Parameters for the circuit.
    """
    if p <= 0:
        raise ValueError("Number of layers (p) must be greater than 0.")

    num_qubits = hamiltonian.num_qubits
    parameters = [Parameter(f"theta_{i}") for i in range(2 * p)]

    # Validate the Hamiltonian
    hmltn.validate_hamiltonian(hamiltonian, num_qubits)

    # Initialize the quantum circuit
    circuit = QuantumCircuit(num_qubits)
    circuit.h(range(num_qubits))  # Apply Hadamard gates to all qubits

    # Build the QAOA layers
    for layer in range(p):
        logging.info(f"Constructing QAOA layer {layer + 1}/{p}")
        apply_cost_terms_optimized(circuit, hamiltonian, parameters[:p], layer)
        apply_dynamic_mixer(circuit, parameters[p:], layer, mixer_type, custom_mixer)
    

    return circuit, parameters
