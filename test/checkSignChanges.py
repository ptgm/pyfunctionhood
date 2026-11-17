"""Brute-force check of get_f_parents/children_with_sign_changes.
Closest parents (children) in signature S' = minimal (maximal) 
non-degenerate monotone functions g in S' whose true set contains
(is contained in) the true set of f.

A test case is a pair (f, K): f a non-degenerate monotone function 
over n variables and K a non-empty set of variables whose sign changes.
Number of pairs = #functions * (2^n - 1):

    n    #functions  #K = 2^n - 1   #pairs (f, K)
    2             2             3               6
    3             9             7              63
    4           114            15           1,710
    5         6,894            31         213,714
    6     7,785,062            63     ~4.9 * 10^8
    7  ~2.4 * 10^12           127    ~3.1 * 10^14
    8  ~5.6 * 10^22           255    ~1.4 * 10^25

Exhaustive checking is only feasible up to n=4.
For n>=5 `sample` random (f,K) pairs are checked instead 
(n=5 with 10,000 pairs takes about 30 s and 
covers ~4.7% of the 213,714 pairs; n>=6 sampling vs time will be evident).

Usage: python checkSignChanges.py [maxdim=5] [sample=10000]
  Dimensions 2..maxdim are checked: exhaustively for n<=4, on `sample` random pairs for n>=5.
  sample=0 forces an exhaustive check for every dimension (very slow for n>=5).
"""
import sys, random
from bitarray import bitarray
from pyfunctionhood import HasseDiagram, Function, Clause

def all_functions(n):
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

def true_set(fn, n, K):  # variables in K are negative: literal true iff x_i == 0
    return frozenset(x for x in range(1 << n) if any(((x ^ K) & s) == s for s in fn))

def to_fn(n, masks):
    return Function(n, {Clause(bitarray(''.join('1' if (m >> i) & 1 else '0' for i in range(n)))) for m in masks})

def from_fn(f):
    return frozenset(sum(1 << i for i in c.get_on_literals()) for c in f.get_clauses())

def check(n, sample=None):
    funcs = all_functions(n); hd = HasseDiagram(n); bad = tot = 0
    Tpos = {f: true_set(f, n, 0) for f in funcs}
    if sample is None:  # exhaustive
        pairs = {K: funcs for K in range(1, 1 << n)}
    else:  # random (f,K) pairs, grouped by K so that each Tk is computed once
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
                bad += 1; print('MISMATCH n=%d K=%d f=%s' % (n, K, sorted(f)))
    print('n=%d: %d (f,K) pairs, %d mismatches' % (n, tot, bad))
    return bad

if __name__ == '__main__':
    maxdim = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    sample = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
    sys.exit(1 if sum(check(n, (sample or None) if n > 4 else None) for n in range(2, maxdim + 1)) else 0)
