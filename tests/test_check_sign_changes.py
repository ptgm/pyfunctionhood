"""Pytest for sign changes validation using checkSignChanges.

This module contains parameterized tests that validate the correctness of
get_f_parents/children_with_sign_changes by checking against brute-force
exhaustive or sampled (f, K) pairs.
"""
#A test case is a pair (f, K): f a non-degenerate monotone function 
#over n variables and K a non-empty set of variables whose sign changes.
#Number of pairs = #functions * (2^n - 1):
#
# n    #functions  #K = 2^n - 1   #pairs (f, K)
# 2             2             3               6
# 3             9             7              63
# 4           114            15           1,710
# 5         6,894            31         213,714 - tested below for 100 random pairs
# 6     7,785,062            63     ~4.9 * 10^8
# 7  ~2.4 * 10^12           127    ~3.1 * 10^14
# 8  ~5.6 * 10^22           255    ~1.4 * 10^25

import pytest
import sys
import random
from bitarray import bitarray
from pyfunctionhood import HasseDiagram, Function, Clause


def all_functions(n):
    """Generate all non-degenerate monotone functions over n variables."""
    full = (1 << n) - 1
    subsets = sorted(range(1, full + 1), key=lambda s: (bin(s).count('1'), s))
    res = []
    def rec(i, cur):
        if i == len(subsets):
            u = 0
            for c in cur: u |= c
            if u == full: res.append(frozenset(cur))
            return
        rec(i + 1, cur)
        s = subsets[i]
        if all((s & c) != c and (s & c) != s for c in cur):
            cur.append(s); rec(i + 1, cur); cur.pop()
    rec(0, [])
    return res


def true_set(fn, n, K):
    """Compute the true set of a function with sign changes in variables K.
    
    Variables in K are negative: a literal is true iff x_i == 0.
    """
    return frozenset(x for x in range(1 << n) if any(((x ^ K) & s) == s for s in fn))


def to_fn(n, masks):
    """Convert from mask representation to Function object."""
    return Function(n, {Clause(bitarray(''.join('1' if (m >> i) & 1 else '0' for i in range(n)))) for m in masks})


def from_fn(f):
    """Convert from Function object to mask representation."""
    return frozenset(sum(1 << i for i in c.get_on_literals()) for c in f.get_clauses())


def check_dimension(n, sample=None):
    """Check all (f, K) pairs for dimension n.
    
    Args:
        n: number of variables
        sample: if None, do exhaustive check; otherwise randomly sample this many pairs
        
    Returns:
        Tuple of (mismatches, total_pairs_checked)
    """
    hd = HasseDiagram(n)
    bad = tot = 0
    
    if sample is None:  # exhaustive: need all functions
        funcs = all_functions(n)
        Tpos = {f: true_set(f, n, 0) for f in funcs}
        pairs = {K: funcs for K in range(1, 1 << n)}
    else:  # random (f,K) pairs: only generate functions as needed
        funcs = all_functions(n)  # Still need all for comparison, but cache results
        Tpos = {f: true_set(f, n, 0) for f in funcs}
        pairs = {}
        for _ in range(sample):
            pairs.setdefault(random.randrange(1, 1 << n), []).append(random.choice(funcs))
    
    for K, fs in pairs.items():
        Tk = {f: true_set(f, n, K) for f in funcs}
        Kb = bitarray(''.join('1' if (K >> i) & 1 else '0' for i in range(n)))
        for f in fs:
            up = [g for g in funcs if Tpos[f] <= Tk[g]]
            down = [g for g in funcs if Tk[g] <= Tpos[f]]
            mn = {g for g in up if not any(Tk[h] < Tk[g] for h in up)}
            mx = {g for g in down if not any(Tk[g] < Tk[h] for h in down)}
            P, _, _ = hd.get_f_parents_with_sign_changes(to_fn(n, f), Kb)
            C, _, _ = hd.get_f_children_with_sign_changes(to_fn(n, f), Kb)
            tot += 1
            if {from_fn(g) for g in P} != mn or {from_fn(g) for g in C} != mx:
                bad += 1
    
    return bad, tot


@pytest.mark.parametrize("n", [2, 3, 4])
def test_sign_changes_exhaustive(n):
    """Test sign changes with exhaustive checking for n=2,3,4.
    
    For small dimensions (n <= 4), all (f, K) pairs are checked.
    """
    mismatches, total = check_dimension(n, sample=None)
    assert mismatches == 0, f"Found {mismatches} mismatches in {total} (f, K) pairs for n={n}"


@pytest.mark.parametrize("n,sample", [(5, 100)])
def test_sign_changes_sampled(n, sample):
    """Test sign changes with random sampling for larger dimensions.
    
    For n=5 with 100 random (f, K) pairs sampled.
    Note: n=6 would require generating 7.7M functions just to check 1 pair,
    so it's not practical for routine testing.
    """
    mismatches, total = check_dimension(n, sample=sample)
    assert mismatches == 0, f"Found {mismatches} mismatches in {total} sampled (f, K) pairs for n={n} (sample={sample})"



if __name__ == "__main__":
    # Allow running directly with: python -m pytest tests/test_check_sign_changes.py
    pytest.main([__file__, "-v"])
