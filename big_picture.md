# Big Picture of Monte Carlo

| **Concept** | **Representative Quantities / Methods** | **Purpose / Idea** |
|:-------------|:---------------------------------------|:-------------------|
| **Population/Truth** | random variable $Y$, mean $\mu$, variance $\sigma^2$, probability density/mass function $\varrho$, cumulative distribution function *F*, quantile function *Q* | Describe the true (often unknown) distribution or system behavior |
| **Sampling** | IID, low-discrepancy (QMC), Markov Chain Monte Carlo (MCMC), acceptance–rejection | Generate representative points from the population |
| **Estimation** | Sample mean, variance, histogram, ECDF, quantile estimates | Approximate population quantities using finite samples |
| **Uncertainty** | Central Limit Theorem (CL T), bootstrap, Bayesian credible intervals | Quantify the reliability of Monte Carlo estimates |
| **Efficiency** | Importance sampling, control variates, stratified sampling, multilevel MC (MLMC) | Reduce variance or computational cost for a fixed accuracy |
| **Applications** | Quantitative finance, Bayesian inference, queueing systems, reliability analysis | Apply Monte Carlo methodology to practical problems |
