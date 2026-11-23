#!/usr/bin/env python3
"""Reproduces fig_sc_cost.pdf: average time per call of the closest-parents / closest-children
algorithms across signatures, versus the number k of simultaneous sign changes (k=0: same-signature
algorithms on the same functions).

Requirements:   pip install pyfunctionhood matplotlib      (pyfunctionhood pulls in bitarray)

Usage
  python fig_sc_cost.py                       # plot from the data in ./results
  python fig_sc_cost.py --run                 # compute the MISSING points, then plot
  python fig_sc_cost.py --run --workers 4     # ... on 4 processes
  python fig_sc_cost.py --run --n 6 --k 3 4 --force     # recompute only the points (6,3) and (6,4)
  python fig_sc_cost.py --run --samples 10 --reps 10 --batch 10 --nmax 8 --data results

One file is written per point (n,k), named   <data>/n<n>_k<k>_s<samples>_r<reps>_b<batch>.txt   (k=0: same-signature
baseline), written atomically when the point is complete and never overwritten unless --force is given.  The
parameters are part of the name, so changing --samples/--reps/--batch computes new points instead of silently
reusing old ones.  Tab-separated columns:
  sample, n, level, k, rep, t_parents, n_parents, t_children, n_children

What is timed: for each dimension n, a pool of functions is sampled by `samples` random walks from the infimum to the
supremum through same-signature parents (the walk itself is not timed).  The walks are seeded by (n, sample), so every
point (n,k) is measured on the very same functions, and a recomputed point reuses them.  At every visited f, `reps`
random sets K of k sign changes are drawn, and each measurement is the mean time of `batch` consecutive calls (a
single call lasts only a few microseconds, comparable to the timer overhead).  For k=0 the same-signature algorithms
get_f_parents / get_f_children are timed instead.  The plotted value is the mean over all measurements of a point.
Timings depend on the machine; avoid --workers larger than the number of physical cores.

Legacy files results_scA_n<n>_r<samples>.txt (one file per n, as written by earlier versions) are still read
when the data directory contains no per-point files, e.g. `--data results_sc`.
"""
import argparse, csv, glob, multiprocessing, os, random, re, time
from collections import defaultdict

# ----------------------------------------------------------------------------- measurement
def _measure(job):
    """All measurements of point (n,k) on the functions of walk number `sample`."""
    from bitarray import bitarray
    from pyfunctionhood import HasseDiagram
    n, k, sample, reps, batch = job
    walk = random.Random('walk-%d-%d' % (n, sample))              # same walk for every k, in every run
    rng = random.Random()                                         # sets K: fresh randomness
    hd = HasseDiagram(n)
    finf, fsup = hd.get_infimum(), hd.get_supremum()
    rows, f = [], finf
    while f != fsup:
        P = hd.get_f_parents(f)
        level = len(f.get_clauses())
        for rep in range(reps):
            if k == 0:                                            # same-signature baseline
                t = time.perf_counter()
                for _ in range(batch): sp = hd.get_f_parents(f)
                tp = (time.perf_counter() - t) / batch
                t = time.perf_counter()
                for _ in range(batch): sc = hd.get_f_children(f)
                tc = (time.perf_counter() - t) / batch
                rows.append((sample, n, level, 0, rep, tp, sum(map(len, sp)), tc, sum(map(len, sc))))
            else:
                K = bitarray(n)
                K.setall(0)
                for i in rng.sample(range(n), k):
                    K[i] = 1
                t = time.perf_counter()
                for _ in range(batch): sp, _, _ = hd.get_f_parents_with_sign_changes(f, K)
                tp = (time.perf_counter() - t) / batch
                t = time.perf_counter()
                for _ in range(batch): sc, _, _ = hd.get_f_children_with_sign_changes(f, K)
                tc = (time.perf_counter() - t) / batch
                rows.append((sample, n, level, k, rep, tp, len(sp), tc, len(sc)))
        f = walk.choice(sorted((g for part in P for g in part), key=str))   # sorted: reproducible walk
    return (n, k, sample), rows

def point_file(data, n, k, samples, reps, batch):
    return os.path.join(data, 'n%d_k%d_s%d_r%d_b%d.txt' % (n, k, samples, reps, batch))

def run(data, ns, ks, samples, reps, batch, workers, force):
    os.makedirs(data, exist_ok=True)
    points = [(n, k) for n in ns for k in range(0, n + 1) if ks is None or k in ks]
    todo = [(n, k) for n, k in points if force or not os.path.exists(point_file(data, n, k, samples, reps, batch))]
    print('%d of %d points to compute (%d already exist)' % (len(todo), len(points), len(points) - len(todo)), flush=True)
    if not todo:
        return
    todo.sort(key=lambda p: (-p[0], p[1]))                        # slowest first: better load balance
    jobs = [(n, k, s + 1, reps, batch) for n, k in todo for s in range(samples)]
    part, left = defaultdict(list), {p: samples for p in todo}
    with multiprocessing.Pool(workers) as pool:
        for (n, k, s), rows in pool.imap_unordered(_measure, jobs):
            part[(n, k)] += rows
            left[(n, k)] -= 1
            if left[(n, k)] == 0:                                 # point complete: write it atomically
                fname = point_file(data, n, k, samples, reps, batch)
                with open(fname + '.tmp', 'w') as fh:
                    csv.writer(fh, lineterminator='\n', delimiter='\t').writerows(sorted(part.pop((n, k))))
                os.replace(fname + '.tmp', fname)
                print('wrote', fname, flush=True)

