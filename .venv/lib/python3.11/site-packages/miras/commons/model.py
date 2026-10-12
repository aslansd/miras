"""A common-pool resource shared by culturally different groups, and the
spread of an innovation that lowers each adopter's consumption at a cost.

Implements the miras.commons model specification (September 2026). Section
names in comments refer to that document. Groups differ in tightness,
in-group altruism, out-group parochialism, wealth, political power and
contact; the innovation is seeded in one group, either as originating there
or as introduced from outside.

Each step: 1 recharge, 2 harvest (rationed under shortage), 3 payoffs,
4 social learning, 5 simultaneous adoption update.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace

import numpy as np

from ..engine.groups import GroupedPopulation, water_fill

NONE, OUTSIDE = -1, -2          # innovation owner codes (otherwise a group index)


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Group:
    """A group and its experimental attributes (all in [0, 1] except size,
    wealth and power, which are relative: 1 = average)."""

    name: str = "group"
    size: int = 200
    tightness: float = 0.5        # tau: conformity, sanctions, caution
    altruism: float = 0.5         # alpha_in: values own group's share of saved water
    parochialism: float = 0.5     # alpha_out: filters out-group models, resists others' traits
    wealth: float = 1.0           # w: lowers the effective cost of a product
    power: float = 1.0            # p: prestige, and share of water in a shortage
    contact: float = 0.1          # c: how often members learn from other groups


@dataclass(frozen=True)
class Innovation:
    saving: float = 0.4           # delta: fraction of demand an adopter saves
    cost: float = 0.1             # kappa: cost per step, in units of service value
    wealth_scaling: float = 1.0   # epsilon: 1 = a product (cost / wealth), 0 = a convention
    efficiency: bool = True       # D1: same service from less water (False: sufficiency)


@dataclass(frozen=True)
class Resource:
    rho: float = 0.85             # recharge / demand with no adopters
    storage: float = 20.0         # K / I: steps of recharge the store holds
    demand: float = 1.0           # d0: water per person per step without the innovation
    collapse_threshold: float = 0.1


@dataclass(frozen=True)
class Learning:
    p_learn: float = 0.1          # fraction of each group learning per step
    n_conform: int = 10           # sample size in conformist events
    theta: float = 1.5            # conformity exponent (amendment A3; spec draft: 3)
    beta_s: float = 10.0          # slope of payoff-based switching (A3; draft: 1)
    mu: float = 0.01              # experimentation rate
    eta: float = 0.8              # how much tightness suppresses experimentation
    beta_prestige: float = 1.0    # beta: weight of power in prestige
    gamma_share: float = 1.0      # gamma: weight of power in the shortage share
    sigma_max: float = 0.3        # largest sanction for deviating
    lambda0: float = 4.0          # value of saved water at an empty store (A3; draft: 1)
    service_value: float = 1.0    # b
    zeta: float = 0.5             # resistance to a trait owned by another group
    zeta_ext: float = 0.5         # resistance to a trait owned by outsiders


@dataclass(frozen=True)
class Mechanisms:
    """Switches for every mechanism in 'Group attributes as mechanisms'."""

    tight_conformity: bool = True
    tight_sanctions: bool = True
    tight_caution: bool = True
    ingroup_value: bool = True
    outgroup_filter: bool = True
    ownership_bias: bool = True
    ownership_rejection: bool = False   # D4(c) variant
    wealth_cost: bool = True
    power_prestige: bool = True
    power_share: bool = True

    def without(self, *names) -> "Mechanisms":
        unknown = set(names) - set(asdict(self))
        if unknown:
            raise KeyError(f"unknown mechanisms {sorted(unknown)}; known: {sorted(asdict(self))}")
        return replace(self, **{n: False for n in names})


@dataclass(frozen=True)
class Seeding:
    """How the innovation enters (section 'Origination versus introduction').

    mode: 'originate' (owned by the seed group), 'introduce' (owned by
    'outside', optionally with subsidy and demonstrators), 'none' (reference:
    no innovation), or 'all' (reference: every group seeded equally, no owner).
    timing: 'plenty' seeds with a full store; 'scarcity' seeds when shortage
    begins (spec amendment A2: the pilot showed timing can decide the outcome).
    """

    mode: str = "originate"
    group: int = 0
    timing: str = "scarcity"      # 'plenty': full store; 'scarcity': shortage from step 0 (A2)
    fraction: float = 0.05
    support: bool = True          # introduction brings the subsidy and demonstrators
    subsidy: float = 0.5          # phi
    subsidy_steps: int = 100      # T_sub
    demo_prestige: float = 2.0    # p_ext
    demo_steps: int = 100         # T_demo

    def __post_init__(self):
        if self.mode not in ("originate", "introduce", "none", "all"):
            raise ValueError("mode must be originate, introduce, none or all")
        if self.timing not in ("plenty", "scarcity"):
            raise ValueError("timing must be plenty or scarcity")


# --------------------------------------------------------------------------- #
# Results
# --------------------------------------------------------------------------- #
@dataclass
class CommonsResult:
    adoption: np.ndarray          # (T, G) adopting share per group after each step
    stock: np.ndarray             # (T,) stock after harvest, as a fraction of capacity
    shortage: np.ndarray          # (T,) 1 - harvest / demand
    payoff: np.ndarray            # (T, G) mean material payoff per group
    sizes: np.ndarray
    a_star: float                 # adoption share at which demand equals recharge
    seeding: Seeding
    threshold: float = 0.1
    names: list = field(default_factory=list)

    @property
    def overall(self) -> np.ndarray:
        return self.adoption @ self.sizes / self.sizes.sum()

    def outcomes(self, window: int = 100) -> dict:
        """The outcomes of 'Outcomes and experimental design'."""
        T = len(self.stock)
        w = slice(max(0, T - window), T)
        overall = self.overall
        mean_last = float(overall[w].mean())
        collapsed = bool(self.shortage[w].mean() > self.threshold)
        hit = np.flatnonzero(overall >= self.a_star)
        g_pay = self.payoff[w].mean(axis=0)
        seed = self.seeding.group
        others = np.delete(np.arange(len(self.sizes)), seed) if len(self.sizes) > 1 else []
        return {
            "final_adoption": float(overall[-1]),
            "mean_adoption_last": mean_last,
            "sustained": bool(mean_last >= self.a_star and not collapsed),
            "collapsed": collapsed,
            "mean_shortage_last": float(self.shortage[w].mean()),
            "reach": int((self.adoption[-1] > 0.5).sum()),
            "time_to_a_star": int(hit[0]) if hit.size else -1,
            "gini_payoff": gini(g_pay),
            "seed_group_adoption": float(self.adoption[-1, seed]),
            "other_groups_adoption": (float(self.adoption[-1, others] @ self.sizes[others]
                                            / self.sizes[others].sum()) if len(others) else np.nan),
            # continuous view of sustainability (0.2.1): how far adoption ends
            # above (+) or below (-) the share the commons needs
            "a_star": float(self.a_star),
            "adoption_gap": float(mean_last - self.a_star),
        }


def gini(x) -> float:
    x = np.sort(np.asarray(x, float))
    if x.size == 0 or np.allclose(x, 0):
        return 0.0
    x = x - min(0.0, x.min())            # payoffs can be negative: shift to >= 0
    n = x.size
    return float((2 * np.arange(1, n + 1) - n - 1) @ x / (n * x.sum())) if x.sum() > 0 else 0.0


# --------------------------------------------------------------------------- #
# The model
# --------------------------------------------------------------------------- #
class CommonsModel:
    def __init__(self, groups, innovation=None, resource=None, learning=None, mechanisms=None):
        self.groups = list(groups)
        if not self.groups:
            raise ValueError("need at least one group")
        self.inn = innovation or Innovation()
        self.res = resource or Resource()
        self.lrn = learning or Learning()
        self.mech = mechanisms or Mechanisms()
        g = self.groups
        self.sizes = np.array([x.size for x in g])
        self.tau = np.array([x.tightness for x in g], float)
        self.alpha_in = np.array([x.altruism for x in g], float)
        self.alpha_out = np.array([x.parochialism for x in g], float)
        self.wealth = np.array([x.wealth for x in g], float)
        self.power = np.array([x.power for x in g], float)
        self.contact = np.array([x.contact for x in g], float)
        lo = 1 - self.inn.saving
        if not (0 < self.res.rho) or self.inn.saving <= 0:
            raise ValueError("need rho > 0 and a positive saving")
        self.a_star = (1 - self.res.rho) / self.inn.saving
        self._lo = lo

    # entitlement weights for sharing a shortage, and in-group value shares
    def entitlements(self):
        if self.mech.power_share:
            return self.sizes * self.power ** self.lrn.gamma_share
        return self.sizes.astype(float)

    def run(self, steps=500, seeding=None, seed=None, rng=None) -> CommonsResult:
        rng = rng if rng is not None else np.random.default_rng(seed)
        sd = seeding or Seeding()
        pop = GroupedPopulation(self.sizes, rng)
        N, G, grp = pop.N, pop.n_groups, pop.group
        inn, res, L, M = self.inn, self.res, self.lrn, self.mech
        d0, delta = res.demand, inn.saving
        I = res.rho * N * d0
        K = res.storage * I
        ent = self.entitlements()
        omega = ent / ent.sum()
        eps = inn.wealth_scaling if M.wealth_cost else 0.0
        base_cost = inn.cost / self.wealth ** eps                         # per group
        mu_g = L.mu * (1 - L.eta * self.tau) if M.tight_caution else np.full(G, L.mu)
        p_conf = self.tau if M.tight_conformity else np.zeros(G)
        prestige = self.power ** L.beta_prestige if M.power_prestige else np.ones(G)

        # seeding ('Origination versus introduction')
        a = np.zeros(N, dtype=np.int8)
        owner = NONE
        if sd.mode in ("originate", "introduce"):
            if not 0 <= sd.group < G:
                raise ValueError("seed group out of range")
            mem = pop.members(sd.group)
            k = max(1, int(round(sd.fraction * mem.size)))
            a[rng.choice(mem, k, replace=False)] = 1
            owner = sd.group if sd.mode == "originate" else OUTSIDE
        elif sd.mode == "all":
            for g in range(G):
                mem = pop.members(g)
                a[rng.choice(mem, max(1, int(round(sd.fraction * mem.size))), replace=False)] = 1
        support = sd.mode == "introduce" and sd.support

        # resistance to adopting an owned trait, by the adopter's group
        if owner == NONE or not M.ownership_bias:
            own_factor = np.ones(G)
        elif owner == OUTSIDE:
            own_factor = 1 - L.zeta_ext * self.alpha_out
        else:
            own_factor = 1 - L.zeta * self.alpha_out
            own_factor[owner] = 1.0
        # D4(c): a per-step utility cost of carrying another group's trait
        if M.ownership_rejection and owner != NONE:
            z = L.zeta_ext if owner == OUTSIDE else L.zeta
            reject_cost = z * self.alpha_out
            if owner >= 0:
                reject_cost[owner] = 0.0
        else:
            reject_cost = np.zeros(G)

        T = int(steps)
        rec_adopt = np.zeros((T, G))
        rec_stock = np.zeros(T)
        rec_short = np.zeros(T)
        rec_pay = np.zeros((T, G))
        # A2: 'plenty' starts with a full store; 'scarcity' with an empty one,
        # which is the state an innovation-free commons reaches when shortage
        # begins (the steps before it change nothing without adopters)
        R = K if sd.timing == "plenty" else 0.0
        for t in range(T):
            # 1 recharge; 2 harvest ('The common-pool resource')
            R = min(K, R + I)
            d = d0 * (1 - delta * a)
            D = d.sum()
            H = min(D, R)
            R -= H
            if H >= D * (1 - 1e-12):
                h = d
                short = 0.0
            else:
                Dg = np.bincount(grp, weights=d, minlength=G)
                Xg = water_fill(H, Dg, ent)
                h = np.empty(N)
                for g in range(G):
                    m = pop.members(g)
                    h[m] = water_fill(Xg[g], d[m])                          # equal quota (D2a)
                short = 1 - H / D
            # 3 payoffs ('Payoffs')
            service = np.minimum(1.0, h / d) if inn.efficiency else h / d0
            subsidised = support and t < sd.subsidy_steps
            cost = base_cost * (1 - sd.subsidy) if subsidised else base_cost
            f = pop.group_mean(a)
            maj = np.where(f > 0.5, 1, np.where(f < 0.5, 0, -1))           # -1: no majority
            strength = 2 * np.maximum(f, 1 - f) - 1
            sanc_g = self.tau * L.sigma_max * strength if M.tight_sanctions else np.zeros(G)
            deviant = (maj[grp] >= 0) & (a != maj[grp])
            lam = L.lambda0 * (1 - R / K)
            value_g = (self.alpha_in * omega * lam * delta * d0) if M.ingroup_value else np.zeros(G)
            pi = L.service_value * service - cost[grp] * a - sanc_g[grp] * deviant
            u = pi + value_g[grp] * a - reject_cost[grp] * a

            # 4 social learning ('Social learning')
            learners = np.flatnonzero(rng.random(N) < L.p_learn)
            new = a.copy()
            if learners.size:
                gl = grp[learners]
                exp = rng.random(learners.size) < mu_g[gl]
                # experimentation: anyone can drop the innovation, but only people
                # whose group already has adopters can try it (spec amendment A1:
                # nobody can try a device or convention they have never encountered)
                aware = f[gl] > 0
                flip = exp & ((a[learners] == 1) | aware)
                new[learners[flip]] = 1 - a[learners[flip]]
                rest = learners[~exp]
                conf = rng.random(rest.size) < p_conf[grp[rest]]
                # conformist events: follow the sampled majority, exponent theta
                cl = rest[conf]
                if cl.size:
                    fm = a[pop.sample_in_group(cl, L.n_conform)].mean(axis=1)
                    num = fm ** L.theta
                    p1 = num / (num + (1 - fm) ** L.theta)
                    target = (rng.random(cl.size) < p1).astype(np.int8)
                    adopt = (target == 1) & (a[cl] == 0)
                    ok = rng.random(cl.size) < own_factor[grp[cl]]
                    target = np.where(adopt & ~ok, a[cl], target)
                    new[cl] = target
                # payoff-based events: one model, proportional imitation
                pl = rest[~conf]
                if pl.size:
                    self._payoff_learning(pl, a, u, new, pop, prestige, own_factor, support,
                                          t, sd, rng, h, cost, sanc_g, maj, value_g,
                                          reject_cost, d0, delta, L)
            a = new
            # 5 record
            rec_adopt[t] = pop.group_mean(a)
            rec_stock[t] = R / K
            rec_short[t] = short
            rec_pay[t] = pop.group_mean(pi)
        return CommonsResult(rec_adopt, rec_stock, rec_short, rec_pay, self.sizes.copy(),
                             self.a_star, sd, res.collapse_threshold,
                             [g.name for g in self.groups])

    def _payoff_learning(self, pl, a, u, new, pop, prestige, own_factor, support, t, sd, rng,
                         h, cost, sanc_g, maj, value_g, reject_cost, d0, delta, L):
        M, grp = self.mech, pop.group
        src, looked, _ = pop.choose_model_groups(pl, self.contact, prestige, filter_out=None)
        # outside demonstrators: an extra source for learners in the seed group
        demo = np.zeros(pl.size, bool)
        if support and t < sd.demo_steps:
            in_seed = grp[pl] == sd.group
            others = np.delete(np.arange(pop.n_groups), sd.group)
            w_groups = float((pop.sizes[others] * prestige[others]).sum())
            w_demo = (sd.demo_prestige ** L.beta_prestige) * pop.sizes.mean()
            p_demo = w_demo / (w_demo + w_groups)
            demo = looked & in_seed & (rng.random(pl.size) < p_demo)
        # parochial filter on everything from outside the group
        if M.outgroup_filter:
            rejected = looked & (rng.random(pl.size) < self.alpha_out[grp[pl]])
            src = np.where(rejected, grp[pl], src)
            demo &= ~rejected
        models = pop.random_members(src)
        a_m = a[models].copy()
        u_m = u[models].copy()
        if demo.any():
            # a demonstrator shows the innovation working in the learner's own
            # situation: the learner's utility if it adopted
            i = pl[demo]
            g = grp[i]
            if self.inn.efficiency:
                s_ad = np.minimum(1.0, h[i] / (d0 * (1 - delta)))
            else:
                s_ad = np.minimum(h[i], d0 * (1 - delta)) / d0
            sanction = sanc_g[g] * (maj[g] == 0)
            a_m[demo] = 1
            u_m[demo] = (L.service_value * s_ad - cost[g] - sanction + value_g[g] - reject_cost[g])
        differ = a_m != a[pl]
        p = np.clip(L.beta_s * (u_m - u[pl]), 0.0, 1.0)
        p = np.where((a_m == 1) & differ, p * own_factor[grp[pl]], p)
        switch = differ & (rng.random(pl.size) < p)
        new[pl[switch]] = a_m[switch]
