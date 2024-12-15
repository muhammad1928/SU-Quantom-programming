from qiskit import QuantumCircuit
import numpy as np

def apply_qft(n, circuit):
    """
    Applies the Quantum Fourier Transform (QFT) to the first n qubits of the circuit.
    Args:
        n (int): Number of qubits to apply QFT on.
        circuit (QuantumCircuit): The quantum circuit to modify.
    """
    circuit.barrier()
    for j in range(n - 1, -1, -1):  # Iterate from n-1 to 0
        circuit.h(j)  # Apply Hadamard gate to qubit j
        for k in range(j - 1, -1, -1):  # Apply controlled phase gates
            angle = np.pi / (2 ** (j - k))
            circuit.cp(angle, k, j)
        circuit.barrier()
    # Reverse the order of qubits with swaps
    for i in range(n // 2):
        circuit.swap(i, n - i - 1)

def apply_iqft(n, circuit):
    """
    Applies the Inverse Quantum Fourier Transform (IQFT) to the first n qubits of the circuit.
    Args:
        n (int): Number of qubits to apply IQFT on.
        circuit (QuantumCircuit): The quantum circuit to modify.
    """
    # Reverse the order of qubits with swaps
    for i in range(n // 2 - 1, -1, -1):
        circuit.swap(i, n - i - 1)
    circuit.barrier()
    for j in range(n):  # Iterate from 0 to n-1
        for k in range(j):
            angle = -np.pi / (2 ** (j - k))
            circuit.cp(angle, k, j)  # Apply inverse controlled phase gate
        circuit.h(j)  # Apply Hadamard gate to qubit j
        circuit.barrier()

def apply_qft_gen(qubits, circuit):
    """
    Generalized QFT to apply to a specific list of qubits.
    Args:
        qubits (list[int]): List of qubit indices to apply QFT on.
        circuit (QuantumCircuit): The quantum circuit to modify.
    """
    n = len(qubits)
    circuit.barrier()
    for j in range(n - 1, -1, -1):
        circuit.h(qubits[j])  # Apply Hadamard gate to the j-th qubit
        for k in range(j - 1, -1, -1):  # Apply controlled phase gates
            angle = np.pi / (2 ** (j - k))
            circuit.cp(angle, qubits[k], qubits[j])
        circuit.barrier()
    for i in range(n // 2):
        circuit.swap(qubits[i], qubits[n - i - 1])

def apply_iqft_gen(qubits, circuit):
    """
    Generalized IQFT to apply to a specific list of qubits.
    Args:
        qubits (list[int]): List of qubit indices to apply IQFT on.
        circuit (QuantumCircuit): The quantum circuit to modify.
    """
    n = len(qubits)
    for i in range(n // 2):
        circuit.swap(qubits[i], qubits[n - i - 1])
    circuit.barrier()
    for j in range(n):
        for k in range(j):
            angle = -np.pi / (2 ** (j - k))
            circuit.cp(angle, qubits[k], qubits[j])  # Apply inverse controlled phase gate
        circuit.h(qubits[j])  # Apply Hadamard gate to the j-th qubit
        circuit.barrier()


# Example 1: QFT on 3 qubits
n = 3
qc = QuantumCircuit(n, 0)
apply_qft(n, qc)
print ( qc )
print ()

# Example 2: Generalized QFT on specific qubits
qc = QuantumCircuit(5, 0)
apply_qft_gen([0, 2, 4], qc)
print ( qc )
print ()

# Example 3: IQFT on 4 qubits
n = 4
qc = QuantumCircuit(n, 0)
apply_iqft(n, qc)
print ( qc )
print ()

# Example 4: Generalized IQFT on specific qubits
qc = QuantumCircuit(5, 0)
apply_iqft_gen([0, 1, 3], qc)
print ( qc )
print ()