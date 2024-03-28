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

    def get_f_parents(self, f: 'Function') -> Tuple[Set['Function'], int, int, int]:
        """ Returns the set of immediate parents of f. """
        fParents = set()
        nR1, nR2, nR3 = 0, 0, 0
        # Get maximal independent clauses
        sC = self.powerset.get_maximal(self.powerset.get_independent(f.clauses))

        # Add all parents from the 1st rule
        for c in sC:
            fp = f.clone_rm_add(set(), {c})
            #print('fp:',fp, 'R1')
            nR1 += 1
            fParents.add(fp)

        # Get maximal dominated clauses
        lD = [d for d in self.powerset.get_maximal( \
            self.powerset.get_dominated_directly(f.clauses))\
                   if not any([d.le(s) for s in sC])]
        sD = set(lD)
        #print('lD:', lD)

        # Add all parents of the 2nd and 3rd form
        for d in lD: # TODO Check if ok, or have two sets
            if d not in sD: continue
            sContained = d.getContainedIn(f.clauses)
            fp = f.clone_rm_add(sContained, {d})
            if fp.is_consistent():
                #print('fp:',fp,'R2')
                nR2 += 1
                fParents.add(fp)
                sD.remove(d)
            elif len(sContained) == 1:
                sTmp = self.powerset.get_dominated_directly(sContained)\
                    .intersection(sD)
                sTmp.remove(d)
                for elem in sTmp:
                    fp = f.clone_rm_add(sContained, {d,elem})
                    fParents.add(fp)
                    nR3 += 1
                    #print('fp:',fp, 'R3')
                sD.remove(d)
        return fParents, nR1, nR2, nR3
    
    def get_f_children(self, f: 'Function') -> Set['Function']:
        """ Returns the set of immediate children of f. """
        fChildren, dmergeable = set(), {}
        
        # Add all children of the 1st form
        for s in f.clauses:
            bMergeCand = False
            for l in s.missing_literals():
                sl = s.clone_add(l)
                sAbsorbed = f.getAbsorbed(sl)
                if len(sAbsorbed) == 1:
                    fc = f.clone_rm_add({s}, {sl})
                    if fc.is_consistent():
                        #print('fc:',fc, 'R1')
                        fChildren.add(fc)
                elif len(sAbsorbed) == 2:
                    bMergeCand = True
            if bMergeCand:
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
                    #print('c:',c, 'l:',l+1, 'cl:',cl, 'sAbsorbed:',sAbsorbed)
                    if len(sAbsorbed) == 2:
                        fc = f.clone_rm_add(sAbsorbed, {cl})
                        #print('fc:',fc, 'R3')
                        fChildren.add(fc)
                lmergeable.pop()

        return fChildren