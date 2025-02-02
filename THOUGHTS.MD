# THOUGHTS.md

## Reflections on the Implementation of Quantum Factoring

### Overview

This project focused on simulating Shor’s algorithm using the Quantum Rings simulator to factor semiprime numbers. We aimed to build an efficient circuit that utilizes a unified quantum register, while minimizing resource requirements. This involved adapting classical ideas like phase estimation, controlled modular multiplication, and classical postprocessing, with quantum algorithms such as the Quantum Fourier Transform (QFT).

### Algorithmic Details

- **Phase Estimation and QFT:**
    - The algorithm extracts the phase corresponding to the periodic function \(f(x) = a^x \mod N\) using the Quantum Fourier Transform. The QFT and inverse QFT were implemented as custom functions that act on specific sets of qubits in the register. The accuracy of phase estimation greatly relies on the correct implementation of the QFT and its inverse and directly influences the precision with which the period \(r\) can be extracted.

- **Controlled Modular Multiplication:**
    - We implemented controlled modular multiplication to compute \((a \times x) \mod N\) on the computational register. While a more efficient modular multiplication can be constructed using QFT-based adders (as described in Draper's and Beauregard’s approaches), we opted for a simpler implementation.
        - **Note:** We attempted to incorporate a modular multiplication approach inspired by Stephane Beauregard's paper "Circuit for Shor’s algorithm using 2n+3 qubits," which outlines a method to implement modular multiplication more efficiently. However, due to time constraints and the complexity of the QFT-based adder circuit, the Beauregard-inspired method was not fully implemented. The challenges included proper initialization and the complex interdependencies between the qubits when implementing the QFT adder. This approach requires a more intricate gate sequence, and we ran into some issues getting it to work properly in time.
        - Instead, we implemented a less resource-efficient method that uses a hardwired approach where classical constants are incorporated directly into the circuit. This is done via a sequence of conditional gates (such as controlled-X, Toffoli and Fredkin gates) based on the bit representation of a. While this method was easier to implement on the simulator it is not as scalable as the method suggested by Beauregard.

- **Postprocessing via Continued Fractions:**
    - Measurement of the quantum register outputs bit strings approximating the phase \(\phi = \frac{j}{r}\). We then use classical continued fraction expansion to determine the denominator \( r \) (the period) and subsequently use the GCD to find the factors of \(N\).

### Challenges and Learnings

- **Circuit Depth vs. Qubit Count:**
    - In this design we encountered the classic tradeoff between minimizing the number of qubits and keeping the circuit depth manageable. Reducing the number of qubits is always beneficial, as it reduces the physical resources required and minimizes error rates due to gate errors, while shallower circuits generally produce more accurate results due to less decoherence and gate error accumulation. The current implementation prioritizes lower qubit count using a unified register, which leads to increased circuit depth.
    - If we prioritize lower qubit count, the circuit generally becomes deeper because we will need to reuse qubits for computations, which in our current implementation will require multiple controlled operations. If we prioritize shallow circuits, we would need to duplicate the qubits, which in the end would result in larger qubit counts, but less operations, and thus, a shallower circuit.

- **Modular Arithmetic Complexity:**
    - Modular addition and multiplication operations are not inherently suited to quantum hardware and are difficult to implement efficiently. Implementing a reversible modular adder and its controlled variant required careful handling of ancilla bits, and careful manipulation of overflow conditions. The "hardwiring" of classical constants simplifies the circuit, but reduces the scalabilty, highlighting a trade-off between ease of implementation and optimality.

- **Beauregard’s Approach:**
    - Beauregard’s paper details a method for constructing a modular multiplication circuit using only \(2n+3\) qubits by utilizing a QFT-based adder and sequentially computing multiplications. Our implementation, while inspired by this approach, does not fully realize this optimization due to the implementation complexity and time constraints.

### Future Directions

- **Integrating Beauregard’s Modular Multiplication:**
    - Future development will focus on integrating Beauregard's technique which will significantly reduce both the qubit count and overall gate complexity. This would involve using the QFT based adder instead of our currently implemented hardwired approach which is a significant area of improvement.

- **Error Mitigation and Circuit Optimization:**
    - As quantum hardware develops, minimizing circuit depth and implementing error mitigation will become crucial. Optimizing subroutines like the QFT and refining the controlled operations are key for reducing error rates.

- **Scalability Analysis:**
    - Although this simulation is on a quantum simulator, analyzing resource usage is key to understanding scalability on physical quantum hardware.

### Final Thoughts

This project provided invaluable insights into the practical aspects of implementing quantum algorithms. We underscored the importance of both classical and quantum components in Shor’s algorithm, and the challenges in building optimized quantum arithmetic circuits. Future work will focus on better optimized quantum circuits and the integration of error mitigation.
