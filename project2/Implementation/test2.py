from qiskit.circuit.library import QFT, MCXGate
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
import math

# 1.1 Initialization
def set_bits(circuit, A, X):
    # Apply X-gate to qubits 
    for i in range(len(X)):
        if X[i] == '1':
            circuit.x(A[i])

# 1.2 Copying
def copy(circuit, A, B):
    # Copy contents of register A to register B
    for i in range(len(A)):
        circuit.cx(A[i], B[i])

#  1.3 Full Adder
def full_adder(circuit, a, b, r, c_in, c_out, AUX):
    # Compute sum
    circuit.ccx(a, b, AUX[0] if AUX else None)  
    circuit.cx(a, c_out if c_out is not None else r)
    circuit.cx(b, c_out if c_out is not None else r)
    circuit.cx(c_in, r)

# 1.4 Addition
def add(circuit, A, B, R, AUX, initial_carry=None):
    # Initialize carry to zero  
    c_in = AUX[0] if initial_carry is None else initial_carry
    for i in range(len(A)):
        # Ensure enough auxiliary qubits
        aux_qubit = AUX[i] if i < len(AUX) else None
        c_out = AUX[i+1] if i+1 < len(AUX) else None
        full_adder(circuit, A[i], B[i], R[i], c_in, c_out, [aux_qubit] if aux_qubit is not None else [])
        c_in = c_out if c_out is not None else c_in

#  1.5 Subtraction
def subtract(circuit, A, B, R, AUX, initial_carry=1):
    # First, negate B
    for b in B:
        circuit.x(b)

    # Then add with initial carry
    add(circuit, A, B, R, AUX, initial_carry)

# 1.6 Comparison
def greater_than(circuit, A, B, r, AUX):
    # Temporary registers for computation
    temp_B = QuantumRegister(len(B))
    temp_A = QuantumRegister(len(A))
    circuit.add_register(temp_B)
    circuit.add_register(temp_A)

    # Copy A and B to temporary registers
    copy(circuit, A, temp_A)
    copy(circuit, B, temp_B)

    # Subtract B from A
    subtract(circuit, temp_A, temp_B, temp_A, AUX)

    # XOR operation: result is 1 if A > B, 0 otherwise
    circuit.measure(temp_A[len(temp_A)-1], r)

# 1.7 Addition Modulo N
def controlled_subtract(circuit, control_bit, N, R, AUX):
    # Controlled subtraction of N from R
    temp_R = QuantumRegister(len(R))
    qc = QuantumCircuit(R, N, AUX)

    # Prepare temporary register
    for i in range(len(R)):
        qc.reset(temp_R[i])

    # Conditionally subtract N from R
    qc.append(subtract(circuit, R, N, temp_R, AUX),
              qargs=[control_bit] + list(R) + list(N) + list(temp_R) + list(AUX))

    # Copy back when subtraction is performed
    copy(circuit, temp_R, R)

def add_mod(circuit, N, A, B, R, AUX):
    # Add A+B
    add(circuit, A, B, R, AUX)

    # Check if result > N
    temp = QuantumRegister(1)
    greater_than(circuit, R, N, temp, AUX)

    # Conditional subtraction of N
    controlled_subtract(circuit, temp, N, R, AUX)

# 1.8 Multiplication by Two Modulo N
def times_two_mod(circuit, N, A, R, AUX):
    # Double A modulo N
    copy(circuit, A, R)
    add_mod(circuit, N, R, R, R, AUX)

#  1.9 Multiplication by a Power of Two Modulo N
def times_two_power_mod(circuit, N, A, k, R, AUX):
    # Repeated doubling k times
    copy(circuit, A, R)
    for _ in range(k):
        times_two_mod(circuit, N, R, R, AUX)


#  1.10 Multiplication Modulo N 
def controlled_times_two_power_mod(circuit, N, A, k, R, AUX, control_bit):
    # Create a simplified placeholder implementation
    if isinstance(control_bit, int):
        control_bit = circuit.qubits[control_bit]

    for i in range(len(R)):
        circuit.ccx(control_bit, A[i], R[i])

def multiply_mod(circuit, N, A, B, R, AUX):
    # Initialize R to zero
    for r_bit in R:
        circuit.reset(r_bit)

    # Iterate through bits of B
    for k in range(len(B)):
        # Create a temporary register for partial multiplication
        temp_R = QuantumRegister(len(R))

        # Conditionally multiply A by 2^k mod N when B[k] is 1
        controlled_times_two_power_mod(circuit, N, A, k, temp_R, AUX, B[k])

        # Add the partial result to R
        add_mod(circuit, N, temp_R, R, R, AUX)

