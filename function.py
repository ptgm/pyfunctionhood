from clause import *
from typing import Set

class Function:
    def __init__(self, nvars:int, clauses: Set['Clause']) -> None:
        if not clauses:
            raise ValueError('Empty set of clauses!')
        if nvars <= 0 or any(c.get_size() != nvars for c in clauses):
            raise ValueError('One clause has size !=' + str(nvars)+'!')
        self.nvars = nvars
        self.clauses = clauses
        self.update_consistency()
    
    @staticmethod
    def fromString(nvars: int, strClauses: str) -> 'Function':
        strClauses = strClauses.replace(' ', '')
        if not strClauses:
            raise ValueError('Empty function string!')
        clauses = set()
        for strc in strClauses[2:-2].split('},{'):
            if not strc:
                raise ValueError('Empty clause!')
            tmp = '0'*nvars
            for l in strc.split(','):
                tmp = tmp[:int(l)-1] + '1' + tmp[int(l):]
            clauses.add(Clause(tmp))
        return Function(nvars, clauses)

    def clone_rm_add(self, scRm: Set['Clause'], scAdd: Set['Clause']) -> 'Function':
        f = Function(self.nvars, self.clauses.copy())
        for c in scRm: f.clauses.remove(c)
        for c in scAdd: f.clauses.add(c)
        f.update_consistency()
        return f
    
    def add_clause(self, c: 'Clause') -> None:
        self.clauses.add(c)
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
        self.consistent = self.is_independent() and self.is_cover()

    def is_independent(self) -> bool:
        return all(c1.is_independent(c2) for c1 in self.clauses for c2 in self.clauses if c1 != c2)

    def is_cover(self) -> bool:
        bcover = bitarray('0'*self.nvars)
        for c in self.clauses:
            bcover |= c.get_signature()
        return bcover.all()

    def __eq__(self, other) -> bool:
        return isinstance(other, Function) and \
                self.nvars == other.nvars and \
                self.clauses == other.clauses

    def __hash__(self) -> int:
        # Combine the hashes of the elements using XOR
        hash_value = 0
        for c in self.clauses:
            hash_value ^= hash(c)
        return hash_value

    def __str__(self) -> str:
        return '{' + ','.join(sorted([str(c) for c in self.clauses])) + '}'

    def __repr__(self) -> str:
        return str(self)

    def evaluate(self, signs: bitarray, values: bitarray) -> bool:
        return any(c.evaluate(signs, values) for c in self.clauses)

    def get_level(self) -> list[int]:
        return sorted([(self.nvars - c.get_order()) for c in self.clauses], reverse=True)

    def level_cmp(self, other: 'Function') -> int:
        lself, lother = self.get_level(), other.get_level()
        szself, szother = len(lself), len(lother)

        # Compare element by element
        for i in range(min(szself, szother)):
            if   lself[i] > lother[i]: return 1
            elif lself[i] < lother[i]: return -1

        if   szself  < szother: return -1
        elif szself == szother: return  0
        else:                   return  1

