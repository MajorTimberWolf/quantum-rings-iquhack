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

def iqft_cct(qc, q, n):
    """
    Quantum Fourier Transform inverse implementation
    Args:
        qc (QuantumCircuit): The quantum circuit
        q (QuantumRegister): The quantum register
        n (int): Number of qubits
    """
    for i in range(n):
        for j in range(1, i+1):
            # Ensure angles are within valid range
            angle = -math.pi / float(2**(i-j+1))
            qc.cu1(angle, q[j-1], q[i])
        qc.h(q[i])
    qc.barrier()

def create_modular_multiplication(qc, q, x, N):
    """
    Creates a modular multiplication circuit based on the example circuit
    Args:
        qc (QuantumCircuit): The quantum circuit
        q (QuantumRegister): The quantum register
        x (int): Multiplier
        N (int): Modulus
    """
    # Using the working structure from the example code
    qc.cx(q[2], q[4])
    qc.cx(q[2], q[5])
    qc.cx(q[6], q[4])
    qc.ccx(q[1], q[5], q[3])
    qc.cx(q[3], q[5])
    qc.ccx(q[1], q[4], q[6])
    qc.cx(q[6], q[4])

def shors_circuit(N, shots=1024):
    """
    Creates Shor's algorithm circuit following the working example structure
    Args:
        N (int): Number to factor
        shots (int): Number of circuit runs
    Returns:
        tuple: (circuit, measurement results)
    """
    # Use the same structure as the working example
    numberofqubits = 7  # Fixed size as per example
    q = QuantumRegister(numberofqubits, 'q')
    c = ClassicalRegister(4, 'c')
    qc = QuantumCircuit(q, c)

    # Initialize source and target registers (following example)
    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.x(6)
    qc.barrier()

    # Modular exponentiation (using 7 as coprime)
    create_modular_multiplication(qc, q, 7, N)
    qc.barrier()

    # Apply inverse QFT
    iqft_cct(qc, q, 3)  # Apply to first 3 qubits as per example

    # Measure
    qc.measure(q[0], c[0])
    qc.measure(q[1], c[1])
    qc.measure(q[2], c[2])

    # Execute circuit
    try:
        job = backend.run(qc, shots=shots)
        job_monitor(job)
        result = job.result()
        counts = result.get_counts()
        return qc, counts
    except Exception as e:
        print(f"Circuit execution error: {str(e)}")
        return qc, None

def plot_histogram(counts, title=""):
    """
    Plots histogram of measurement results
    """
    if counts is None:
        print("No counts to plot")
        return
        
    fig, ax = plt.subplots(figsize=(10, 7))
    plt.xlabel("Measured State")
    plt.ylabel("Counts")
    mylist = [key for key, val in counts.items() for _ in range(val)]
    unique, inverse = np.unique(mylist, return_inverse=True)
    bin_counts = np.bincount(inverse)
    plt.bar(unique, bin_counts)
    maxFreq = max(counts.values())
    plt.ylim(ymax=np.ceil(maxFreq / 10) * 10 if maxFreq % 10 else maxFreq + 10)
    plt.title(title)
    plt.show()

# Test with provided semiprimes
semiprimes = {
    8: 143,
    10: 899,
    12: 3127,
}

for bits, N in semiprimes.items():
    print(f"\nFactoring {N} ({bits} bits):")
    try:
        # Create and execute circuit
        circuit, counts = shors_circuit(N)
        
        # Draw circuit
        print("Drawing circuit...")
        circuit.draw('mpl')
        
        # Plot results if available
        if counts:
            print("Plotting results...")
            plot_histogram(counts, f"Quantum Phase Estimation Results for N={N}")
            print("Measurement counts:", counts)
        
    except Exception as e:
        print(f"Error processing {N}: {str(e)}")
    finally:
        try:
            del circuit
        except:
            pass

print("\nQuantum factoring complete!")
