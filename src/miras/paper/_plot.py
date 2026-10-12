"""Plotting helpers for the paper figures: R-style density(), HPDI, colour
palettes (RColorBrewer Set1, colorRampPalette, scales::alpha)."""
from __future__ import annotations

import numpy as np

# matplotlib is imported inside the functions that need it, so the paper
# modules (e.g. building Stan data) work with the core install alone.

# RColorBrewer::brewer.pal(9, "Set1")
SET1 = ["#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00",
        "#FFFF33", "#A65628", "#F781BF", "#999999"]

def inv_logit(x):
    return 1.0 / (1.0 + np.exp(-np.asarray(x, float)))


def color_ramp(colors, n):
    """R colorRampPalette(colors)(n): linear RGB interpolation."""
    from matplotlib.colors import to_rgba
    rgb = np.array([to_rgba(c)[:3] for c in colors])
    xs = np.linspace(0, 1, len(colors))
    t = np.linspace(0, 1, n)
    return [tuple(np.interp(ti, xs, rgb[:, k]) for k in range(3)) for ti in t]


def alpha(color, a):
    """scales::alpha"""
    from matplotlib.colors import to_rgba
    r, g, b, _ = to_rgba(color)
    return (r, g, b, a)


def bw_nrd0(x):
    """R's default bandwidth (Silverman's rule of thumb, bw.nrd0)."""
    x = np.asarray(x, float)
    hi = np.std(x, ddof=1)
    iqr = np.subtract(*np.percentile(x, [75, 25]))
    lo = min(hi, iqr / 1.34)
    if not lo:
        lo = hi or abs(x[0]) or 1.0
    return 0.9 * lo * x.size ** -0.2


def r_density(x, n=512, cut=3.0):
    """Gaussian KDE mimicking R's density(x): bw.nrd0, grid of n points from
    min(x)-cut*bw to max(x)+cut*bw. Returns (grid, density)."""
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    bw = bw_nrd0(x)
    grid = np.linspace(x.min() - cut * bw, x.max() + cut * bw, n)
    y = np.zeros(n)
    for chunk in np.array_split(x, max(1, x.size // 5000)):
        y += np.exp(-0.5 * ((grid[:, None] - chunk[None, :]) / bw) ** 2).sum(axis=1)
    y /= x.size * bw * np.sqrt(2 * np.pi)
    return grid, y


def hpdi(samples, prob=0.89):
    """rethinking::HPDI (coda::HPDinterval algorithm)."""
    v = np.sort(np.asarray(samples, float))
    n = v.size
    gap = max(1, min(n - 1, int(round(n * prob))))
    init = np.arange(n - gap)
    i = int(np.argmin(v[init + gap] - v[init]))
    return v[i], v[i + gap]


def shade_density(ax, samples, color, inner=(0.05, 0.95)):
    """The recurring R idiom: 90% interval of the density filled at alpha 0.9,
    the full range at alpha 0.2."""
    samples = np.asarray(samples, float)
    samples = samples[np.isfinite(samples)]
    x, y = r_density(samples)
    for (lo_q, hi_q), a in ((inner, 0.9), ((0.0, 1.0), 0.2)):
        lo, hi = np.quantile(samples, [lo_q, hi_q])
        sel = np.flatnonzero((x >= lo) & (x < hi))
        if sel.size == 0:
            continue
        xs = np.concatenate(([x[sel[0]]], x[sel], [x[sel[-1]]]))
        ys = np.concatenate(([0.0], y[sel], [0.0]))
        ax.fill(xs, ys, color=alpha(color, a), lw=0)
    return x, y


def clean_density_axis(ax):
    """bty='n', yaxt='n'"""
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_yticks([])


def spawn_seeds(seed, n):
    """Independent integer seeds for parallel jobs."""
    return [int(x) for x in np.random.SeedSequence(seed).generate_state(n, dtype=np.uint64) % (2**63)]
