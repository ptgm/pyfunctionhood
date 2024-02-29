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

        for c in cMaxIndpt:
            fparents.add(f.clone_add(c)) # Parents of 1st Form
        
        cMaxDom = self.powerset.get_dominated_directly(f.clauses)
        for s in f.clauses:
            sDom = self.powerset.get_dominated_directly({s})
            for sp in sDom:
                if sp in cMaxDom: # TODO isIncludedIn(sp, cMaxIndpt)
                    sDom.remove(sp)
            sVisited = set()
            for sp in sDom:
                sVisited.add(sp)
                fp = (f.clone_remove(s)).add_clause(sp)
                fp.update_consistency()
                if fp.is_cover():
                    fparents.add(fp) # Parents of 2nd Form
                elif len(fp.clauses) == len(f.clauses):
                    
                    



        return fparents