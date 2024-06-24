from typing import Set
from bitarray import bitarray

class Clause:
    def __init__(self, str_signature: str) -> None:
        if not str_signature or any(c not in ('0','1') for c in str_signature):
            raise ValueError("Invalid signature!")
        self.cardinality = len(str_signature)
        self.signature = bitarray(str_signature)

    def clone_add(self, lit: int) -> 'Clause':
        c = Clause(self.signature.to01())
        c.signature[lit] = True
        return c
    
    def get_size(self) -> int:
        return self.cardinality

    def get_signature(self) -> bitarray:
        return self.signature

    def get_order(self) -> int:
        return self.signature.count()

    def has_some_literal(self, c: 'Clause') -> bool:
        return any(self.signature[i] and c.signature[i] \
                   for i in range(self.cardinality))
    
    def missing_literals(self) -> list[int]:
        return [i for i in range(self.cardinality) if not self.signature[i]]

    def __hash__(self) -> int:
        """ Hash function for Clause using the signature bit """
        return hash(self.signature.tobytes())

    def get_containing(self, sClauses: Set['Clause']) -> Set['Clause']:
        containing = set()
        for s in sClauses:
            if self <= s:
                containing.add(s)
        return containing

    def get_contained(self, sClauses: Set['Clause']) -> Set['Clause']:
        contained = set()
        for s in sClauses:
            if s != self and s <= self:
                contained.add(s)
        return contained
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Clause) and \
                self.cardinality == other.cardinality and \
                self.signature == other.signature

    def __ge__(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        # with list comprehension
        return all((self.signature[i] or not c.signature[i]) for i in range(self.cardinality))

    def __gt__(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        return self >= c and not self == c

    def __le__(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        return c >= self

    def __lt__(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        return c > self

    def is_independent(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        return not self>=c and not self<=c

    def get_subsets(self) -> Set['Clause']:
        subsets = set()
        for i in range(self.cardinality):
            if self.signature[i]:
                c = Clause(self.signature.to01())
                c.signature[i] = False
                subsets.add(c)
        return subsets
    
    def get_supersets(self) -> Set['Clause']:
        supersets = set()
        for i in range(self.cardinality):
            if not self.signature[i]:
                c = Clause(self.signature.to01())
                c.signature[i] = True
                supersets.add(c)
        return supersets
    
    def __str__(self) -> str:
        return "{" + ",".join(str(i + 1) for i in range(self.cardinality) if self.signature[i]) + "}"

    def __repr__(self) -> str:
        return str(self)
