from hassediagram import *
import random, time, sys

################## Functions in arXiv paper Fig 5 ##################
#fS1 = Function(n, {Clause('1110'), Clause('1011'), Clause('0111')})
#fS2 = Function(n, {Clause('1110'), Clause('0011')})
#fS3 = Function(n, {Clause('1110'), Clause('1101'), Clause('0011')})
#fS4 = Function(n, {Clause('1010'), Clause('0110'), Clause('0011')})

if len(sys.argv) < 2:
    print('Usage: python', sys.argv[0], '<dim>')
    sys.exit()
n = int(sys.argv[1])
hd = HasseDiagram(n)

#####################################################################
# Testing children vs parents
finf = hd.get_infimum()
fsup = hd.get_supremum()

## Random walk from the infimum to the supremum
tracesz, nR1, nR2, nR3 = 0, 0, 0, 0
f = finf
t1 = time.time()
while f != fsup:
    s1Parents, s2Parents, s3Parents = hd.get_f_parents(f)
    nR1 += len(s1Parents)
    nR2 += len(s2Parents)
    nR3 += len(s3Parents)
    lParents = list(s1Parents)+list(s2Parents)+list(s3Parents)
    # generate a random int to index the set of parents
    i = random.randint(0, len(lParents)-1)
    # check parent children -- begin
    s1Children, s2Children, s3Children = hd.get_f_children(lParents[i])
    if not (f in s1Children or f in s2Children or f in s3Children):
        print('f:', f)
        print('lParents:', lParents)
        print('lP[i]:', lParents[i])
        print('lP[i].children:', sChildren)
        sys.exit()
    # check parent children -- end
    f = lParents[i]
    tracesz += 1
t2 = time.time()
print('Time:', t2-t1)
print('Sz:', tracesz, ' nR1:',nR1, ' nR2:',nR2, ' nR3:',nR3)

## Random walk from the supremum to the infimum
tracesz, nR1, nR2, nR3 = 0, 0, 0, 0
f = fsup
t1 = time.time()
while f != finf:
    s1Children, s2Children, s3Children = hd.get_f_children(f)
    nR1 += len(s1Children)
    nR2 += len(s2Children)
    nR3 += len(s3Children)
    lChildren = list(s1Children)+list(s2Children)+list(s3Children)
    # generate a random int to index the set of children
    i = random.randint(0, len(lChildren)-1)
    # check child parents -- begin
    s1Parents, s2Parents, s3Parents = hd.get_f_parents(lChildren[i])
    if not (f in s1Parents or f in s2Parents or f in s3Parents):
        print('f:', f)
        print('lChildren:', lChildren)
        print('lC[i]:', lChildren[i])
        print('lC[i].parents:', sParents)
        sys.exit()
    # check child parents -- end
    f = lChildren[i]
    tracesz += 1
t2 = time.time()
print('Time:', t2-t1)
print('Sz:', tracesz, ' nR1:',nR1, ' nR2:',nR2, ' nR3:',nR3)
