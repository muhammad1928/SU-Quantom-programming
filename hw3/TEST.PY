from qiskit import QuantumCircuit

class ClassicalCircuit:
    def __init__(self, filename):
        self.n_inputs = 0
        self.n_outputs = 0
        self.n_internal = 0
        self.input_gates = []  # list with n_inputs numbers indicating which are the input gates
        self.output_gates = []  # list with n_outputs numbers indicating which are the output gates
        self.internal_gates = []  # list with n_internal numbers indicating which are the internal gates
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
        print("Gates: ")  # reads n_outputs + n_internal
        for gate in self.gates:
            print(gate)
        print()

    def convert_step_1(self, quantumCircuit):
        for gate in self.gates:
            gate_index = gate[0]
            if gate[1] == "and":
                quantumCircuit.ccx(gate[2], gate[3], gate_index)
            elif gate[1] == "or":
                quantumCircuit.x(gate[2])
                quantumCircuit.x(gate[3])
                quantumCircuit.ccx(gate[2], gate[3], gate_index)
                quantumCircuit.x(gate[2])
                quantumCircuit.x(gate[3])
            elif gate[1] == "xor":
                quantumCircuit.cx(gate[2], gate[3])
                quantumCircuit.cx(gate[3], gate_index)
                quantumCircuit.cx(gate[2], gate_index)
            elif gate[1] == "nand":
                quantumCircuit.ccx(gate[2], gate[3], gate_index)
                quantumCircuit.x(gate_index)
            elif gate[1] == "not":
                quantumCircuit.x(gate_index)

    def convert_step_2(self, quantumCircuit):
        for gate in self.gates:
            gate_index = gate[0]
            if gate[1] == "and":
                quantumCircuit.ccx(gate[2], gate[3], gate_index)
            elif gate[1] == "or":
                quantumCircuit.x(gate[2])
                quantumCircuit.x(gate[3])
                quantumCircuit.ccx(gate[2], gate[3], gate_index)
                quantumCircuit.x(gate[2])
                quantumCircuit.x(gate[3])
            elif gate[1] == "xor":
                quantumCircuit.cx(gate[2], gate[3])
                quantumCircuit.cx(gate[3], gate_index)
                quantumCircuit.cx(gate[2], gate_index)
            elif gate[1] == "nand":
                quantumCircuit.ccx(gate[2], gate[3], gate_index)
                quantumCircuit.x(gate_index)
            elif gate[1] == "not":
                quantumCircuit.x(gate_index)

        for output_gate in self.output_gates:
            quantumCircuit.cx(output_gate, output_gate + self.n_outputs)

    def convert(self, quantumCircuit):
        for gate in self.gates:
            gate_index = gate[0]
            if gate[1] == "and":
                quantumCircuit.ccx(gate[2], gate[3], gate_index)
            elif gate[1] == "or":
                quantumCircuit.x(gate[2])
                quantumCircuit.x(gate[3])
                quantumCircuit.ccx(gate[2], gate[3], gate_index)
                quantumCircuit.x(gate[2])
                quantumCircuit.x(gate[3])
            elif gate[1] == "xor":
                quantumCircuit.cx(gate[2], gate[3])
                quantumCircuit.cx(gate[3], gate_index)
                quantumCircuit.cx(gate[2], gate_index)
            elif gate[1] == "nand":
                quantumCircuit.ccx(gate[2], gate[3], gate_index)
                quantumCircuit.x(gate_index)
            elif gate[1] == "not":
                quantumCircuit.x(gate_index)

        for output_gate in self.output_gates:
            quantumCircuit.cx(output_gate, output_gate + self.n_outputs)
        for output_gate in self.output_gates:
            quantumCircuit.measure(output_gate + self.n_outputs, output_gate)

# Initialize the ClassicalCircuit from a file and perform conversions
cc = ClassicalCircuit("circuit.txt")
cc.print()

n_wires = cc.n_inputs + cc.n_outputs + cc.n_internal
qc = QuantumCircuit(n_wires, 0)
cc.convert_step_1(qc)
print(qc)
print()

n_wires = cc.n_inputs + cc.n_outputs + cc.n_internal
qc = QuantumCircuit(n_wires, 0)
cc.convert_step_2(qc)
print(qc)
print()

n_wires = cc.n_inputs + 2 * cc.n_outputs + cc.n_internal
qc = QuantumCircuit(n_wires, cc.n_outputs)
cc.convert(qc)
print(qc)
print()
