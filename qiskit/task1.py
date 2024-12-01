# task 1

from qiskit import QuantumCircuit

def inner_product(circuit, a):
    """
    Adds CNOT gates to the circuit to compute the inner product modulo 2.
    Parameters:
        circuit (QuantumCircuit): The quantum circuit.
        a (str): A binary string representing the secret.
    """
    n = len(a)
    for i, bit in enumerate(reversed(a)):
        if bit == '1':
            circuit.cx(i, n)  # Control qubit is `i`, target qubit is `n`
    circuit.barrier()  # Separate the inner product block

# Test the function
a = "01101"
n = len(a)
circuit = QuantumCircuit(n + 1, 0)
inner_product(circuit, a)
print(circuit)


# task 2

from qiskit import QuantumCircuit

def hadamards(circuit):
    # Get the number of qubits in the circuit
    num_qubits = circuit.num_qubits
    
    # Apply Hadamard gate to each qubit
    for qubit in range(num_qubits):
        circuit.h(qubit)
    
    # Optionally, add a barrier for visual clarity
    circuit.barrier()

# Example usage:
circuit = QuantumCircuit(5, 0)  # Create a quantum circuit with 5 qubits and 0 classical bits
hadamards(circuit)  # Apply Hadamard gates to each qubit
print(circuit)


# task 3

from qiskit import QuantumCircuit

# Assuming the functions 'inner_product' and 'hadamards' are already defined

def bernstein_vazirani(a):
    n = len(a)
    # Create a quantum circuit with n+1 qubits and n classical bits
    circuit = QuantumCircuit(n + 1, n)
    
    # Step 3: Apply the X gate to the output qubit (the last qubit)
    circuit.x(n)  # Apply X to the (n+1)th qubit
    
    # Step 4: Apply a layer of Hadamard gates to all qubits
    hadamards(circuit)
    
    # Step 5: Apply the inner product circuit with respect to a
    inner_product(circuit, a)
    
    # Step 6: Apply another layer of Hadamard gates to all qubits
    hadamards(circuit)
    
    # Step 7: Measure the n input qubits and store the result in classical bits
    circuit.measure(range(n), range(n))
    
    # Step 8: Return the quantum circuit
    return circuit

# Example usage:
a = "01101"
circuit = bernstein_vazirani(a)
print(circuit)


# task 4
from qiskit import QuantumCircuit, transpile
from qiskit.providers.basic_provider import BasicSimulator


# Step 4: Simulate the circuit using BasicSimulator
def simulate_circuit(a):
    # Create the Bernstein-Vazirani circuit
    circuit = bernstein_vazirani(a)
    
    # Use BasicSimulator from BasicAer
    backend = BasicSimulator()
    
    # Execute the circuit
    n_shots = 1024
    result = backend.run(circuit, shots=n_shots).result()
    
    # Get the counts of the measured outcomes
    counts = result.get_counts(circuit)
    prob = {key:value/n_shots for key,value in counts.items()}
    
    # Print the counts, expecting the result to be the binary string a with high probability
    print("Measurement results:", counts)
    print("Probabilities: ", prob)


# Example usage:
a = "01101"  # Example secret string
simulate_circuit(a)
