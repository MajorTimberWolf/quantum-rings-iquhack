# Quantum Factoring via Quantum Rings Simulator

This repository contains a Python implementation of a version of Shor's algorithm using the Quantum Rings simulator. The code, built with the `QuantumRingsLib` library, is designed to factor semiprime numbers by employing the order-finding subroutine at the core of Shor's algorithm. If you'd like to know my Thoughts during this whole hackathon, they can be found [here](https://github.com/MajorTimberWolf/quantum-rings-iquhack/blob/main/THOUGHTS.MD) + an article regarding this implementation coming soon :)

## Overview

The implementation follows these key steps:

- **Quantum Register Initialization:**
  The number of qubits is dynamically determined based on the bit-length of the integer \( N \) to be factored. The algorithm utilizes three distinct registers:
    - **Counting Register:**  A register used for phase estimation. It is initialized into a uniform superposition using Hadamard gates.
    - **Computational Register:** This register holds the number whose order is being estimated and is initialized to the state \(|1\rangle\).
    - **Ancilla Register:**  A register used as temporary storage during controlled modular multiplication.

- **Quantum Fourier Transform (QFT) and Inverse QFT:**
  Custom functions `qft` and `iqft` implement the Quantum Fourier Transform and its inverse over designated blocks of qubits within the quantum register. These are critical for extracting the phase that encodes the period \( r \) of the modular exponentiation function.

- **Controlled Modular Multiplication:**
  The `controlled_modular_multiply` function is designed to compute \((x \times a) \mod N\) under the control of a separate qubit. This operation is a key building block for constructing the modular exponentiation required by Shor’s algorithm. This is done by hardwiring the classical constants into the circuit, and using the controlled-x gate, ccx (toffoli) gate and the cswap gate (Fredkin gate)
  
- **Circuit Assembly:**
  The function `create_shor_circuit(N, a)` constructs the full quantum circuit by:
  1.  Initializing the counting and computational registers, preparing them for the quantum computation.
  2.  Applying a series of controlled modular multiplication operations, using varying powers of \( a \), controlled by the qubits in the counting register.
  3.  Applying the inverse Quantum Fourier Transform to the counting register.
  4.  Measuring the counting register to obtain the classical bitstrings for post-processing.

- **Classical Post-Processing:**
  The measurement outcomes are then classically processed using continued fraction expansion (via `continued_fraction_expansion`) to estimate the period \( r \). Finally, the factors of \( N \) are derived from the period using classical routines, such as the greatest common divisor (GCD).

## Code

The full implementation is available in the [linked repository](https://github.com/MajorTimberWolf/quantum-rings-iquhack).

## Results

For each semiprime ( N ) tested, the results will include:

- **Factors:** The prime factors (e.g., 143 is factored as \(11 \times 13\)).
- **Quantum Resources:**
    - **Counting Register:**  \(2n\) qubits, where \(n\) is the number of bits in \(N\).
    - **Computational Register:**  \(n\) qubits.
    - **Ancilla Register:** \(n\) qubits.
    - **Total Qubits:**  Ideally, \(4n\) qubits would be required; however, due to the unified register implementation, the total number of qubits is equal to \(2n + 3\).
    - **Circuit Depth:** The circuit depth will be reported directly by the `qc.depth()` method.
-   **Execution Times:** The execution times are monitored via the job monitor output from the Quantum Rings backend.
-   **Measurement Results:** The measurement outcomes for each factorization are visualized as bar charts. These charts display the frequencies of different measurement outcomes for the counting register, which are used in the continued fraction expansion process to deduce the period \(r\).  Significant peaks in the measurement outcomes are related to the periods needed for successful factorization.

## Registration and Validation

-   **Quantum Rings Email:** `abku2504@gmail.com`
This email was used to register with Quantum Rings and validates the execution of the circuit.

## Algorithm Documentation

The implementation leverages the core ideas of Shor’s algorithm:

1.  **Phase Estimation:**
    *   The algorithm utilizes the quantum phase estimation algorithm to determine the period of the function \(f(x) = a^x \mod N\), where \(a\) is a coprime number to \(N\).
    *   The counting register is initialized in a superposition using Hadamard gates to probe all possible phases. The eigenvalues of the unitary operator \(U\) (where \(U|x\rangle = |ax \mod N\rangle\)) are of the form \(e^{2\pi i s/r}\), where \(r\) is the period we want to extract.  Applying the inverse QFT on the counting register allows us to extract the estimate of the phase and thus of the period.

2.  **Controlled Modular Multiplication:**
    *   Controlled modular multiplications implement modular exponentiation by applying the operator \(U^x\) on the computational register conditionally on the state of the qubits in the counting register.
    *   This is done by hardwiring the classical constants into the circuit, and using the controlled-x gate, ccx (toffoli) gate and the cswap gate (Fredkin gate). This implementation method is more straightforward and easier to implement compared to QFT-based adders.

3.  **Classical Postprocessing:**
    *   The results of the quantum computation are classical bitstrings representing estimates of the phase.
    *   These estimates are used with continued fraction expansion to get the best rational approximation for the phase, whose denominator gives us the period \(r\).
    *    Once we find \(r\), we calculate the greatest common divisor (GCD) of  \(a^{r/2} + 1\) and \(a^{r/2} - 1\) with the number we are trying to factor, \(N\). If the GCD is nontrivial, we found a factor!

## References

-   Shor, P. (1997). Polynomial-time algorithms for prime factorization and discrete logarithms on a quantum computer. *SIAM J. Comput.*
-   Stephane Beauregard, “Circuit for Shor’s algorithm using 2n+3 qubits”  

## Future Work

Future improvements may include integrating a more optimized modular multiplication circuit inspired by Beauregard’s techniques to reduce qubit counts and circuit depth further, and we will attempt to incorporate error correction in future iterations.
