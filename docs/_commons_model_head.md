# miras.commons: model reference

A compact reference to the model in `miras.commons`. The full design
document, with the reasoning behind every choice, is the *miras.commons
model specification* (September 2026, with amendments A1 to A4); this file
records what the code implements.

Several groups share one resource (for example water). An innovation lets an
adopter use a fraction δ less of it, at a cost κ. Groups differ in tightness,
in-group altruism, out-group parochialism, wealth, political power and
contact. The innovation is seeded in one group, either originating there
(owned by that group) or introduced from outside (owned by "outside", with an
optional subsidy and outside demonstrators), during plenty or at the onset of
scarcity.

## One step

1. **Recharge**: R ← min(K, R + I), with I = ρ N d₀ and K = storage × I.
2. **Harvest**: demand dᵢ = d₀(1 − δ aᵢ); H = min(D, R). In a shortage, groups
   get water in proportion to N_g p_g^γ, capped at their demand, excess passed
   on (water-filling); within a group everyone gets an equal quota, capped at
   their demand.
3. **Payoffs**: service sᵢ = min(1, hᵢ/dᵢ) (efficiency) or hᵢ/d₀ (sufficiency);
   πᵢ = b sᵢ − κᵢ aᵢ − σᵢ, with κᵢ = κ(1 − φ[subsidy on]) / w_g^ε and a
   sanction σᵢ = τ_g σ_max (2 f_maj − 1) for deviating from the group majority.
   Learners act on uᵢ = πᵢ + α_in,g ω_g λ(R) δ d₀ aᵢ, where ω_g is the group's
   entitlement share and λ(R) = λ₀(1 − R/K).
4. **Learning** (a fraction p_learn of each group):
   - experiment with probability μ(1 − η τ_g): drop the innovation, or try it
     if it is present in the learner's group (amendment A1);
   - otherwise, with probability τ_g, a conformist event: sample n group
     members, adopt with probability f^θ / (f^θ + (1 − f)^θ);
   - otherwise one model: from another group with probability c_g (chosen in
     proportion to N_h p_h^β; outside demonstrators are an extra source for the
     seed group while support lasts), kept with probability 1 − α_out,g, else an
     in-group model; switch with probability clip(β_s (u_model − uᵢ), 0, 1);
   - adopting a trait owned by another group is multiplied by 1 − ζ α_out,g
     (1 − ζ_ext α_out,g for an outside-owned trait, in every group).
5. **Update** everyone at once and record adoption per group, stock, shortage
   and mean payoffs.

Sustainability threshold: demand ≤ recharge exactly when the adoption share
reaches A* = (1 − ρ)/δ.

## Amendments after the pilot (27 September 2026)

| # | Change |
| --- | --- |
| A1 | Experimentation can drop the innovation anywhere but try it only where it is already present (the no-innovation reference now has no adopters). |
| A2 | Seeding timing is an experimental factor: during plenty (full store) or at the onset of scarcity (empty store). |
| A3 | Recalibrated defaults so a mid-level population sits near its tipping point: β_s 1 → 10, θ 3 → 1.5, λ₀ 1 → 4. Results are conditional on this calibration. |
| A4 | Verification V1 made exact: first shortage at step ⌊(K − D)/(D − I)⌋ + 1. |

## Mechanism switches

Every mechanism can be switched off (`Mechanisms().without(...)`, or
`--off` on the command line): `tight_conformity`, `tight_sanctions`,
`tight_caution`, `ingroup_value`, `outgroup_filter`, `ownership_bias`,
`ownership_rejection` (off by default: D4c), `wealth_cost`,
`power_prestige`, `power_share`.

