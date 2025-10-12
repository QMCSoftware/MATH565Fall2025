---
title: Big Picture
layout: default
permalink: /big_picture/
---

# Big Picture of Monte Carlo

| **Concept** | **Representative Quantities / Methods** | **Purpose / Idea** |
|:-------------|:---------------------------------------|:-------------------|
 **Population/Truth** | random variable $Y=f(\boldsymbol{X})$, mean $\mu$, variance $\sigma^2$, probability density/mass function $\varrho$, cumulative distribution function *F*, quantile function *Q* | The system whose behavior one wants to understand, which is governed by randomness or uncertainty 
| **Sampling** | IID, low-discrepancy (QMC), Markov Chain Monte Carlo (MCMC), acceptance–rejection | Generate representative points from the population |
| **Estimation** | Sample mean, variance, histogram, ECDF, quantile estimates | Approximate population quantities using finite samples |
| **Uncertainty** | Central Limit Theorem (CL T), bootstrap, Bayesian credible intervals | Quantify the reliability of Monte Carlo estimates |
| **Efficiency** | Importance sampling, control variates, stratified sampling, multilevel MC (MLMC) | Reduce variance or computational cost for a fixed accuracy |
| **Applications** | Quantitative finance, Bayesian inference, queueing systems, reliability analysis | Apply Monte Carlo methodology to practical problems |
