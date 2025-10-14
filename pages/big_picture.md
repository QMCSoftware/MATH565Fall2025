---
title: Big Picture
layout: default
permalink: /big_picture/
---

# Monte Carlo Big Ideas 

| **Concept** | **Representative Quantities / Methods** | **Purpose / Idea** |
|:-------------|:---------------------------------------|:-------------------|
 **Population/Truth** | random variable $Y=f(\boldsymbol{X})$, mean $\mu$, variance $\sigma^2$, probability density/mass function $\varrho$, cumulative distribution function *F*, quantile function *Q* |  System governed by randomness or uncertainty, whose behavior one wants to understand
 **Applications** | quantitative finance, Bayesian inference, queueing systems, uncertainty quantification (UQ), image rendering, stochastic gradient descent | Apply Monte Carlo methodology to practical problems
**Sampling** | independent and identically distibuted (IID), low discrepancy (LD), quartile transformation, affine transformation, multivariate Gaussian, Markov Chain Monte Carlo (MCMC), acceptance–rejection | Generate representative points from the population 
**Estimation** | sample mean, sample variance, histogram, kernel density estimation, empirical distribution function, empirical quantile function | Approximate population quantities using sample quantities
| **Efficiency** | importance sampling, control variates, stratified sampling, multilevel (quasi-)Monte Carlo (ML(Q)MC) | Reduce variance/variation or computational cost for a fixed accuracy
| **Estimate Uncertainty** | Central Limit Theorem (CLT), bootstrap, Bayesian credible intervals, tracking Fourier coefficients | Quantify the reliability of Monte Carlo estimates |

