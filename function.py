from typing import Set, List
from bitarray import bitarray
from clause import *

class Function:
    def __init__(self, nvars:int, clauses: Set['Clause']) -> None:
        if not clauses:
            raise ValueError("Empty set of clauses!")
        if nvars <= 0 or any(c.get_size() != nvars for c in clauses):
            raise ValueError("All clauses must have the same size!")
        self.nvars = nvars
        self.clauses = clauses
        self.update_consistency()

    def get_size(self) -> int:
        """ Returns the number of variables of the function. """
        return self.nvars

    def get_clauses(self) -> Set['Clause']:
        """ Returns the set of clauses of the function without a copy. """
        return self.clauses

    def is_consistent(self) -> bool:
        """ Returns True if the function is consistent, False otherwise. """
        return self.consistent

    def update_consistency(self) -> None:
        self.consistent = self.has_independent_clauses() and self.is_cover()

    def has_independent_clauses(self) -> bool:
        for c1 in self.clauses:
            for c2 in self.clauses:
                if c1 != c2 and not c1.is_independent(c2):
                    return False
        return True

    def is_cover(self) -> bool:
        bcover = bitarray('0'*self.nvars)
        for c in self.clauses:
            bcover |= c.get_signature()
        return bcover.all()

    def __eq__(self, other: 'Function') -> bool:
        return isinstance(other, Function) and \
                self.nvars == other.nvars and \
                self.clauses == other.clauses

    def add_clause(self, c: 'Clause') -> None:
        self.clauses.add(c)
        self.update_consistency()

    def __hash__(self) -> int:
        return hash(self.clauses)

    def clone_add(self, c: 'Clause') -> 'Function':
        f = Function(self.nvars, self.clauses.copy())
        f.clauses.add(c)
        f.update_consistency()
        return f

    def clone_remove(self, c: 'Clause') -> 'Function':
        f = Function(self.nvars, self.clauses.copy())
        f.clauses.remove(c)
        f.update_consistency()
        return f

    def __str__(self) -> str:
        return "{" + ",".join(str(c) for c in self.clauses) + "}"

    def __repr__(self) -> str:
        return str(self)