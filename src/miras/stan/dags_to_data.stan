// Linear regression used to estimate the causal effect of migration (M) on
// cultural diversity (D), adjusting for conformity (C).
// Equivalent to the rethinking::ulam model in DAGstoData.R:
//   D ~ dnorm(mu, sigma); mu <- a + bmd*M + bcd*C;
//   c(a, bmd, bcd) ~ dnorm(0, 1); sigma ~ dexp(1)
data {
  int<lower=1> N;
  vector[N] D;
  vector[N] M;
  vector[N] C;
}
parameters {
  real a;
  real bmd;
  real bcd;
  real<lower=0> sigma;
}
model {
  a ~ normal(0, 1);
  bmd ~ normal(0, 1);
  bcd ~ normal(0, 1);
  sigma ~ exponential(1);
  D ~ normal(a + bmd * M + bcd * C, sigma);
}
