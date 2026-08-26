from .clause import Clause
from .function import Function
from .powerset import PowerSet
from bitarray import bitarray
from typing import Tuple, Set

class HasseDiagram:
    # Dedeking number: number of monotone Boolean functions of n variables:
    #  https://oeis.org/A000372
    # Number of monotone non-degenerate Boolean functions of n variables:
    #  n=2 ->                                                       2 functions
    #  n=3 ->                                                       9 functions
    #  n=4 ->                                                     114 functions
    #  n=5 ->                                                   6 894 functions
    #  n=6 ->                                               7 785 062 functions
    #  n=7 ->                                       2 414 627 396 434 functions
    #  n=8 ->                          56 130 437 209 370 320 359 966 functions
    #  n=9 -> 286 386 577 668 298 410 623 295 216 696 338 374 471 993 functions

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
        s1Parents = { f.clone_rm_add(set(), { c }) for c in sC }
        
        # Get maximal dominated clauses
        lD = [d for d in self.powerset.get_maximal( \
            self.powerset.get_dominated_directly(f.clauses))\
                   if not any([(d<=s) for s in sC])]

        # Add all parents from the 2nd rule
        sDnotUsed = {}
        for d in lD:
            sContained = d.get_containing(f.clauses)
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
            for l in s.get_off_literals():
                sl = s.clone_add(l)
                sAbsorbed = sl.get_contained(f.clauses)
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
                for l in c.get_off_literals():
                    cl = c.clone_add(l)
                    sAbsorbed = cl.get_contained(fMergeable.clauses)
                    if len(sAbsorbed) == 2:
                        fc = f.clone_rm_add(sAbsorbed, {cl})
                        s3Children.add(fc)
                        #print('fc:',fc, 'R3')
                lmergeable.pop()

        return s1Children, s2Children, s3Children

    def get_f_parents_with_sign_changes(self, f: 'Function', changed_signs: bitarray) -> Tuple[Set['Function'], Set['Function'], Set['Function']]:
        """ Returns the set of immediate parents of f when the variables/regulators
        flagged in changed_signs have switched sign (0->1 or 1->0). """
        if changed_signs.count() == 0:
            raise ValueError('changed_signs must flag at least one variable!')
        if len(changed_signs) != self.nvars:
            raise ValueError('changed_signs must have size ' + str(self.nvars) + '!')

        # S_bullet: clauses of f with all sign-changed literals removed
        sBullet = set()
        for c in f.clauses:
            signature = c.get_signature() & ~changed_signs
            if signature.count() == 0:
                # Existence criterion: no f' exists once a clause becomes empty
                return set(), set(), set()
            sBullet.add(Clause(signature))

        # Keep only the smallest clauses, dropping any that are supersets of another
        sBullet = self.powerset.get_minimal(sBullet)

        # S' = S_bullet union each maximal independent clause of f
        sC = self.powerset.get_maximal(self.powerset.get_independent(sBullet))
        sParents = { Function(self.nvars, sBullet | { c }) for c in sC }

        return sParents, set(), set() # between signature changes only R1 parents are possible

    def get_f_children_with_sign_changes(self, f: 'Function', changed_signs: bitarray) -> Tuple[Set['Function'], Set['Function'], Set['Function']]:
        """ Returns the set of immediate children of f when the variables/regulators
        flagged in changed_signs have switched sign (0->1 or 1->0). """
        if changed_signs.count() == 0:
            raise ValueError('changed_signs must flag at least one variable!')
        if len(changed_signs) != self.nvars:
            raise ValueError('changed_signs must have size ' + str(self.nvars) + '!')

        # Existence criterion: f' exists only if some clause is made up exclusively of unchanged variables
        invariants = { c for c in f.clauses if (c.get_signature() & changed_signs).count() == 0 }
        if not invariants:
            return set(), set(), set()

        # One f' per clause s in invariants: f' = sRest union ext(s)
        sChildren = set()
        for s in invariants:
            sRest = invariants - { s }
            s_ext = s
            for l in s.get_off_literals():
                candidate = s_ext.clone_add(l)
                if all(candidate.is_independent(c) for c in sRest):
                    s_ext = candidate
            if s_ext != s: # s unextended would just recreate f, not a child
                sChildren.add(Function(self.nvars, sRest | { s_ext }))

        return sChildren, set(), set() # between signature changes only R1 children are possible
