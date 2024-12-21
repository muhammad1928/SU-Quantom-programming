import numpy as np
from qiskit import QuantumCircuit

# Quantum Fourier Transform (QFT) Functions
def qft(circuit, n):
    """Applies the Quantum Fourier Transform to the first n qubits in the circuit."""
    for j in range(n):
        circuit.h(j)
        for k in range(j + 1, n):
            circuit.cp(np.pi / (2 ** (k - j)), j, k)
        circuit.barrier()
    for j in range(n // 2):
        circuit.swap(j, n - j - 1)
    return circuit

def inverse_qft(circuit, n):
    """Applies the inverse Quantum Fourier Transform to the first n qubits in the circuit."""
    for j in range(n // 2):
        circuit.swap(j, n - j - 1)
    for j in range(n - 1, -1, -1):
        for k in range(n - 1, j, -1):
            circuit.cp(-np.pi / (2 ** (k - j)), j, k)
        circuit.h(j)
        circuit.barrier()
    return circuit

# Generalized QFT Functions
def qft_on_qubits(circuit, qubits):
    """Applies the QFT to a specified list of qubits in the circuit."""
    n = len(qubits)
    for j in range(n):
        circuit.h(qubits[j])
        for k in range(j + 1, n):
            circuit.cp(np.pi / (2 ** (k - j)), qubits[j], qubits[k])
        circuit.barrier()
    for j in range(n // 2):
        circuit.swap(qubits[j], qubits[n - j - 1])
    return circuit

def inverse_qft_on_qubits(circuit, qubits):
    """Applies the inverse QFT to a specified list of qubits in the circuit."""
    n = len(qubits)
    for j in range(n // 2):
        circuit.swap(qubits[j], qubits[n - j - 1])
    for j in range(n - 1, -1, -1):
        for k in range(n - 1, j, -1):
            circuit.cp(-np.pi / (2 ** (k - j)), qubits[j], qubits[k])
        circuit.h(qubits[j])
        circuit.barrier()
    return circuit

# Classical to Quantum Circuit Conversion Class
class ClassicalCircuit:
    def __init__(self, filename):
        self.n_inputs = 0
        self.n_outputs = 0
        self.n_internal = 0
        self.gates = []  # List of gate instructions
        self._read_file(filename)

    def _read_file(self, filename):
        """Reads and parses the classical circuit file."""
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()

            self.n_inputs = int(lines[0].strip())
            self.n_outputs = int(lines[1].strip())
            self.n_internal = int(lines[2].strip())

            for line in lines[6:]:
                parts = line.strip().split()
                if parts:
                    self.gates.append(parts)
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File '{filename}' not found.")
        except (ValueError, IndexError):
            raise ValueError("Error: Invalid circuit file format.")

    def convert_step_1(self, quantum_circuit):
        """Converts classical logic gates to quantum gates (first step)."""
        for gate in self.gates:
            self._apply_gate(quantum_circuit, gate, reverse=False)

    def convert_step_2(self, quantum_circuit):
        """Converts classical logic gates to quantum gates (reverse step)."""
        for gate in reversed(self.gates):
            self._apply_gate(quantum_circuit, gate, reverse=True)

    def convert(self, quantum_circuit):
        """Performs the complete conversion of the classical circuit to a quantum circuit."""
        self.convert_step_1(quantum_circuit)
        self.convert_step_2(quantum_circuit)

    def _apply_gate(self, quantum_circuit, gate, reverse):
        """Applies a quantum gate based on the classical gate description."""
        try:
            target_qubit = int(gate[0])
            gate_type = gate[1]

            if gate_type == 'and':
                control_qubit1 = int(gate[2])
                control_qubit2 = int(gate[3])
                quantum_circuit.ccx(control_qubit1, control_qubit2, target_qubit)

            elif gate_type == 'not':
                control_qubit = int(gate[2])
                if reverse:
                    quantum_circuit.cx(control_qubit, target_qubit)
                    quantum_circuit.x(target_qubit)
                else:
                    quantum_circuit.x(target_qubit)
                    quantum_circuit.cx(control_qubit, target_qubit)

            elif gate_type in {'or', 'xor', 'nand'}:
                print(f"Gate '{gate_type}' not implemented: {gate}")

        except (ValueError, IndexError):
            print(f"Error processing gate: {gate}")

# Example usage
cc = ClassicalCircuit("circuit.txt")
n_wires = cc.n_inputs + cc.n_outputs + cc.n_internal
quantum_circuit = QuantumCircuit(n_wires)

cc.convert(quantum_circuit)
print(quantum_circuit)
