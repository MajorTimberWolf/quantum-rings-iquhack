#!/usr/bin/env python
"""
Quantum Rings version of a simplified Shor's algorithm example.
This demo builds a circuit to factor semiprime integers.
Supports factoring of integers up to 12-bit size with a placeholder for modular exponentiation.
"""

import QuantumRingsLib
from QuantumRingsLib import QuantumRegister, ClassicalRegister, QuantumCircuit
from QuantumRingsLib import QuantumRingsProvider, job_monitor, JobStatus
from matplotlib import pyplot as plt
import numpy as np
import math
import sys
import qiskit  # Import qiskit to ensure it's available

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

def modular_exponentiation_placeholder(qc, q, a, N, exponent_bits, work_bits):
    """
    Placeholder for modular exponentiation, slightly improved to use exponent and work bits.
    For now, it applies some controlled gates based on exponent bits to demonstrate circuit execution.
    In a real Shor's algorithm, this would be replaced with a proper modular exponentiation circuit.
    """
    print(f"Executing modular exponentiation placeholder for a={a}, N={N}")
    # Example: apply CNOT gates based on exponent bits (placeholder logic)
    for i in range(exponent_bits):
        for j in range(work_bits):
            if (i + j) % 2 == 0: # Just some arbitrary control for demonstration
                qc.cx(q[i], q[exponent_bits + j])
    qc.barrier()
    return


# --- Main script ---

def main():
    semiprimes = {
        8: 143,
        10: 899,
        12: 3127,
        # 14: 11009,  # You can uncomment these to test larger numbers, but be mindful of qubit requirements and execution time
        # 16: 47053,
        # 18: 167659,
        # 20: 744647,
        # 22: 3036893,
        # 24: 11426971,
        # 26: 58949987,
        # 28: 208241207,
        # 30: 857830637,
        # 32: 2776108693,
        # 34: 11455067797,
        # 36: 52734393667,
        # 38: 171913873883,
        # 40: 862463409547,
        # 42: 2830354423669,
        # 44: 12942106192073,
        # 46: 53454475917779,
        # 48: 255975740711783,
        # 50: 696252032788709,
        # 52: 3622511636491483,
        # 54: 15631190744806271,
        # 56: 51326462028714137,
        # 58: 217320198167105543,
        # 60: 827414216976034907,
        # 62: 3594396771839811733,
        # 64: 13489534701147995111,
        # 66: 48998116978431560767,
        # 68: 220295379750460962499,
        # 70: 757619317101213697553,
        # 72: 4239706985407101925109,
        # 74: 13081178794322790282667,
        # 76: 48581232636534199345531,
        # 78: 263180236071092621088443,
        # 80: 839063370715343025081359,
        # 82: 3145102596907521247788809,
        # 84: 13410747867593584234359179,
        # 86: 74963308816794035875414187,
        # 88: 196328049947816898123437813,
        # 90: 900212494943030042797046797,
        # 92: 3408479268382267351010110507,
        # 94: 13410207519922000104514406009,
        # 96: 56540697284955642837798912007,
        # 98: 212736089539904961817389577063,
        # 100: 793334180624272295351382130129,
        # ... (rest of the list)
    }

    # --- Set up the Quantum Rings provider and backend ---
    provider = QuantumRingsProvider(
        token='rings-64.8fourH2rnXVCbZ3QCI0wFKibkUij6WHS',
        name='abku2504@gmail.com'
    )
    backend = provider.get_backend("scarlet_quantum_rings")
    shots = 1024
    provider.active_account()


    for bit_size, N in list(semiprimes.items())[:3]: # Iterate through the first 3 semiprimes (up to 12-bit)
        print(f"\n--- Factoring N = {N} (Bit size: {bit_size}) ---")
        try:
            a = int(input(f"Enter an integer 'a' coprime to N={N} (for demo, try a=2): "))
        except ValueError:
            sys.exit("Please enter valid integer values.")

        if math.gcd(a, N) != 1:
            sys.exit(f"Error: 'a'={a} is not coprime to N={N}. Please choose a coprime 'a'.")

        # --- Build the quantum circuit ---
        exponent_bits = bit_size # Number of qubits for exponent register, roughly bit size of N
        work_bits = bit_size      # Number of qubits for work register, for simplicity same as exponent for now.
        number_of_qubits = exponent_bits + work_bits + 1 # +1 for potential ancilla, adjust if needed. Let's start with this
        q = QuantumRegister(number_of_qubits, 'q')
        c = ClassicalRegister(exponent_bits, 'c') # Measure exponent register
        qc = QuantumCircuit(q, c)

        # Prepare the input state:
        # Apply Hadamard gates to the exponent register
        for i in range(exponent_bits):
            qc.h(q[i])

        # Initialize the work register: set qubit (exponent_bits + work_bits) to |1> (last qubit for now)
        qc.x(q[number_of_qubits - 1])
        qc.barrier()

        # Apply the modular exponentiation (placeholder for now).
        modular_exponentiation_placeholder(qc, q, a, N, exponent_bits, work_bits)

        # Apply the inverse QFT on the exponent register.
        iqft_cct(qc, q, exponent_bits)

        # Measure the exponent register into classical bits.
        for i in range(exponent_bits):
            qc.measure(q[i], c[i])

        # Optionally draw the circuit.
        qc.draw('mpl')

        # --- Execute the circuit ---
        print(f"Submitting job for N={N} to Quantum Rings backend...")
        job = backend.run(qc, shots=shots)
        job_monitor(job)
        result = job.result()
        counts = result.get_counts()

        print(f"Measurement counts for N={N}:")
        print(counts)
        plot_histogram(counts, title=f"Shor's Algorithm Placeholder (N={N}, a={a}) Results")

        # --- Period finding and Factor Extraction (Conceptual - Needs Implementation) ---
        print("\n--- Period Finding and Factor Extraction (Conceptual) ---")
        print("Analysis of measurement counts to find the period 'r' and extract factors of N is needed.")
        print("This involves:")
        print("1. Identifying the most frequent measurement outcomes.")
        print("2. Using continued fractions to estimate the period 'r' from these outcomes.")
        print("3. Calculating factors using gcd(a^(r/2) ± 1, N).")
        print("This part is not yet implemented in this placeholder demo.")


        # Clean up
        del qc, result, job

if __name__ == "__main__":
    main()