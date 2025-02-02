#!/usr/bin/env python
"""
Quantum Rings version of a simplified Shor's algorithm example.
This demo builds a circuit to factor 15 using the modular exponentiation for a = 7.
Currently, only N=15 and a=7 is implemented.
"""

import QuantumRingsLib
from QuantumRingsLib import QuantumRegister, ClassicalRegister, QuantumCircuit
from QuantumRingsLib import QuantumRingsProvider, job_monitor, JobStatus
from matplotlib import pyplot as plt
import numpy as np
import math
import sys

# --- Utility functions ---

def iqft_cct(qc, reg, n):
    """
    Implements the inverse QFT on the first n qubits of the given register.
    """
    for i in range(n):
        for j in range(1, i+1):
            # Apply controlled U1 rotation with negative angle.
            angle = -math.pi / (2 ** (i - j + 1))
            qc.cu1(angle, reg[j-1], reg[i])
        qc.h(reg[i])
    qc.barrier()
    return

def plot_histogram(counts, title=""):
    """
    Plot a simple histogram of measurement counts.
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    plt.xlabel("States")
    plt.ylabel("Counts")
    # Expand counts into a list for plotting.
    state_list = [state for state, cnt in counts.items() for _ in range(cnt)]
    unique, inverse = np.unique(state_list, return_inverse=True)
    bin_counts = np.bincount(inverse)
    plt.bar(unique, bin_counts)
    maxFreq = max(counts.values())
    plt.ylim(top=(math.ceil(maxFreq/10)*10 if maxFreq % 10 else maxFreq+10))
    plt.title(title)
    plt.show()
    return

def modular_exponentiation(qc, q, a, N):
    """
    For N = 15 and a = 7, builds the modular exponentiation subcircuit
    that computes f(x) = 7^x mod 15 using a hard-coded sequence.
    This demo assumes:
       - The exponent register consists of the first 3 qubits in q.
       - Qubits q[3] to q[6] are used as work registers.
    
    The following gate sequence is taken from early demonstrations.
    """
    if N != 15 or a != 7:
        sys.exit("Error: This demo currently supports only N=15 with a=7.")
    qc.cx(q[2], q[4])
    qc.cx(q[2], q[5])
    qc.cx(q[6], q[4])
    qc.ccx(q[1], q[5], q[3])
    qc.cx(q[3], q[5])
    qc.ccx(q[1], q[4], q[6])
    qc.cx(q[6], q[4])
    qc.barrier()
    return

# --- Main script ---

def main():
    try:
        N = int(input("Enter the integer N to factorize (must be 15 for this demo): "))
        a = int(input("Enter an integer a (for demo, use a=7 which is coprime with 15): "))
    except ValueError:
        sys.exit("Please enter valid integer values.")
    
    if N != 15 or a != 7:
        sys.exit("This demo currently supports only N=15 with a=7.")

    # --- Set up the Quantum Rings provider and backend ---
    provider = QuantumRingsProvider(
        token='rings-200.b8X795Phx09UGpAHt8noxrzbDiKdFL1h',
        name='abku2504@gmail.com'
    )
    backend = provider.get_backend("scarlet_quantum_rings")
    shots = 1024

    provider.active_account()

    # --- Build the quantum circuit ---
    number_of_qubits = 7  # For this demo, we use 7 qubits.
    q = QuantumRegister(number_of_qubits, 'q')
    c = ClassicalRegister(4, 'c')
    qc = QuantumCircuit(q, c)

    # Prepare the input state:
    # Apply Hadamard gates to the first 3 qubits (exponent register)
    qc.h(q[0])
    qc.h(q[1])
    qc.h(q[2])
    # Initialize the work register: set qubit 6 to |1>
    qc.x(q[6])
    qc.barrier()

    # Apply the modular exponentiation for a = 7 mod 15.
    modular_exponentiation(qc, q, a, N)

    # Apply the inverse QFT on the first 3 qubits.
    iqft_cct(qc, q, 3)

    # Measure the exponent register (first 3 qubits) into classical bits.
    qc.measure(q[0], c[0])
    qc.measure(q[1], c[1])
    qc.measure(q[2], c[2])

    # Optionally draw the circuit.
    qc.draw('mpl')
    
    # --- Execute the circuit ---
    print("Submitting job to Quantum Rings backend...")
    job = backend.run(qc, shots=shots)
    job_monitor(job)
    result = job.result()
    counts = result.get_counts()
    
    print("Measurement counts:")
    print(counts)
    plot_histogram(counts, title="Shor's Algorithm (N=15, a=7) Results")

    # Clean up
    del qc, result, job

if __name__ == "__main__":
    main()