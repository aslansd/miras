"""Toy simulators with known identifiability, used as ground truth.
Top-level functions so they can be pickled for cores > 1."""


def identified(p, r):  return [p["a"] + r.normal(0, .03), p["b"] + r.normal(0, .03)]
def product(p, r):     return [p["a"] * p["b"] + r.normal(0, .01)]
def total(p, r):       return [p["a"] + p["b"] + r.normal(0, .02)]
def ratio(p, r):       return [p["a"] / p["b"] + r.normal(0, .02), r.normal()]
def irrelevant_c(p, r): return [p["a"] + r.normal(0, .03), p["b"] + r.normal(0, .03)]
def weak_b(p, r):      return [p["a"] + r.normal(0, .03), p["b"] + r.normal(0, .2)]
def correlated(p, r):  return [p["a"] + p["b"] + r.normal(0, .02), p["a"] - .5 * p["b"] + r.normal(0, .02)]
def product_plus_c(p, r): return [p["a"] * p["b"] + r.normal(0, .01), p["c"] + r.normal(0, .03)]
def normal_mean(p, r): return [r.normal(p["mu"], 1, 25).mean(), r.normal()]
def b_only_when_a_low(p, r):
    return [p["a"] + r.normal(0, .03), (p["b"] if p["a"] < 0.5 else 0.0) + r.normal(0, .03)]
