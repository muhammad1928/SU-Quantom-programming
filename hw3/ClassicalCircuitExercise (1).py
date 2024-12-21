import numpy as np
from qiskit import QuantumCircuit

class ClassicalCircuit:
    def __init__(self,filename):
        self.n_inputs = 0
        self.n_outputs = 0
        self.n_internal = 0
        self.input_gates = [] # list with n_inputs numbers indicating which are the input gates
        self.output_gates = [] # list with n_outputs numbers indicating which are the output gates
        self.internal_gates = [] # list with n_internal numbers indicating which are the internal gates
        self.gates = []
        self.read(filename)
    
    def read(self,filename):
        with open(filename,'r') as file:
            lines = file.readlines()
        self.n_inputs = int(lines[0].strip())
        self.n_outputs = int(lines[1].strip())
        self.n_internal = int(lines[2].strip())
        self.input_gates = list(map(int,lines[3].strip().split()))
        self.output_gates = list(map(int,lines[4].strip().split()))
        self.internal_gates = list(map(int,lines[5].strip().split()))
        for line in lines[6:]:
            gate = line.strip().split()
            gate[0] = int(gate[0])
            if gate[1] == "and" or gate[1] == "or" or gate[1] == "xor" or gate[1]=="nand":
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
        print("Gates: ") # reads n_outputs + n_internal
        for gate in self.gates:
            print(gate)
        print()

    # Forward pass: Apply classical gates as quantum gates with proper logic and dynamic dependencies.
    def convert_step_1(self,quantumCircuit):

        for gate in self.gates:
            # The target qubit
            target = gate[0]  
            # The type of gate (e.g., 'and', 'not')
            gate_type = gate[1] 
            # The operand qubits 
            operands = gate[2:]  

            # Apply Toffoli (CCNOT) gate for AND operation
            if gate_type == 'and':
                quantumCircuit.ccx(operands[0], operands[1], target)

            # Apply X gate for NOT operation
            elif gate_type == 'not':
                # Apply CNOT where target influences the operand
                quantumCircuit.x(target)
                if operands:
                    quantumCircuit.cx(operands[0], target)
            # Apply CNOT gate for XOR operation
            elif gate_type == 'xor':

                quantumCircuit.cx(operands[0], target)

            # OR gate implemented using Toffoli and auxiliary X gates
            elif gate_type == 'or':
                # Invert the first operand
                quantumCircuit.x(operands[0]) 
                # Invert the second operand
                quantumCircuit.x(operands[1])  
                quantumCircuit.ccx(operands[0], operands[1], target)
                # Revert the first operand
                quantumCircuit.x(operands[0]) 
                # Revert the second operand
                quantumCircuit.x(operands[1])  

            elif gate_type == 'nand':
                # NAND gate is AND followed by NOT
                quantumCircuit.ccx(operands[0], operands[1], target)
                quantumCircuit.x(target)

            # Add a barrier for clarity after each gate
            quantumCircuit.barrier()



    # Reverse pass: Undo gates in reverse order to restore auxiliary qubits to their original state.
    def convert_step_2(self,quantumCircuit):
        for idx, gate in enumerate(reversed(self.gates)):
            # The target qubit
            target = gate[0]  
            # The type of gate (e.g., 'and', 'not')
            gate_type = gate[1]  
            # The operand qubits
            operands = gate[2:]  
            # Undo Toffoli (CCNOT) gate for AND operation
            if gate_type == 'and':
                
                quantumCircuit.ccx(operands[0], operands[1], target)
            # Undo NOT with dependency
            elif gate_type == 'not':
                
                if operands:
                    # Undo CNOT where target influenced the operand
                    quantumCircuit.cx(operands[0], target)
                quantumCircuit.x(target)  # Undo X gate to the target

            elif gate_type == 'xor':
                # Undo CNOT for XOR operation
                quantumCircuit.cx(target, operands[0])
            # Undo OR operation using Toffoli and auxiliary X gates
            elif gate_type == 'or':

                # Revert the first operand
                quantumCircuit.x(operands[0]) 
                # Revert the second operand 
                quantumCircuit.x(operands[1])  
                quantumCircuit.ccx(operands[0], operands[1], target)
                # Invert the first operand
                quantumCircuit.x(operands[0]) 
                # Invert the second operand 
                quantumCircuit.x(operands[1])  
            # Undo NAND (NOT followed by AND)
            elif gate_type == 'nand':
                # Undo NOT
                quantumCircuit.x(target)  
                # Undo AND
                quantumCircuit.ccx(operands[0], operands[1], target)  

            # Add a barrier for clarity after each reversed gate
            quantumCircuit.barrier()

    # Step 1: Apply gates in forward order
    def convert(self,quantumCircuit):
             
        self.convert_step_1(quantumCircuit)

        # Step 2: Copy outputs to separate qubits
        for i, output in enumerate(self.output_gates):
            target_qubit = self.n_inputs + self.n_internal + i + 2
            quantumCircuit.cx(output, target_qubit)
        
        quantumCircuit.barrier()

        # Step 3: Undo gates in reverse order
        self.convert_step_2(quantumCircuit)


    def convert_contr_step_1(self, quantum_circuit, control_qubit):
        # Forward pass with controlled gates.
        for gate in self.gates:
            # The target qubit
            target = gate[0]  
            # The type of gate (e.g., 'and', 'not')
            gate_type = gate[1] 
            # The operand qubits 
            operands = gate[2:]  

            if gate_type == 'and':
                # Apply controlled Toffoli (multi-controlled Toffoli)
                quantum_circuit.mcx([control_qubit, operands[0], operands[1]], target)
            elif gate_type == 'not':
                # Apply controlled NOT
                quantum_circuit.cx(control_qubit, target)
            
            # Add a barrier for clarity
            quantum_circuit.barrier()


    # Reverse pass with controlled gates.
    def convert_contr_step_2(self, quantum_circuit, control_qubit):
        for gate in reversed(self.gates):
            # The target qubit
            target = gate[0]  
            # The type of gate (e.g., 'and', 'not')
            gate_type = gate[1] 
            # The operand qubits 
            operands = gate[2:]  

            if gate_type == 'and':
                # Undo controlled Toffoli (multi-controlled Toffoli)
                quantum_circuit.mcx([control_qubit, operands[0], operands[1]], target)

            elif gate_type == 'not':
                # Undo controlled NOT
                quantum_circuit.cx(control_qubit, target)
    
    # Full conversion with controlled gates
    def convert_contr(self, quantum_circuit, control_qubit):
        # Controlled forward pass
        self.convert_contr_step_1(quantum_circuit, control_qubit)

        # Copy output to fresh qubits
        for i, output in enumerate(self.output_gates):
            fresh_qubit = self.n_inputs + self.n_internal + i
            quantum_circuit.cx(output, fresh_qubit)

        # Controlled reverse pass
        self.convert_contr_step_2(quantum_circuit, control_qubit)

    
cc = ClassicalCircuit("circuit.txt")
cc.print()

n_wires = cc.n_inputs + cc.n_outputs + cc.n_internal
qc = QuantumCircuit(n_wires,0)
cc.convert_step_1(qc)
print(qc)
print()

n_wires = cc.n_inputs + cc.n_outputs + cc.n_internal
qc = QuantumCircuit(n_wires,0)
cc.convert_step_2(qc)
print(qc)
print()

n_wires = cc.n_inputs + 2*cc.n_outputs + cc.n_internal
qc = QuantumCircuit(n_wires,0)
cc.convert(qc)
print(qc)
print()

