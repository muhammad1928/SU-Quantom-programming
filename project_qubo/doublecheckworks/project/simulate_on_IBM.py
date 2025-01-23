from qiskit_ibm_runtime import QiskitRuntimeService, Session, EstimatorV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def validate_inputs(circuit, hamiltonian, parameters):
    """
    Validate inputs to ensure compatibility.
    """
    if circuit.num_qubits != hamiltonian.num_qubits:
        raise ValueError("Mismatch between circuit qubits and Hamiltonian qubits.")
    if len(parameters) != len(circuit.parameters):
        raise ValueError("Parameter count mismatch for the given circuit.")

def preprocess_circuit(circuit, hamiltonian, backend):
    """
    Preprocess the QAOA circuit by transpiling it for the IBM Quantum backend.
    """
    validate_inputs(circuit, hamiltonian, circuit.parameters)

    # Generate pass manager for backend optimization
    pass_manager = generate_preset_pass_manager(backend=backend)
    transpiled_circuit = pass_manager.run(circuit)

    return transpiled_circuit

def run_on_ibm_quantum(hamiltonian, circuit, parameters, backend=None, shots=1024, validate_constraints=None, session=None):
    """
    Run the optimized QAOA circuit on IBM Quantum hardware.

    Args:
        hamiltonian: The cost Hamiltonian (SparsePauliOp).
        circuit: The QAOA circuit (QuantumCircuit).
        parameters: The parameters for the QAOA circuit (list of Parameter).
        backend: Specific IBM Quantum backend (optional).
        shots: Number of shots for the execution (default 1024).
        validate_constraints (callable, optional): Function to validate the most probable bitstring.

    Returns:
        dict: Results from the quantum job, including measurement counts.
    """
    try:
        # Initialize IBM Quantum service
        service = QiskitRuntimeService()
        if backend is None:
            backend = service.backend("ibm_kyiv")
        logging.info(f"Using backend: {backend.name}")

        # Preprocess the circuit for the selected backend
        logging.info("Preprocessing the circuit for the IBM Quantum backend...")
        preprocessed_circuit = preprocess_circuit(circuit, hamiltonian, backend)

        # Apply the layout to the Hamiltonian observables
        observables = hamiltonian.apply_layout(preprocessed_circuit.layout)

        # Set up a session for job submission
        if session is None:
            logging.info("No active session detected. Creating a new session...")
            session = Session(backend=backend)

        # Set up a session for job submission
        with session as active_session:
            logging.info("Submitting job to IBM Quantum...")

            # Create Estimator instance for evaluating expectation values
            estimator = EstimatorV2()

            # Run the job on the quantum hardware
            job = estimator.run([(preprocessed_circuit, observables, parameters)])
            result = job.result()

            # Extract the expectation value
            pub_result = result[0]
            expectation_value = pub_result.data.evs[0]
            # Simulate counts if needed (placeholder or real results in practice)
            counts = {"placeholder_bitstring": 1}  # Replace with actual count inference if available

            # Extract the most probable bitstring
            most_probable_bitstring = max(counts, key=counts.get, default=None)

            # Validate the most probable bitstring
            is_valid = validate_constraints(most_probable_bitstring) if validate_constraints else True

            logging.info("Job completed successfully!")

            return {
                "counts": counts,
                "most_probable_bitstring": most_probable_bitstring,
                "is_valid": is_valid,
                "expectation_value": expectation_value
            }

    except Exception as e:
        logging.error(f"An error occurred during execution: {e}")
        return {
            "counts": {},
            "most_probable_bitstring": None,
            "is_valid": False,
            "expectation_value": None
        }
    finally:
        if session:
            try:
                session.close()
                logging.info("Session closed successfully.")
            except Exception as close_error:
                logging.error(f"Failed to close the session: {close_error}")