import random, time, sys, multiprocessing, csv
sys.path.append('../')
from hassediagram import *

def mp_worker(data):
    dHD, trialNum = data[0], data[1]
    t1 = time.time()
    hd = HasseDiagram(dHD)

    ## Random walk from the infimum to the supremum
    finf = hd.get_infimum()
    fsup = hd.get_supremum()

    tracesz, nR1, nR2, nR3 = 1, 0, 0, 0
    f = finf
    while f != fsup:
        s1Parents, s2Parents, s3Parents = hd.get_f_parents(f)
        nR1 += len(s1Parents)
        nR2 += len(s2Parents)
        nR3 += len(s3Parents)
        lParents = list(s1Parents)+list(s2Parents)+list(s3Parents)
        # generate a random int to index the set of parents
        i = random.randint(0, len(lParents)-1)
        f = lParents[i]
        tracesz += 1
    t2 = time.time()
    return (trialNum, dim, tracesz, t2-t1, nR1, nR2, nR3)

# read arguments from command line
suffix = sys.argv[1]
nthreads = int(sys.argv[2])
dim = int(sys.argv[3])
nTrials = int(sys.argv[4])

# each process will consider as data the following tuple: (dim, trialNum)
data_list = [(dim, trialNum+1) for trialNum in range(nTrials)]

with multiprocessing.Pool(nthreads) as p:
    with open('results_n' + str(dim) + '_r' + str(nTrials) + '_' + suffix + '.txt', 'a') as fh:
        writer = csv.writer(fh, lineterminator='\n', delimiter='\t')
        for result in p.imap_unordered(mp_worker, data_list):
            print("Result:",result)
            writer.writerow(result)

print("Done!")