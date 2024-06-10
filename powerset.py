from clause import *
from typing import List, Dict
from collections import defaultdict

class PowerSet:
    def __init__(self, nvars: int) -> None:
        self.nvars = nvars
        self.subset_clauses = defaultdict(set)
        self.superset_clauses = defaultdict(set)
        # useful to compute the independent clauses
        self.all = set()
        # initialize the graph with the most specific clause
        c = Clause('1'*nvars)
        self.superset_clauses[c] = set()
        self.build_graph(c)

    def build_graph(self, c_superset: 'Clause') -> None:
        if c_superset not in self.subset_clauses:
            self.subset_clauses[c_superset] = set()
        if c_superset in self.all:
            return
        self.all.add(c_superset)
        if c_superset.get_order() <= 1:
            return
        for c_subset in c_superset.get_subsets():
            if c_subset not in self.superset_clauses:
                self.superset_clauses[c_subset] = set()
            s_tmp = self.subset_clauses[c_superset]
            s_tmp.add(c_subset)
            self.subset_clauses[c_superset] = s_tmp
            s_tmp = self.superset_clauses[c_subset]
            s_tmp.add(c_superset)
            self.superset_clauses[c_subset] = s_tmp
            self.build_graph(c_subset)

    def get_dominated_directly(self, s_clauses: Set['Clause']) -> Set['Clause']:
        s_dominated = set()
        for c in s_clauses:
            s_dominated.update(self.subset_clauses.get(c, set()))
        return s_dominated

    def get_dominant_directly(self, s_clauses: Set['Clause']) -> Set['Clause']:
        s_dominant = set()
        for c in s_clauses:
            s_dominant.update(self.superset_clauses.get(c, set()))
        return s_dominant

    def get_dominated_recursively(self, c: 'Clause', s_seen: Set['Clause']) -> Set['Clause']:
        for c_subset in self.subset_clauses.get(c):
            if c_subset not in s_seen:
                s_seen.add(c_subset)
                s_seen.update(self.get_dominated_recursively(c_subset, s_seen))
        return s_seen

    def get_dominant_recursively(self, c: 'Clause', s_seen: Set['Clause']) -> Set['Clause']:
        for c_superset in self.superset_clauses.get(c, set()):
            if c_superset not in s_seen:
                s_seen.add(c_superset)
                s_seen.update(self.get_dominant_recursively(c_superset, s_seen))
        return s_seen

    def get_independent(self, clauses: Set['Clause']) -> Set['Clause']:
        if not clauses: # If the set is empty
            return { Clause('1'*self.nvars) } # return the maximal clause
        dep_set = set()
        for c in clauses:
            dep_set.update(self.get_dominated_recursively(c, dep_set))
            dep_set.update(self.get_dominant_recursively(c, dep_set))
        s_diff = self.all - clauses - dep_set
        return s_diff

    def get_minimal(self, s_clauses: Set['Clause']) -> Set['Clause']:
        l_clauses = list(s_clauses)
        s_minimal = set()
        for i in range(len(l_clauses)):
            dominates = False
            for j in range(len(l_clauses)):
                if i != j and l_clauses[i] >= l_clauses[j]:
                    dominates = True
                    break
            if not dominates:
                s_minimal.add(l_clauses[i])
        return s_minimal

    def get_maximal(self, s_clauses: Set['Clause']) -> Set['Clause']:
        l_clauses = list(s_clauses)
        s_maximal = set()
        for i in range(len(s_clauses)):
            if any([i != j and l_clauses[j]>=l_clauses[i] for j in range(len(s_clauses))]):
                continue
            s_maximal.add(l_clauses[i])
        return s_maximal

    def __str__(self) -> str:
        s = ""
        for c in self.all:
            s += f"{c}\tSuper: {self.superset_clauses.get(c, set())}\tSub: {self.subset_clauses.get(c, set())}\n"
        return s
