#!/usr/bin/env python3
"""Reproduces fig_sc_neighbourhood.pdf: size of the neighbourhood of a function across signatures, versus the
number k of simultaneous sign changes:
  (a) fraction of the C(n,k) target signatures that contain a closest relative,
  (b) average number of closest relatives in a target signature that contains at least one,
  (c) total number of closest relatives summed over all C(n,k) target signatures.
Parents: solid; children: dashed; empty squares: same-signature immediate relatives (k=0).

Requirements:   pip install pyfunctionhood matplotlib      (pyfunctionhood pulls in bitarray)

Usage
  python fig_sc_neighbourhood.py                      # plot from the data in ./results
  python fig_sc_neighbourhood.py --run                # compute the MISSING points, then plot
  python fig_sc_neighbourhood.py --run --workers 4    # ... on 4 processes
  python fig_sc_neighbourhood.py --run --nmax 7       # skip n=8 (by far the slowest)
  python fig_sc_neighbourhood.py --run --n 6 --k 3 4 --force     # recompute only the points (6,3) and (6,4)

One file is written per point (n,k), named   <data>/neigh_n<n>_k<k>_s<samples>.txt   (k=0: same-signature baseline),
written atomically when the point is complete and never overwritten unless --force is given.  The number of random
walks <samples> is part of the name (so changing it computes new points).  Tab-separated columns, one row per
visited function f:
  sample, n, step, k, n_signatures, p_exists, n_parents, c_exists, n_children
i.e. for the C(n,k) sets K of size k: how many of them admit a closest parent / child and how many closest
parents / children there are in total (k=0: the same-signature immediate parents / children, n_signatures=1).

Experiment: for each dimension n, `samples` random walks from the infimum to the supremum (through same-signature
parents) provide the functions f; the walks are seeded by (n, sample), so every point (n,k) uses the same functions
(and the same walks as fig_sc_cost.py).  For every visited f and EVERY set K of k sign changes we record whether a
closest parent / child exists and how many there are.  Default number of walks: 100 for n<=6, 40 for n=7, 20 for n=8
(n=8 takes about a minute per walk and needs 2^8-1 calls per visited function); --samples N uses N for every n.

Legacy files results_scC_n<n>_r<samples>.txt (one file per n, as written by earlier versions) are still read
when the data directory contains no per-point files, e.g. `--data results_sc`.
"""
import argparse, csv, glob, itertools, multiprocessing, os, random, re
from collections import defaultdict

DEFAULT_SAMPLES = {2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 40, 8: 20}

# ----------------------------------------------------------------------------- experiment
def _measure(job):
    """Counts of point (n,k) for the functions of walk number `sample`."""
    from bitarray import bitarray
    from pyfunctionhood import HasseDiagram
    n, k, sample = job
    walk = random.Random('walk-%d-%d' % (n, sample))              # same walk for every k, in every run
    hd = HasseDiagram(n)
    finf, fsup = hd.get_infimum(), hd.get_supremum()
    rows, f, step = [], finf, 0
    while True:
        P = hd.get_f_parents(f)
        if k == 0:                                                # same-signature baseline
            C = hd.get_f_children(f)
            np_, nc = sum(map(len, P)), sum(map(len, C))
            rows.append((sample, n, step, 0, 1, int(np_ > 0), np_, int(nc > 0), nc))
        else:
            a = [0, 0, 0, 0, 0]                                   # nsig, p_exists, n_par, c_exists, n_chi
            for K in itertools.combinations(range(n), k):
                bits = bitarray(n)
                bits.setall(0)
                for i in K:
                    bits[i] = 1
                sp, _, _ = hd.get_f_parents_with_sign_changes(f, bits)
                sc, _, _ = hd.get_f_children_with_sign_changes(f, bits)
                a[0] += 1
                a[1] += int(len(sp) > 0); a[2] += len(sp)
                a[3] += int(len(sc) > 0); a[4] += len(sc)
            rows.append((sample, n, step, k, *a))
        if f == fsup:
            break
        f = walk.choice(sorted((g for part in P for g in part), key=str))   # sorted: reproducible walk
        step += 1
    return (n, k, sample), rows

def samples_for(n, override):
    return override or DEFAULT_SAMPLES[n]

def point_file(data, n, k, samples):
    return os.path.join(data, 'neigh_n%d_k%d_s%d.txt' % (n, k, samples))

def run(data, ns, ks, override, workers, force):
    os.makedirs(data, exist_ok=True)
    points = [(n, k) for n in ns for k in range(0, n + 1) if ks is None or k in ks]
    todo = [(n, k) for n, k in points if force or not os.path.exists(point_file(data, n, k, samples_for(n, override)))]
    print('%d of %d points to compute (%d already exist)' % (len(todo), len(points), len(points) - len(todo)), flush=True)
    if not todo:
        return
    todo.sort(key=lambda p: (-p[0], p[1]))                        # slowest first: better load balance
    jobs = [(n, k, s + 1) for n, k in todo for s in range(samples_for(n, override))]
    part, left = defaultdict(list), {(n, k): samples_for(n, override) for n, k in todo}
    with multiprocessing.Pool(workers) as pool:
        for (n, k, s), rows in pool.imap_unordered(_measure, jobs):
            part[(n, k)] += rows
            left[(n, k)] -= 1
            if left[(n, k)] == 0:                                 # point complete: write it atomically
                fname = point_file(data, n, k, samples_for(n, override))
                with open(fname + '.tmp', 'w') as fh:
                    csv.writer(fh, lineterminator='\n', delimiter='\t').writerows(sorted(part.pop((n, k))))
                os.replace(fname + '.tmp', fname)
                print('wrote', fname, flush=True)

