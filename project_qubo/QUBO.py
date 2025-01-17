#Obs: Based on the tutorial:

# https://qiskit-community.github.io/qiskit-optimization/tutorials/03_minimum_eigen_optimizer.html


from qiskit_algorithms.utils import algorithm_globals
from qiskit_algorithms import QAOA, NumPyMinimumEigensolver
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import Sampler
from qiskit_optimization.algorithms import (
MinimumEigenOptimizer,
RecursiveMinimumEigenOptimizer,
SolutionSample,
OptimizationResultStatus,
)

from qiskit_optimization import QuadraticProgram
from qiskit.visualization import plot_histogram
from typing import List, Tuple
import numpy as np


# create a QUBO
qubo = QuadraticProgram()
qubo.binary_var("x")
qubo.binary_var("y")
qubo.binary_var("z")
qubo.minimize(linear=[1, -2, 3], quadratic={("x", "y"): 1, ("x", "z"): -1, ("y", "z"): 2})


print(qubo.prettyprint())


op, offset = qubo.to_ising()
print("offset: {}".format(offset))
print("operator:")
print(op)


# Transforming an sparse Pauli operator back into a quadratic program
# For example, if we want to solve the quadratic program using other tools.
qp = QuadraticProgram()
qp.from_ising(op, offset, linear=True)
print(qp.prettyprint())


##################################################
# Solving the QUBO with the MinimumEigenOptimizer
##################################################


# Choosing a Random Seed 
algorithm_globals.random_seed = 10598

# Solving with QAOA (Quantum Approximation Optimization Algorithm)
print("\nSolution with QAOA:\n")
qaoa_mes = QAOA(sampler=Sampler(), optimizer=COBYLA(), initial_point=[0.0, 0.0])
qaoa = MinimumEigenOptimizer(qaoa_mes) # using QAOA
qaoa_result = qaoa.solve(qubo)
print(qaoa_result.prettyprint())


# Exact version. For testing purposes. Uses the classical numpy eigensolver to get the optimal solution. Will only work for small examples. 
print("\n Exact Solution:\n")
exact_mes = NumPyMinimumEigensolver()
exact = MinimumEigenOptimizer(exact_mes) 
exact_result = exact.solve(qubo)
print(exact_result.prettyprint())


#Printing Sampling Statistics
print("variable order:", [var.name for var in qaoa_result.variables])
for s in qaoa_result.samples:
    print(s)