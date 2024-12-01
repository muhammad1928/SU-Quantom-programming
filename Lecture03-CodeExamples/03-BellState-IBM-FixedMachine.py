####
#### OBS: Replace "your_quantum_ibm_api_token" with the API Token associated with your account at quantum.ibm.com 
####
f = open("apitoken.txt", "r")
apiToken = f.read()

from qiskit import QuantumCircuit
circuit = QuantumCircuit(2, 2) # 2 quantum qubits (first argument) and 2 classical bits (second argument)
circuit.h(0)        # Apply a Hadamard gate to qubit 0
circuit.cx(0, 1)    # Apply a CNOT gate with qubit 0 as control and qubit 1 as target
circuit.measure([0, 1], [0, 1])  # Measure qubit 0 and 1 and store results in classical bits 0 and 1 respectively.
print(circuit) # Print the circuit

#Simulation Using IBM Hardware
#The code below is generic and can be used with other quantum circuits with a small number of qubits. 

#Set up the service
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2 as Sampler
service = QiskitRuntimeService(channel="ibm_quantum",token=str(apiToken))
#Select a specific quantum computer
backend = service.backend("ibm_kyiv")
#To select the least busy option, comment the line above and uncomment the line below.
#backend = service.least_busy(simulator=False,operational=True)

# Transpile the circuit
from qiskit import transpile 
transpiled_circuit = transpile(circuit,backend)
#print(transpiled_circuit)

#Sample
sampler = Sampler(mode=backend)
n_shots = 1024
sampler.options.default_shots = n_shots
result = sampler.run([transpiled_circuit]).result()

# Extract Information (counts and probability distribution) 
counts = result[0].data.c.get_counts() # Use this line if you use the measure method passing register numbers.
#counts = result[0].data.meas.get_counts() # Use this line if you use the method measure_all()
probs = {key:value/n_shots for key,value in counts.items()}
print("Counts:", counts)
print("Probs: ", probs)
print()


