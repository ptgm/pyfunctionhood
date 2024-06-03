from clause import *
from function import *
from hassediagram import *
import random, time, sys

# Testing functions in arXiv paper Fig 5 ##############
#n=4
#fS1 = Function(n, {Clause('1110'), Clause('1011'), Clause('0111')})
#fS2 = Function(n, {Clause('1110'), Clause('0011')})
#fS3 = Function(n, {Clause('1101'), Clause('1010'), Clause('0110'), Clause('0011')})
#fS4 = Function(n, {Clause('1010'), Clause('0110'), Clause('0011')})

n=3
hd = HasseDiagram(n)
#print('Parents[',fS1,']:',hd.get_f_parents(fS1))
#print('Childrens[',fS3,']:',hd.get_f_children(fS3))
f1 = Function.fromString(n, '{{2,3},{1}}')
print('f1:', f1)
print('fChildren:', hd.get_f_children(f1))
sys.exit()
#####################################################################
# Testing children vs parents
hd = HasseDiagram(3)

## Random walk from the infimum to the supremum
tracesz = 0
finf = hd.get_infimum()
fsup = hd.get_supremum()
f = finf
t1 = time.time()
while f != fsup:
    print('-----------------------------------')
    print('f:',f)
    sParents, _, _, _ = hd.get_f_parents(f)
    lParents = list(sParents)
    print('lP:',lParents)
    # generate a random int to index the set of parents
    i = random.randint(0, len(lParents)-1)
    print('lP['+str(i)+']:',lParents[i])
    # check parent children -- begin
    sChildren, _, _, _ = hd.get_f_children(lParents[i])
    print('sC:',sChildren)
    if f not in sChildren:
        print('.f:', f)
        print('.lP[i]:', lParents[i])
        print('.lP[i].children:', sChildren)
        sys.exit()
    # check parent children -- end
    f = lParents[i]
    tracesz += 1
t2 = time.time()
print('Time:', t2-t1)
print('Sz:', tracesz)