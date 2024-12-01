####
#### OBS: Replace "your_quantum_ibm_api_token" with the API Token associated with your account at quantum.ibm.com 
####

#Define the circuit
from qiskit import QuantumCircuit
def generalized_GHZ_state(n):
    circuit = QuantumCircuit (n,n)
    # Apply the Hadamard gate at qubit 0
    circuit . h (0)
    circuit.barrier() # draw a barrier
    # Apply CNOT Gates
    for i in range (n -1):
        circuit.cx(i,i +1)
    circuit.barrier() # draw a barrier
    measured_qubits =[i for i in range (n)]
    classical_results =[ i for i in range (n)]
    circuit.measure(measured_qubits, classical_results)
    return circuit

n = 4
circuit = generalized_GHZ_state(n)
print (circuit)

#Simulation Using IBM Hardware
#The code below is generic and can be used with other quantum circuits with a small number of qubits. 

#Set up the service
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2 as Sampler
service = QiskitRuntimeService(channel="ibm_quantum",token="your_quantum_ibm_api_token")
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


