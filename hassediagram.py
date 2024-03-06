from clause import *
from function import *
from powerset import *

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

    def get_f_parents(self, f: 'Function') -> Set['Function']:
        """ Returns the set of immediate parents of f. """
        fparents = set()
        cMaxIndpt = self.powerset.get_maximal(self.powerset.get_independent(f.clauses))

        # Add all parents of the 1st form
        for c in cMaxIndpt:
            fp = f.clone_add_rm({c}, set())
            print('fp:',fp, 'R1')
            fparents.add(fp)
        
        # Get maximal dominated clauses
        cMaxDom = [c for c in self.powerset.get_dominated_directly(f.clauses)\
                   if not any([c.le(sp) for sp in cMaxIndpt])]
        # Exclude maximal dominated, dominated by other maximal dominated
        cMaxDom = [c for c in cMaxDom if not any([c.le(sp) for sp in cMaxDom if sp != c])]
        print('cMaxDom:',cMaxDom)

        # Add all parents of the 2nd and 3rd form
        for sp in cMaxDom:
            cRm = [c for c in f.clauses if sp.lt(c)]
            fp = f.clone_add_rm({sp}, cRm)
            if fp.is_consistent(): # If it's a cover: 2nd form
                print('fp:',fp, 'R2')
                fparents.add(fp)
            elif len(fp.clauses) == len(f.clauses):
                cMissingLits = fp.get_missing_lits()
                print('sp:', sp, '  cMissingLits:',cMissingLits)
                for spp in cMaxDom:
                    if sp != spp and spp.has_literal(cMissingLits):
                        fpp = fp.clone_add_rm({spp}, set())
                        if fpp.is_consistent(): # If it's a cover: 3rd form
                            # Though pair (sp,spp) may appear again as (spp,sp)
                            # it's not a problem because fparents is a set
                            print('fp:',fpp, 'R3')
                            fparents.add(fpp)
        return fparents
    