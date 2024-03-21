from clause import *
from function import *
from powerset import *
from hassediagram import *

import random, time

#fS1 = Function(4, {Clause('1110'), Clause('1011'), Clause('0111')})
#fS2 = Function(4, {Clause('1110'), Clause('0011')})
#fS3 = Function(4, {Clause('1101'), Clause('1010'), Clause('0110'), Clause('0011')})
#fS4 = Function(4, {Clause('1010'), Clause('0110'), Clause('0011')})
#fX = Function(4, {Clause('1101'), Clause('1010'), Clause('0110')})
#f=fX
#print(hd.get_f_parents(f))
#print(hd.get_f_children(f))

t1 = time.time()
hd = HasseDiagram(2)

## Random walk from the infimum to the supremum
finf = hd.get_infimum()
fsup = hd.get_supremum()
print("finf:", finf)
print("fsup:", fsup)

t2 = time.time()
print("Time to set up the Hasse diagram:", t2-t1)

print('-------------------------------------------------------')
nfunctions = 1
f = finf
print("f:", f)
while f != fsup:
    fParents = list(hd.get_f_parents(f))
    # generate a random int to index the set of parents
    i = random.randint(0, len(fParents)-1)
    f = fParents[i]
    #print("f:", f)
    nfunctions += 1
print("#functions:", nfunctions)
t3 = time.time()
print("Time to walk from infimum to supremum:", t3-t2)

print('-------------------------------------------------------')
nfunctions = 1
f = fsup
print("f:", f)
while f != finf:
    fChildren = list(hd.get_f_children(f))
    # generate a random int to index the set of children
    i = random.randint(0, len(fChildren)-1)
    f = fChildren[i]
    #print("f:", f)
    nfunctions += 1
print("#functions:", nfunctions)
t4 = time.time()
print("Time to walk from supremum to infimum:", t4-t3)

print('-------------------------------------------------------')
print('-------------------------------------------------------')
print('-------------------------------------------------------')
hd = HasseDiagram(4)
f = Function(4, {Clause('1101'), Clause('1010'), Clause('0111')})
print(f)
print(hd.get_f_parents(f))
#print(hd.get_f_children(f))
