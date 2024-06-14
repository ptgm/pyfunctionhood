from clause import *
from function import *
from powerset import *
from typing import Tuple

class HasseDiagram:
    # Dedeking number: number of monotone Boolean functions of n variables:
    #   https://oeis.org/A000372
    # Number of monotone non-degenerate Boolean functions of n variables:
	# n=2 ->                                                       2 functions
	# n=3 ->                                                       9 functions
	# n=4 ->                                                     114 functions
	# n=5 ->                                                   6.894 functions
	# n=6 ->                                               7.785.062 functions
	# n=7 ->                                       2.414.627.396.434 functions
	# n=8 ->                          56.130.437.209.370.320.359.966 functions
    # n=9 ->                                                     ... functions

    def __init__(self, nvars: int) -> None:
        self.nvars = nvars
        self.powerset = PowerSet(nvars)

    def get_infimum(self) -> 'Function':
        """ Returns the infimum of the set of functions. """
        return Function(self.nvars, { Clause('1'*self.nvars) })
    
    def get_supremum(self) -> 'Function':
        """ Returns the supremum of the set of functions. """
        return Function(self.nvars,
            { Clause('0'*i + '1' + '0'*(self.nvars - 1 - i))
              for i in range(self.nvars) } )

    def get_size(self) -> int:
        """ Returns the number of variables of the Hasse diagram. """
        return self.nvars

    def get_f_parents(self, f: 'Function') -> Tuple[Set['Function'], Set['Function'], Set['Function']]:
        """ Returns the set of immediate parents of f. """
        s1Parents, s2Parents, s3Parents = set(), set(), set()

        # Get maximal independent clauses
        sC = self.powerset.get_maximal(self.powerset.get_independent(f.clauses))

        # Add all parents from the 1st rule
        for c in sC:
            fp = f.clone_rm_add(set(), {c})
            s1Parents.add(fp)
            #print('fp:',fp, 'R1')
        
        # Get maximal dominated clauses
        lD = [d for d in self.powerset.get_maximal( \
            self.powerset.get_dominated_directly(f.clauses))\
                   if not any([(d<=s) for s in sC])]

        # Add all parents from the 2nd rule
        sDnotUsed = {}
        for d in lD:
            sContained = d.get_contained_in(f.clauses)
            fp = f.clone_rm_add(sContained, {d})
            if fp.is_consistent():
                s2Parents.add(fp)
                #print('  fp:',fp,'R2')
            else:
                for s in sContained:
                    if s not in sDnotUsed: sDnotUsed[s] = set()
                    sDnotUsed[s].add(d)

        # Add all parents from the 3rd rule
        for s in sDnotUsed:
            lSigmas = list(sDnotUsed[s])
            if len(lSigmas) < 2: # needs at least 2 clauses to be combined
                continue
            for i in range(len(lSigmas)-1):
                for j in range(i + 1, len(lSigmas)):
                    # by def only s contains both sigma_i and sigma_j
                    fp = f.clone_rm_add({s}, {lSigmas[i],lSigmas[j]})
                    # by def no need to test if isCover(fp)
                    s3Parents.add(fp)
                    #print('  fp:',fp, 'R3')

        return s1Parents, s2Parents, s3Parents
    
    def get_f_children(self, f: 'Function') -> Tuple[Set['Function'], Set['Function'], Set['Function']]:
        """ Returns the set of immediate children of f. """
        s1Children, s2Children, s3Children = set(), set(), set()
        dmergeable = {}

        # Add all children of the 1st form
        for s in f.clauses:
            bToMerge, bExtendable = False, False
            # Child function to be extended with: s \cup {l_i}
            fs = f.clone_rm_add({s},set())
            for l in s.missing_literals():
                sl = s.clone_add(l)
                sAbsorbed = f.getAbsorbed(sl)
                if len(sAbsorbed) == 1:
                    bExtendable = True
                    fs = fs.clone_rm_add(set(), {sl})
                elif len(sAbsorbed) == 2:
                    bToMerge = True

            if bExtendable:
                s2Children.add(fs)
                #print('fc:',fs, 'R2')            
            elif fs.is_consistent():
                s1Children.add(fs)
                #print('fc:',fs, 'R1')
            elif bToMerge:
                # Clauses are only (potentially) mergeable with others of their own size
                sz = s.get_order()
                if sz not in dmergeable: dmergeable[sz] = []
                dmergeable[sz].append(s)

        for sz in dmergeable:
            lmergeable = dmergeable[sz]
            while lmergeable:
                c = lmergeable[-1]
                fMergeable = Function(f.get_size(), set(lmergeable))
                for l in c.missing_literals():
                    cl = c.clone_add(l)
                    sAbsorbed = fMergeable.getAbsorbed(cl)
                    if len(sAbsorbed) == 2:
                        fc = f.clone_rm_add(sAbsorbed, {cl})
                        s3Children.add(fc)
                        #print('fc:',fc, 'R3')
                lmergeable.pop()

        return s1Children, s2Children, s3Children