# ----------------------------------------------------------------------------- plot
def load(data, override, ns):
    C = defaultdict(lambda: [0, 0, 0, 0, 0, 0])                   # (n,k) -> nsig, p_exists, n_par, c_exists, n_chi, rows
    def add(fn):
        with open(fn) as fh:
            for r in csv.reader(fh, delimiter='\t'):
                _, n, _, k, ns_, pe, npar, ce, nc = map(int, r)
                a = C[(n, k)]
                for i, v in enumerate((ns_, pe, npar, ce, nc, 1)):
                    a[i] += v
    found = [(n, k) for n in ns for k in range(n + 1) if os.path.exists(point_file(data, n, k, samples_for(n, override)))]
    if found:
        for n, k in found:
            add(point_file(data, n, k, samples_for(n, override)))
        missing = [(n, k) for n in ns for k in range(n + 1) if (n, k) not in set(found)]
        if missing:
            print('WARNING: %d points missing (not plotted): %s' % (len(missing), ' '.join('n%d_k%d' % p for p in missing)))
    else:                                                         # legacy: one file per n
        legacy = sorted(glob.glob(os.path.join(data, 'results_scC_n*_r*.txt')))
        if not legacy:
            raise SystemExit('no data in %s (use --run, or --data DIR)' % data)
        for fn in legacy:
            add(fn)
    return C

def plot(C, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MaxNLocator

    color = lambda n: 'C%d' % (n - 2)
    nan = float('nan')
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for n in range(2, 9):
        ks = sorted(k for (nn, k) in C if nn == n)
        if not ks:
            continue
        c, a = color(n), (lambda k: C[(n, k)])
        ex_p  = [a(k)[1] / a(k)[0] for k in ks]
        ex_c  = [a(k)[3] / a(k)[0] for k in ks]
        cnd_p = [a(k)[2] / a(k)[1] if a(k)[1] else nan for k in ks]
        cnd_c = [a(k)[4] / a(k)[3] if a(k)[3] else nan for k in ks]
        tot_p = [a(k)[2] / a(k)[5] if a(k)[2] else nan for k in ks]
        tot_c = [a(k)[4] / a(k)[5] if a(k)[4] else nan for k in ks]
        has0 = ks[0] == 0
        for ax, yp, yc in [(axes[0], ex_p, ex_c), (axes[1], cnd_p, cnd_c), (axes[2], tot_p, tot_c)]:
            first = 1 if has0 else 0
            ax.plot(ks[first:], yp[first:], '-o', color=c, label='p=%d' % n)
            ax.plot(ks[first:], yc[first:], '--^', color=c)
            if has0:
                if len(ks) > 1 and ks[1] == 1:                    # dotted link k=0 -> k=1, as in fig_sc_cost
                    ax.plot(ks[:2], yp[:2], ':', color=c)
                    ax.plot(ks[:2], yc[:2], ':', color=c)
                ax.plot(ks[0], yp[0], 's', mfc='white', color=c)  # k=0 baseline, parents
                ax.plot(ks[0], yc[0], 's', mfc='white', color=c)  # k=0 baseline, children
    axes[2].set_yscale('log')
    ylabels = ['Fraction of target signatures\nwith a closest relative',
               'Closest relatives per signature\n(when one exists)',
               'Closest relatives summed over\nall C(n,k) target signatures']
    for ax, yl in zip(axes, ylabels):
        ax.set_xlabel('# of simultaneous sign changes (k)'); ax.set_ylabel(yl)
        ax.grid(True, which='both', linestyle=':')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    axes[0].legend(loc='upper right')
    axes[1].legend([Line2D([], [], color='k', marker='o'), Line2D([], [], color='k', ls='--', marker='^'),
                    Line2D([], [], color='k', marker='s', mfc='white', ls='')],
                   ['parents', 'children', 'k=0 (same signature)'], loc='upper right')
    fig.tight_layout()
    os.makedirs(out, exist_ok=True)
    for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(out, 'fig_sc_neighbourhood.' + ext), dpi=200)
    print('saved', os.path.join(out, 'fig_sc_neighbourhood.pdf'))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--run', action='store_true', help='compute the missing points before plotting')
    ap.add_argument('--force', action='store_true', help='recompute the selected points even if their file exists')
    ap.add_argument('--data', default='results', help='directory of the point files (default: results)')
    ap.add_argument('--out', default='.', help='directory for fig_sc_neighbourhood.pdf/.png (default: .)')
    ap.add_argument('--samples', type=int, default=None,
                    help='random walks per dimension (default: 100 for n<=6, 40 for n=7, 20 for n=8)')
    ap.add_argument('--nmax', type=int, default=8, help='largest dimension; dimensions are 2..nmax (default 8)')
    ap.add_argument('--n', type=int, nargs='+', help='only these dimensions, each >= 2 (with --run); for all dimensions up to N use --nmax N')
    ap.add_argument('--k', type=int, nargs='+', help='only these numbers of sign changes, 0 = baseline (with --run)')
    ap.add_argument('--workers', type=int, default=2, help='processes (default 2)')
    a = ap.parse_args()
    ns = a.n or list(range(2, a.nmax + 1))
    if any(n < 2 or n > 8 for n in ns):
        ap.error('dimensions must be between 2 and 8; for all dimensions up to N use --nmax N (e.g. --nmax 5)')
    if a.k and (min(a.k) < 0 or max(a.k) > max(ns)):
        ap.error('--k values must be between 0 and the largest dimension')
    if a.run:
        run(a.data, ns, set(a.k) if a.k else None, a.samples, a.workers, a.force)
    plot(load(a.data, a.samples, list(range(2, a.nmax + 1))), a.out)
