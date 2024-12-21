from qiskit import QuantumCircuit

class ClassicalCircuit:
    def __init__(self, filename):
        self.n_inputs = 0
        self.n_outputs = 0
        self.n_internal = 0
        self.input_gates = []
        self.output_gates = []
        self.internal_gates = []
        self.gates = []
        self.read(filename)

    def read(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
        self.n_inputs = int(lines[0].strip())
        self.n_outputs = int(lines[1].strip())
        self.n_internal = int(lines[2].strip())
        self.input_gates = list(map(int, lines[3].strip().split()))
        self.output_gates = list(map(int, lines[4].strip().split()))
        self.internal_gates = list(map(int, lines[5].strip().split()))
        for line in lines[6:]:
            gate = line.strip().split()
            gate[0] = int(gate[0])
            if gate[1] in ["and", "or", "xor", "nand"]:
                gate[2] = int(gate[2])
                gate[3] = int(gate[3])
            elif gate[1] == "not":
                gate[2] = int(gate[2])
            self.gates.append(gate)

    def print(self):
        print(f"n_inputs: {self.n_inputs}")
        print(f"n_outputs: {self.n_outputs}")
        print(f"n_internal: {self.n_internal}")
        print(f"Input Gates: {self.input_gates}")
        print(f"Output Gates: {self.output_gates}")
        print(f"Internal Gates: {self.internal_gates}")
        print("Gates: ")
        for gate in self.gates:
            print(gate)
        print()

    def convert_step_1(self, quantumCircuit):
        for gate in self.gates:
            self._apply_gate(quantumCircuit, gate)

    def convert_step_2(self, quantumCircuit):
        for gate in reversed(self.gates):
            self._apply_gate(quantumCircuit, gate)

    def convert(self, quantumCircuit):
        self.convert_step_1(quantumCircuit)
        for i, output_gate in enumerate(self.output_gates):
            output_index = self.n_inputs + self.n_internal + i
            quantumCircuit.cx(output_gate, output_index)
        self.convert_step_2(quantumCircuit)

    def _apply_gate(self, quantumCircuit, gate):
        gate_index, gate_type, *qubits = gate
        if gate_type == "and":
            quantumCircuit.ccx(qubits[0], qubits[1], gate_index)
        elif gate_type == "not":
            quantumCircuit.cx(qubits[0], gate_index)

# Initialize the circuit with the given file
filename = "circuit.txt"
cc = ClassicalCircuit(filename)

# Print the details of the circuit
cc.print()

# Generate the quantum circuits for each step
n_wires = cc.n_inputs + cc.n_outputs + cc.n_internal

# Step 1 Circuit
qc_step_1 = QuantumCircuit(n_wires, 0)
cc.convert_step_1(qc_step_1)
print("Step 1 Quantum Circuit:")
print(qc_step_1.draw())

# Step 2 Circuit
qc_step_2 = QuantumCircuit(n_wires, 0)
cc.convert_step_2(qc_step_2)
print("Step 2 Quantum Circuit:")
print(qc_step_2.draw())

# Full Conversion Circuit
n_wires_full = cc.n_inputs + 2 * cc.n_outputs + cc.n_internal
qc_full = QuantumCircuit(n_wires_full, 0)
cc.convert(qc_full)
print("Full Conversion Quantum Circuit:")
print(qc_full.draw())
