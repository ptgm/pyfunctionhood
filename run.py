from clause import *
from function import *
from powerset import *
from hassediagram import *

import sys
import random, time

maxNvars = int(sys.argv[1])
nRuns = int(sys.argv[2])
lTimes, lDepth = {}, {}

for dim in range(2, maxNvars+1):
    hd = HasseDiagram(dim)
    lTimes[dim], lDepth[dim] = [], []

    ## Random walk from the infimum to the supremum
    finf = hd.get_infimum()
    fsup = hd.get_supremum()

    for i in range(nRuns):
        ts = time.time()
        nfunctions = 1
        f = finf
        while f != fsup:
            fParents = list(hd.get_f_parents(f))
            # generate a random int to index the set of parents
            i = random.randint(0, len(fParents)-1)
            f = fParents[i]
            #print("f:", f)
            nfunctions += 1
        tf = time.time()
        lTimes[dim].append(tf-ts)
        lDepth[dim].append(nfunctions)

for i in range(2, maxNvars+1):
    for j in range(nRuns):
        print(i, lTimes[i][j], lDepth[i][j])