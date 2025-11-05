from typing import Set
from bitarray import bitarray

class Clause:
    def __init__(self, signature, size=None) -> None:
        if not signature:
            raise ValueError('Invalid signature!')
        if isinstance(signature, str):
            if any(c not in ('0','1') for c in signature) or \
               (size and size != len(signature)):
                raise ValueError('Invalid signature!')
            self.cardinality = len(signature)
            self.signature = bitarray(signature)
        elif isinstance(signature, bitarray):
            if size and size != len(signature):
                raise ValueError('Invalid signature!')
            self.cardinality = len(signature)
            self.signature = signature.copy()
        elif isinstance(signature, list):
            if not size or not isinstance(size, int) or size < 1 or \
            any((i < 1 or i > size) for i in signature):
             raise ValueError('Invalid signature!')
            self.cardinality = size
            self.signature = bitarray('0' * size)
            for i in signature:
                self.signature[i - 1] = True

    def clone_add(self, lit: int) -> 'Clause':
        c = Clause(self.signature)
        c.signature[lit] = True
        return c

    def clone_rm(self, lit: int) -> 'Clause':
        c = Clause(self.signature)
        c.signature[lit] = False
        return c

    def get_size(self) -> int:
        return self.cardinality

    def get_signature(self) -> bitarray:
        return self.signature

    def get_order(self) -> int:
        return self.signature.count()

    def get_off_literals(self) -> list[int]:
        return [i for i in range(self.cardinality) if not self.signature[i]]

    def get_on_literals(self) -> list[int]:
        return [i for i in range(self.cardinality) if self.signature[i]]

    def __hash__(self) -> int:
        """ Hash function for Clause using the signature bit """
        return hash(self.signature.tobytes())

    def get_containing(self, sClauses: Set['Clause']) -> Set['Clause']:
        return { s for s in sClauses if self <= s }

    def get_contained(self, sClauses: Set['Clause']) -> Set['Clause']:
        return { s for s in sClauses if s < self }

    def __eq__(self, other) -> bool:
        return isinstance(other, Clause) and \
                self.cardinality == other.cardinality and \
                self.signature == other.signature

    def __ne__(self, other) -> bool:
        return not self == other

    def __ge__(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        # with list comprehension
        return (~self.signature & c.signature).count() == 0

    def __gt__(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        return self >= c and self != c

    def __le__(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        return (~c.signature & self.signature).count() == 0

    def __lt__(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        return self <= c and self != c

    def is_independent(self, c: 'Clause') -> bool:
        if self.cardinality != c.cardinality:
            raise ValueError("Clauses must have the same cardinality!")
        return not self>=c and not self<=c

    def get_subsets(self) -> Set['Clause']:
        return { self.clone_rm(l) for l in self.get_on_literals() }

    def get_supersets(self) -> Set['Clause']:
        return { self.clone_add(l) for l in self.get_off_literals() }

    def __str__(self) -> str:
        return "{" + ",".join(str(i + 1) for i in range(self.cardinality) if self.signature[i]) + "}"

    def __repr__(self) -> str:
        return str(self)

    def evaluate(self, signs: bitarray, values: bitarray) -> bool:
        # (signs XAND values) AND clause
        # number of 1's must be equal to the number of literals in clause
        return ((~(signs ^ values)) & self.signature).count() == self.signature.count()

