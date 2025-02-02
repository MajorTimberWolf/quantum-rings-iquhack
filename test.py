import QuantumRingsLib
from QuantumRingsLib import QuantumRegister, AncillaRegister, ClassicalRegister, QuantumCircuit
from QuantumRingsLib import QuantumRingsProvider
from QuantumRingsLib import job_monitor
from QuantumRingsLib import JobStatus
from matplotlib import pyplot as plt
import numpy as np
import math
from fractions import Fraction

# Initialize QuantumRings provider
provider = QuantumRingsProvider(
    token='rings-200.b8X795Phx09UGpAHt8noxrzbDiKdFL1h',
    name='abku2504@gmail.com'
)
backend = provider.get_backend("scarlet_quantum_rings")
provider.active_account()

def calculate_required_qubits(N):
    n = len(bin(N)) - 2  # Number of bits in N
    n_count = 2 * n      # Qubits for phase estimation
    n_register = n       # Qubits for the number to factor
    n_ancilla = n        # Ancilla qubits needed for multiplication
    return n_count, n_register, n_ancilla

def qft(qc, q, start, n):
    """Apply QFT to n qubits starting at index start."""
    for j in range(n):
        for k in range(j):
            qc.cu1(math.pi / (2 ** (j - k)), q[start + k], q[start + j])
        qc.h(q[start + j])
    # Reverse qubit order
    for j in range(n//2):
        qc.swap(q[start + j], q[start + n - j - 1])

def iqft(qc, q, start, n):
    """Apply inverse QFT to n qubits starting at index start."""
    for j in range(n//2):
        qc.swap(q[start + j], q[start + n - j - 1])
    for j in reversed(range(n)):
        qc.h(q[start + j])
        for k in reversed(range(j)):
            qc.cu1(-math.pi / (2 ** (j - k)), q[start + k], q[start + j])

def controlled_add(qc, control, target_start, target, c, n):
    """Controlled addition of classical constant c to target register."""
    qft(qc, target, target_start, n)
    for i in range(n):
        angle = 2 * math.pi * (c << (n - i - 1)) / (2 ** n)
        qc.cu1(angle, control, target[target_start + i])
    iqft(qc, target, target_start, n)

def controlled_modular_multiply(qc, control, x_start, x_reg, ancilla_start, a, N, n):
    """Controlled modular multiplication by a mod N."""
    # Reset ancilla qubits
    for i in range(n):
        qc.reset(x_reg[ancilla_start + i])
    
    # Compute (x * a) mod N into ancilla
    for i in range(n):
        if (a >> i) & 1:
            shifted_val = (1 << i) % N
            for j in range(n):
                if (shifted_val >> j) & 1:
                    qc.ccx(control, x_reg[x_start + j], x_reg[ancilla_start + j])
    
    # Copy result back to x_reg
    for i in range(n):
        qc.cswap(control, x_reg[x_start + i], x_reg[ancilla_start + i])
    
    # Uncompute ancilla
    for i in range(n):
        qc.reset(x_reg[ancilla_start + i])

def create_shor_circuit(N, a=7):
    # Calculate required qubits for each register
    n_count, n_register, n_ancilla = calculate_required_qubits(N)
    total_qubits = n_count + n_register + n_ancilla
    
    # Create registers
    q = QuantumRegister(total_qubits, 'q')  # All quantum bits in one register
    c = ClassicalRegister(n_count, 'c')     # Classical bits for measurement
    qc = QuantumCircuit(q, c)
    
    # Define start indices for different register sections
    count_start = 0
    register_start = n_count
    ancilla_start = n_count + n_register
    
    # Initialize counting register
    for i in range(n_count):
        qc.h(q[i])
    qc.barrier()
    
    # Initialize computational register to |1>
    qc.x(q[register_start])
    qc.barrier()
    
    # Apply controlled modular multiplications
    for i in range(n_count):
        power = pow(a, 2 ** i, N)
        controlled_modular_multiply(qc, q[i], register_start, q, ancilla_start, power, N, n_register)
        qc.barrier()
    
    # Apply inverse QFT
    iqft(qc, q, count_start, n_count)
    
    # Measure counting register
    for i in range(n_count):
        qc.measure(q[i], c[i])
    
    return qc, n_count

def continued_fraction_expansion(measurement, n_count, N):
    measured_value = int(measurement, 2)
    phase = measured_value / (2 ** n_count)
    frac = Fraction(phase).limit_denominator(N)
    return frac.denominator

def find_factors(N, period, a):
    if period % 2 != 0:
        return None
    x = pow(a, period // 2, N)
    if x == 1 or x == N - 1:
        return None
    factor1 = math.gcd(x + 1, N)
    factor2 = math.gcd(x - 1, N)
    if factor1 * factor2 == N and 1 < factor1 < N and 1 < factor2 < N:
        return factor1, factor2
    return None

# Test with semiprimes
semiprimes = {
    8: 143,
    10: 899,
    12: 3127,
}

for bits, N in semiprimes.items():
    print(f"\nFactoring {N} ({bits} bits):")
    try:
        a = 7  # Ensure a is coprime to N
        qc, n_count = create_shor_circuit(N, a)
        job = backend.run(qc, shots=1024)
        job_monitor(job)
        counts = job.result().get_counts()
        
        print(f"Circuit depth: {qc.depth()}, Qubits: {qc.num_qubits}")
        for measurement, count in counts.items():
            if count > 50:  # Only process measurements with significant counts
                period = continued_fraction_expansion(measurement, n_count, N)
                factors = find_factors(N, period, a)
                if factors:
                    print(f"Factors: {factors[0]} × {factors[1]}")
                    break
        
        plt.figure()
        plt.bar(counts.keys(), counts.values())
        plt.title(f"N={N} Measurement Results")
        plt.show()
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        try:
            del qc
        except:
            pass

print("\nQuantum factoring complete!")