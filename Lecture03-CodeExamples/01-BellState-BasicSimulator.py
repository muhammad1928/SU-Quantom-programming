#Define the circuit
from qiskit import QuantumCircuit
circuit = QuantumCircuit(2, 2) # 2 quantum qubits (first argument) and 2 classical bits (second argument)
circuit.h(0)        # Apply a Hadamard gate to qubit 0
circuit.cx(0, 1)    # Apply a CNOT gate with qubit 0 as control and qubit 1 as target
circuit.measure([0, 1], [0, 1])  # Measure qubit 0 and 1 and store results in classical bits 0 and 1 respectively.
print(circuit) # Print the circuit


# Simulation using BasicSimulator()
#The code below is generic and can be used with other quantum circuits with a small number of qubits. 

#Define the backend
from qiskit.providers.basic_provider import BasicSimulator
backend = BasicSimulator() # Define the backend

#Execute the circuit in the simulator 
n_shots = 1024 # The default number of shots is 1024. 
result = backend.run(circuit, shots=n_shots).result()   

# Extract information. Counts and probability distribution. 
counts = result.get_counts()
prob = {key:value/n_shots for key,value in counts.items()}
print("Counts: ", counts) 
print("Probabilities: ", prob)       
