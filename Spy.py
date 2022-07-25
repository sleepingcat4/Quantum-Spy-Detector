from unicodedata import decimal
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, execute, Aer, IBMQ, BasicAer
import math

from sympy import N

# Setting up the program
alice = QuantumRegister(1, name='alice')
fiber = QuantumRegister(1, name='fiber')
bob = QuantumRegister(1, name='bob')
alice_had = ClassicalRegister(1, name='ahad')
alice_val = ClassicalRegister(1, name='aval')
bob_had = ClassicalRegister(1, name='bhad')
bob_val = ClassicalRegister(1, name='bval')
# fiber_had = ClassicalRegister(1, name='fhad')
fiber_val = ClassicalRegister(1, name='fval')
qc = QuantumCircuit(alice, fiber, bob, alice_had, alice_val, bob_had, bob_val, fiber_val)

# Use Alice's QPU to generate two random bits
# alice = 0
qc.reset(alice)
qc.h(alice)
qc.measure(alice, alice_had)
# alice = 0
qc.reset(alice)
qc.h(alice)
qc.measure(alice, alice_val)

# Prepare Alice's Qubit
# alice = 0
qc.reset(alice)
qc.x(alice).c_if(alice_val, 1)
qc.h(alice).c_if(alice_had, 1)

# Sending the quibit to Bob
qc.swap(alice, fiber)

# Activating the Spy Hunter
spy = True
if spy:
    qc.barrier()
    qc.h(fiber)
    spy_had = True
    if spy_had:
        qc.h(fiber)
    qc.measure(fiber, fiber_val)
    qc.reset(fiber)
    qc.x(fiber).c_if(fiber_val, 1)
    if spy_had:
        qc.h(fiber)

qc.barrier()

# Use Bob's QPU to generate two random bits
qc.reset(bob)
qc.h(bob)
qc.measure(bob, bob_had)

# receive the quibit from Alice
qc.swap(fiber, bob)
qc.h(bob).c_if(bob_had, 1)
qc.measure(bob, bob_val)

backend = BasicAer.get_backend('statevector_simulator')
job = execute(qc, backend=backend)
result = job.result()
counts = result.get_counts(qc)

# Now Alice emails Bob to tell
# him her had setting and value
# if the had setting matches and the value does not, there's a spy
print('counts: ', counts)
# print('Alice had: ' + str(counts['ahad']))
# print('Alice value: ' + str(counts['aval']))
caught = False
for key, val in counts.items():
    ahad, aval, f, bhad, bval = (int(x) for x in key.split(' '))
    if ahad == bhad:
        if aval != bval:
            print('Caught a spy!')
            caught = True
            # break

if not caught:
    print('No spy!')

output = result.get_statevector(qc, decimals = 3)
print(output)
qc.draw() # drawing the circuit