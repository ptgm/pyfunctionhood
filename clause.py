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

    def __eq__(self, other: 'Clause') -> bool:
        return isinstance(other, Clause) and \
                self.cardinality == other.cardinality and \
                self.signature == other.signature

    def getContainedIn(self, sClauses: Set['Clause']) -> Set['Clause']:
        containedIn = set()
        for s in sClauses:
            if self.le(s):
                containedIn.add(s)
        return containedIn
    
    def ge(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        # with list comprehension
        return all((self.signature[i] or not c.signature[i]) for i in range(self.cardinality))

    def gt(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        return self.ge(c) and not self.__eq__(c)

    def le(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        return c.ge(self)

    def lt(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        return c.gt(self)

    def is_independent(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        return not self.ge(c) and not self.le(c)

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
