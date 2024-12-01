from qiskit import QuantumCircuit
circuit = QuantumCircuit (3,3)
circuit.h(0)
circuit.cx(0,1)
circuit.cx(1,2)
circuit.measure([0 ,1 ,2],[0 ,1 ,2])
print(circuit)

#Simulation using AerSimulator()
#The code below is generic and can be used with other quantum circuits with a small number of qubits. 
 
#Define the backend
from qiskit_aer import AerSimulator
backend = AerSimulator()

#Transpile 
from qiskit import transpile
compiled_circuit = transpile(circuit, backend)

#Execute the circuit in the simulator
n_shots = 1024 #The default number of shots is 1024 
result = backend.run(compiled_circuit, shots=n_shots).result()

# Extract Information.
counts = result.get_counts(compiled_circuit)
probs = {key:value/n_shots for key,value in counts.items()}
print("Counts",counts)
print("Probabilities:", probs)
print()