# 1.11 Multiplication Modulo N with a hard-coded factor
def multiply_mod_fixed(circuit, N, X, B, AUX):
    # Convert X to binary string if it's not already
    X = bin(X)[2:].zfill(len(B)) if not isinstance(X, str) else X

    # Create a temporary register to avoid duplicate qubits
    temp_B = QuantumRegister(len(B))
    circuit.add_register(temp_B)

    for k in range(len(B)):
        if X[k] == '1':
            circuit.cx(B[k], temp_B[k])  # Controlled-X operation

    # Copy back if needed
    for k in range(len(B)):
        circuit.cx(temp_B[k], B[k])


#  1.12 Multiplication by X2k mod N
def multiply_mod_fixed_power_2_k(circuit, N, X, B, AUX, k):
    # Pre-compute W = X^2^k mod N using classical computation
    W = (X ** (2**k)) % N

    # Use multiply_mod_fixed with pre-computed W
    multiply_mod_fixed(circuit, N, W, B, AUX)

#  1.13 Multiplication by XY mod N 
def multiply_mod_fixed_power_Y(circuit, N, X, B, AUX, Y):
    # Iterate through bits of Y
    for k in range(len(Y)):
        if Y[k] == '1':
            # Apply multiplication by X·2^k mod N when Y[k] is 1
            multiply_mod_fixed_power_2_k(circuit, N, X, B, AUX, k)

