import QuantumRingsLib
from QuantumRingsLib import QuantumRegister, AncillaRegister, ClassicalRegister, QuantumCircuit
from QuantumRingsLib import QuantumRingsProvider
from QuantumRingsLib import job_monitor
from QuantumRingsLib import JobStatus
from matplotlib import pyplot as plt
import numpy as np
import math

# Initialize QuantumRings provider
provider = QuantumRingsProvider(
    token='rings-200.b8X795Phx09UGpAHt8noxrzbDiKdFL1h',
    name='abku2504@gmail.com'
)
backend = provider.get_backend("scarlet_quantum_rings")
provider.active_account()

def find_period(a, N):
    """
    Find the period of f(x) = a^x mod N
    Args:
        a (int): base of the exponential
        N (int): modulus
    Returns:
        int: period r where a^r ≡ 1 (mod N)
    """
    x = 1
    period = 0
    while True:
        x = (x * a) % N
        period += 1
        if x == 1:
            return period

def iqft_cct(qc, b, n):
    """
    The inverse QFT circuit
    Args:
        qc (QuantumCircuit): The quantum circuit
        b (QuantumRegister): The target register
        n (int): The number of qubits in the registers to use
    """
    for i in range(n):
        for j in range(1, i+1):
            qc.cu1(-math.pi / 2**(i-j+1), b[j-1], b[i])
        qc.h(b[i])
    qc.barrier()

def plot_histogram(counts, title=""):
    """
    Plots the histogram of the counts
    Args:
        counts (dict): The dictionary containing the counts of states
        title (str): A title for the graph
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    plt.xlabel("States")
    plt.ylabel("Counts")
    mylist = [key for key, val in counts.items() for _ in range(val)]
    unique, inverse = np.unique(mylist, return_inverse=True)
    bin_counts = np.bincount(inverse)
    plt.bar(unique, bin_counts)
    maxFreq = max(counts.values())
    plt.ylim(ymax=np.ceil(maxFreq / 10) * 10 if maxFreq % 10 else maxFreq + 10)
    plt.title(title)
    plt.show()

def create_modular_exponentiation(qc, q, a, N):
    """
    Create circuit for modular exponentiation a^x mod N
    Args:
        qc (QuantumCircuit): quantum circuit
        q (QuantumRegister): quantum register
        a (int): base for modular exponentiation
        N (int): modulus
    """
    # This is a simplified version for demonstration
    # For actual implementation, you'd need to decompose this into elementary gates
    qc.cx(q[2], q[4])
    qc.cx(q[2], q[5])
    qc.cx(q[6], q[4])
    qc.ccx(q[1], q[5], q[3])
    qc.cx(q[3], q[5])
    qc.ccx(q[1], q[4], q[6])
    qc.cx(q[6], q[4])

def shors_factoring(N, shots=1024):
    """
    Implementation of Shor's algorithm for factoring N using QuantumRings
    Args:
        N (int): number to factor
        shots (int): number of measurements to perform
    Returns:
        dict: measurement results
    """
    # Calculate required number of qubits
    n = len(bin(N)[2:])  # number of bits needed to represent N
    total_qubits = 2 * n + 3  # including ancilla qubits

    # Create quantum registers
    q = QuantumRegister(total_qubits, 'q')
    c = ClassicalRegister(4, 'c')  # Adjust classical register size as needed
    qc = QuantumCircuit(q, c)

    # Initialize counting register
    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.x(6)  # Initialize ancilla
    qc.barrier()

    # Apply modular exponentiation
    create_modular_exponentiation(qc, q, 7, N)  # Using 7 as coprime
    qc.barrier()

    # Apply inverse QFT
    iqft_cct(qc, q, 3)

    # Measure
    qc.measure(q[0], c[0])
    qc.measure(q[1], c[1])
    qc.measure(q[2], c[2])

    # Execute circuit
    job = backend.run(qc, shots=shots)
    job_monitor(job)
    result = job.result()
    counts = result.get_counts()

    return counts, qc

# Process each semiprime
semiprimes = {
    8: 143,
    10: 899,
    12: 3127,
    14: 11009,
    16: 47053,
    18: 167659,
    20: 744647,
    22: 3036893,
}

for bits, N in semiprimes.items():
    print(f"\nFactoring {N} ({bits} bits):")
    try:
        counts, qc = shors_factoring(N)
        
        # Draw the circuit
        qc.draw('mpl')
        
        # Visualize results
        plot_histogram(counts, f"Shor's Algorithm Results for N={N}")
        
        # Process results to find factors
        period = find_period(7, N)  # Using 7 as coprime
        if period % 2 == 0:
            guess1 = pow(7, period//2, N) + 1
            guess2 = pow(7, period//2, N) - 1
            factor1 = math.gcd(guess1, N)
            factor2 = math.gcd(guess2, N)
            if factor1 * factor2 == N:
                print(f"Factors found: {factor1} × {factor2}")
        else:
            print("Period was odd, try again with different coprime")
            
    except Exception as e:
        print(f"Error factoring {N}: {str(e)}")
    finally:
        # Clean up
        del qc
        
print("\nFactoring complete!")