# ----------------------------------------------------------------------------- plot
def load(data, samples, reps, batch, ns):
    A = defaultdict(lambda: defaultdict(list))                    # (n, 'p'|'c') -> k -> [time]
    def add(fn):
        with open(fn) as fh:
            for r in csv.reader(fh, delimiter='\t'):
                _, dim, _, k, _, tp, _, tc, _ = map(float, r)
                A[(int(dim), 'p')][int(k)].append(tp)
                A[(int(dim), 'c')][int(k)].append(tc)
    pat = re.compile(r'n(\d+)_k(\d+)_s%d_r%d_b%d\.txt$' % (samples, reps, batch))
    files = [fn for fn in glob.glob(os.path.join(data, 'n*_k*_s*_r*_b*.txt')) if pat.match(os.path.basename(fn))]
    if files:
        for fn in files:
            add(fn)
        have = {(int(m.group(1)), int(m.group(2))) for m in map(pat.match, map(os.path.basename, files))}
        missing = [(n, k) for n in ns for k in range(n + 1) if (n, k) not in have]
        if missing:
            print('WARNING: %d points missing (not plotted): %s' % (len(missing), ' '.join('n%d_k%d' % p for p in missing)))
    else:                                                         # legacy: one file per n
        legacy = sorted(glob.glob(os.path.join(data, 'results_scA_n*_r*.txt')))
        if not legacy:
            raise SystemExit('no data for samples=%d reps=%d batch=%d in %s (use --run, or --data DIR)' % (samples, reps, batch, data))
        for fn in legacy:
            add(fn)
    return A

def plot(A, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MaxNLocator

    color = lambda n: 'C%d' % (n - 2)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
    for ax, key in [(axes[0], 'p'), (axes[1], 'c')]:
        for n in range(2, 9):
            if (n, key) not in A:
                continue
            ks = sorted(A[(n, key)])
            ys = [sum(A[(n, key)][k]) / len(A[(n, key)][k]) for k in ks]
            if ks[0] == 0:                                        # same-signature baseline
                if len(ks) > 1 and ks[1] == 1:
                    ax.plot(ks[:2], ys[:2], ':', color=color(n))
                ax.plot(ks[0], ys[0], 's', mfc='white', color=color(n))
                ks, ys = ks[1:], ys[1:]
            ax.plot(ks, ys, marker='o', color=color(n), label='n=%d' % n)
        ax.set_yscale('log')
        ax.set_xlabel('# of simultaneous sign changes (k)')
        ax.set_ylabel('Avg time per call (s)')
        ax.grid(True, which='both', linestyle=':')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        h, l = ax.get_legend_handles_labels()
        ax.legend(handles=h + [Line2D([], [], color='k', marker='s', mfc='white', ls='')],
                  labels=l + ['k=0 (same signature)'], ncol=2, loc='upper right')
        ax.set_ylim(top=ax.get_ylim()[1] * 8)                     # headroom for the legend
    fig.tight_layout()
    os.makedirs(out, exist_ok=True)
    for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(out, 'fig_sc_cost.' + ext), dpi=200)
    print('saved', os.path.join(out, 'fig_sc_cost.pdf'))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--run', action='store_true', help='compute the missing points before plotting')
    ap.add_argument('--force', action='store_true', help='recompute the selected points even if their file exists')
    ap.add_argument('--data', default='results', help='directory of the point files (default: results)')
    ap.add_argument('--out', default='.', help='directory for fig_sc_cost.pdf/.png (default: .)')
    ap.add_argument('--samples', type=int, default=10, help='random walks per dimension (default 10)')
    ap.add_argument('--reps', type=int, default=10, help='random sets K per visited function and k (default 10)')
    ap.add_argument('--batch', type=int, default=10, help='consecutive calls per timed measurement (default 10)')
    ap.add_argument('--nmax', type=int, default=8, help='largest dimension; dimensions are 2..nmax (default 8)')
    ap.add_argument('--n', type=int, nargs='+', help='only these dimensions (with --run)')
    ap.add_argument('--k', type=int, nargs='+', help='only these numbers of sign changes, 0 = baseline (with --run)')
    ap.add_argument('--workers', type=int, default=2, help='processes (default 2)')
    a = ap.parse_args()
    ns = a.n or list(range(2, a.nmax + 1))
    if a.run:
        run(a.data, ns, set(a.k) if a.k else None, a.samples, a.reps, a.batch, a.workers, a.force)
    plot(load(a.data, a.samples, a.reps, a.batch, list(range(2, a.nmax + 1))), a.out)