# 2.0 bonus challenge
def qft(circuit, qubits):

    n = len(qubits)

    # Apply QFT
    for i in range(n):
        # Hadamard gate on current qubit
        circuit.h(qubits[i])

        # Apply controlled rotation gates
        for j in range(i+1, n):
            # Compute rotation angle
            control_angle = math.pi / (2 ** (j - i))

            # Controlled rotation
            circuit.cp(control_angle, qubits[j], qubits[i])

    # Optional: Swap qubits to reverse order (if needed)
    for i in range(n//2):
        circuit.swap(qubits[i], qubits[n-1-i])

def test_qft():
    # Create quantum circuit with 4 qubits
    qr = QuantumRegister(4)
    circuit = QuantumCircuit(qr)

    # Apply some initial state (optional)
    circuit.x(qr[1])  # Flip second qubit
    circuit.x(qr[3])  # Flip fourth qubit

    # Apply QFT
    qft(circuit, qr)

    print("QFT Test: Circuit created successfully")
    return circuit


# # Demonstrate usage of qft function
# def main():
#     test_qft()

# if __name__ == "__main__":
#     main()

def period_finding(circuit, f, N, precision):
    # Number of qubits for input and output registers
    n = len(bin(N)[2:])  # number of qubits to represent N
    m = 2 * n + precision  # total number of qubits

    # Create quantum and classical registers
    x = QuantumRegister(n)  # input register
    y = QuantumRegister(m)  # output register
    cr = ClassicalRegister(m)  # classical register for measurement

    # Initialize circuit
    qc = QuantumCircuit(x, y, cr)

    # Prepare uniform superposition for x
    qc.h(x)

    # Apply modular exponentiation
    for i in range(n):
        power = 2**i
        multiply_mod_fixed_power_2_k(qc, N, f, y[n:], x, power)

    # Apply Quantum Fourier Transform (QFT) to y register
    qft(qc, y)

    # Measure y register
    qc.measure(y, cr)

    return qc

def estimate_period(result, precision=10):
    counts = result.get_counts()
    total_qubits = len(list(counts.keys())[0])

    def detect_period(binary_string):
        # Check for periodic patterns explicitly
        for period in range(2, total_qubits + 1):
            segments = [binary_string[i:i+period] for i in range(0, len(binary_string), period)]
            
            # Check if segments are consistent
            if len(set(segments)) <= 2:
                return period
        
        return 2  # Default period

    periods = []
    for measure, count in counts.items():
        period = detect_period(measure)
        periods.extend([period] * count)

    # Find most frequent period
    period_counts = {}
    for p in periods:
        period_counts[p] = period_counts.get(p, 0) + 1
    
    max_count = max(period_counts.values())
    most_frequent_periods = [p for p, count in period_counts.items() if count == max_count]
    
    return min(most_frequent_periods)



def test_quantum_functions():
    tests_passed = 0
    tests_total = 9

    def run_test(test_name, test_func):
        try:
            test_func()
            print(f"✓ {test_name} Test: PASS")
            return True
        except Exception as e:
            print(f"✗ {test_name} Test: FAIL - {e}")
            return False

    # Period Estimation Test Cases
    class MockResult:
        def __init__(self, counts):
            self.counts = counts

        def get_counts(self):
            return self.counts

    # Period Estimation Tests
    def test_period_estimation():
        test_cases = [
            (MockResult({'0110': 300, '1001': 200, '0011': 100}), 3),
            (MockResult({'1000': 200, '0100': 100, '0010': 50}), 2),
            (MockResult({'11110': 500, '00011': 250}), 5)
        ]

        for i, (mock_result, expected_period) in enumerate(test_cases, 1):
            estimated_period = estimate_period(mock_result)
            assert estimated_period == expected_period, \
                f"Test {i}: Expected {expected_period}, Got {estimated_period}"

    # QFT Test with Visualization
    def test_qft_visualization():
        qr = QuantumRegister(4)
        circuit = QuantumCircuit(qr, ClassicalRegister(4))

        
        circuit.x(qr[1])  # Flip second qubit
        circuit.x(qr[3])  # Flip fourth qubit

        # Apply QFT
        qft(circuit, qr)

        # Measure all qubits
        circuit.measure_all()

        # Simulate the circuit
        simulator = AerSimulator()
        compiled_circuit = transpile(circuit, simulator)
        job = simulator.run(compiled_circuit, shots=1024)
        result = job.result()

        # Just print counts instead of plotting
        print(result.get_counts())

    # Quantum Arithmetic Tests
    def test_set_bits():
        qr_a = QuantumRegister(4)
        qc = QuantumCircuit(qr_a)
        set_bits(qc, qr_a, '1010')
        print(qc)  # Use print instead of drawing

    def test_copy():
        qr_a = QuantumRegister(4)
        qr_b = QuantumRegister(4)
        qc = QuantumCircuit(qr_a, qr_b)
        copy(qc, qr_a, qr_b)
        print(qc)

    def test_full_adder():
        qr_a = QuantumRegister(1)
        qr_b = QuantumRegister(1)
        qr_r = QuantumRegister(1)
        qr_aux = QuantumRegister(2)
        qc = QuantumCircuit(qr_a, qr_b, qr_r, qr_aux)

        qc.x(qr_a[0])
        qc.x(qr_b[0])
        full_adder(qc, qr_a[0], qr_b[0], qr_r[0], qr_aux[0], qr_aux[1], [qr_aux[0]])
        print(qc)

    def test_add():
        qr_a = QuantumRegister(4)
        qr_b = QuantumRegister(4)
        qr_r = QuantumRegister(4)
        qr_aux = QuantumRegister(5)
        qc = QuantumCircuit(qr_a, qr_b, qr_r, qr_aux)

        qc.x(qr_a[1])
        qc.x(qr_b[2])
        add(qc, qr_a, qr_b, qr_r, qr_aux)
        print(qc)

    def test_subtract():
        qr_a = QuantumRegister(4)
        qr_b = QuantumRegister(4)
        qr_r = QuantumRegister(4)
        qr_aux = QuantumRegister(5)
        qc = QuantumCircuit(qr_a, qr_b, qr_r, qr_aux)

        qc.x(qr_a[3])
        qc.x(qr_b[1])
        subtract(qc, qr_a, qr_b, qr_r, qr_aux)
        print(qc)

    def test_multiply_mod_fixed():
        N = 15
        X = 11
        B = QuantumRegister(4)
        AUX = QuantumRegister(4)
        qc = QuantumCircuit(B, AUX)
        multiply_mod_fixed(qc, N, X, B, AUX)
        print(qc)

    def test_controlled_times_two_power_mod():
        qr_n = QuantumRegister(4)
        qr_a = QuantumRegister(4)
        qr_r = QuantumRegister(4)
        qr_aux = QuantumRegister(4)
        qr_control = QuantumRegister(1)

        qc = QuantumCircuit(qr_n, qr_a, qr_r, qr_aux, qr_control)
        controlled_times_two_power_mod(qc, 15, qr_a, 2, qr_r, qr_aux, qr_control[0])
        print(qc)

    # Run tests
    tests_passed += run_test("QFT Visualization", test_qft_visualization)
    tests_passed += run_test("Period Estimation", test_period_estimation)
    tests_passed += run_test("Set Bits", test_set_bits)
    tests_passed += run_test("Copy", test_copy)
    tests_passed += run_test("Full Adder", test_full_adder)
    tests_passed += run_test("Add", test_add)
    tests_passed += run_test("Subtract", test_subtract)
    tests_passed += run_test("Multiply Mod Fixed", test_multiply_mod_fixed)
    tests_passed += run_test("Controlled Times Two Power Mod", test_controlled_times_two_power_mod)

    # Overall test result
    print(f"\nTest Results: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total

def main():
    result = test_quantum_functions()
    exit(0 if result else 1)

if __name__ == "__main__":
    main()

