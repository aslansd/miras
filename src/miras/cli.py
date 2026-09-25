"""miras command line.

    miras demo                       # can F_ST alone tell conformity from migration?
    miras paper {dags,abm,longitudinal,abc} [options]
    miras doctor                     # which optional components work here
"""
from __future__ import annotations

import argparse
import importlib
import os
import sys


def _demo(argv):
    p = argparse.ArgumentParser(prog="miras demo", description=(
        "A small, fast identifiability check: in a 10-village population, can a "
        "cross-sectional study recover the conformity exponent and the migration "
        "rate from cultural F_ST alone, and from F_ST plus within-group diversity?"))
    p.add_argument("--n-reference", type=int, default=600)
    p.add_argument("--n-test", type=int, default=40)
    p.add_argument("--cores", type=int, default=os.cpu_count())
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--track", action="store_true", help="record with daftar")
    args = p.parse_args(argv)

    from . import (Conformity, CrossSectional, Islands, Model, ModelSimulator, ReferenceTable,
                   Uniform, WrightFisher, identify)
    model = Model(structure=Islands(n_groups=10, group_size=40), demography=WrightFisher(),
                  learning=Conformity(), innovation=0.05, n_models=15)
    sim = ModelSimulator(model, summaries=("fst", "within_diversity"),
                         design=CrossSectional(n_per_group=25), n_steps=100)
    priors = {"learning.theta": Uniform(0.5, 3.0), "migration": Uniform(0.0, 0.4)}
    print(f"Simulating {args.n_reference} studies from the prior ...", flush=True)
    table = ReferenceTable.build(sim, priors, args.n_reference, seed=args.seed, cores=args.cores)
    for label, summaries in (("F_ST only", ["fst"]),
                             ("F_ST + within-group diversity", ["fst", "within_diversity"])):
        report = identify(sim, priors, table=table.select(summaries), n_test=args.n_test,
                          track=args.track, label=f"demo-{len(summaries)}")
        print(f"\n=== {label} ===\n{report.summary()}")


def _doctor(argv):
    from . import __version__
    from .inference.stan import cmdstan_available
    from .provenance import daftar_available
    print(f"miras {__version__}  (python {sys.version.split()[0]})")
    rows = []
    for mod, extra, purpose in (("numpy", None, "core"),
                                ("matplotlib", "plot", "figures and report plots"),
                                ("pandas", "paper", "paper ABC workflow"),
                                ("cmdstanpy", "stan", "Stan backend")):
        try:
            m = importlib.import_module(mod)
            rows.append((mod, getattr(m, "__version__", "?"), purpose, True))
        except ImportError:
            rows.append((mod, f"missing (pip install 'miras[{extra}]')", purpose, False))
    ok, msg = cmdstan_available()
    rows.append(("CmdStan", "installed" if ok else msg, "Stan backend", ok))
    rows.append(("daftar", "installed" if daftar_available() else "missing (pip install 'miras[provenance]')",
                 "provenance (track=True)", daftar_available()))
    for name, status, purpose, good in rows:
        print(f"  {'ok ' if good else '-- '} {name:<11} {status:<45} {purpose}")
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] in ("-V", "--version"):
        from . import __version__
        print(__version__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "demo":
        return _demo(rest)
    if cmd == "doctor":
        return _doctor(rest)
    if cmd == "paper":
        from .paper import WORKFLOWS
        if not rest or rest[0] not in WORKFLOWS:
            print(f"usage: miras paper {{{','.join(WORKFLOWS)}}} [options]  (add --help for options)")
            return 2
        module = importlib.import_module(WORKFLOWS[rest[0]])
        return module.main(rest[1:])
    print(f"unknown command '{cmd}'\n{__doc__}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
