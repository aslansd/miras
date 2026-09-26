# Roadmap

## Done in 0.1.1

From the first full-scale run on a user's machine (see `TESTING.md`):
convergence of every Stan fit is checked and failures are reported with the
chains responsible; `--identify` leaves unconverged fits out; `--init-radius`
and `--refit`; matplotlib imported lazily; an actionable message when CmdStan
is missing; the ABM sweep and ABC checkpoint and resume exactly; progress lines
estimate the time left; Ctrl-C exits with one line instead of a traceback per
worker; ABC contrasts centred on the posterior. Details in `CHANGELOG.md`.

## Next (0.1.2)

1. **Evidence on stuck chains.** Refit the full-scale longitudinal data with
   several seeds, with and without `--init-radius 0.5`, and record how often a
   chain gets stuck. Change the default initialisation only if the evidence
   supports it. Also check whether the original R/rstan fit shows the same
   behaviour, to tell a property of the model from a property of the port.
2. **Resumable `--identify`.** Each dataset takes about two hours; save each
   finished fit so an interrupted run skips completed datasets, and run
   datasets in parallel when there are cores to spare (each fit already uses
   four).
3. **Checkpoint the remaining long steps**: ABC posterior predictions and the
   longitudinal posterior simulations (minutes rather than hours, so lower
   priority).

## Later

Ordered by what most improves the one question miras exists to answer:
*can this study design recover these parameters?*

1. **More findings.** `UNDERPOWERED` (how many groups / respondents / waves
   until a parameter is recoverable: the paper's power analysis, generalised
   by sweeping the design) and `MISCALIBRATED` (simulation-based calibration,
   Talts et al. 2018, rather than the single 90% coverage number reported now).
2. **Equifinality beyond pairs.** The current detector examines parameter
   pairs. Ridges involving three or more parameters (e.g. conformity, migration
   and innovation jointly) need the full posterior covariance spectrum.
3. **Summary informativeness.** A `WEAK_SUMMARY` finding saying which
   summaries carry information about which parameters, so designs can be
   pruned as well as extended.
4. **Simulation-based inference backend** (neural posterior estimation via
   `sbi`), for designs where ABC's curse of dimensionality bites.
5. **Longitudinal designs as first-class objects**, not only through the paper
   workflow: panel studies with observed networks, as in Fig. 4.
6. **More learning rules and structures.** Prestige / success bias, guided
   variation and content bias; network population structure.
7. **Speed.** A JAX backend (`vmap` over parameter sets) so reference tables
   of 10^5 simulations become interactive.
8. **Real data adapters**, and a validation study: does a design that miras
   calls identifiable actually recover parameters from real data?
9. Populations of LLM agents as learners, audited with daftar's Concordia
   adapter.
