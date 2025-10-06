---
layout: default
title: Assignment 3
permalink: /assgn3/
---

# Assigment 3

Due: Friday, October 17, 2025


1. Consider a Starbucks with one line.  
    * The time until the customer arrives is an exponential random variable with a mean of $t_a$ minutes. When a customer arrives, they join the queue unless the queue is empty, in which case they go to the cashier.
    * The time for the customer to receive an order once they reach the cashier has a (isosceles) triangular density with minimum $t_{\min}$ minutes and maximum $t_{\max}$ minutes.
    * The arrival times and service times for all customers are independent.

    In a Jupyter notebook or equivalent, create a Monte Carlo simulation for this situation, which runs for $N$ customers.

    1. Setting $t_{a}=5$,$t_{\min}=1$, $t_{\max}=5$, and $N=200$, find the probability that the queue reaches $10$ customers or more.
  
    1. How small must $t_{\max}$ be to make the probability of a $10$-or-more-person queue less than $10\%$?  If this is impossible, adjust $t_a$.
  

1. Consider two IID sets of points, ${\lbrace \boldsymbol{X}\_i \rbrace}\_{i=0}^{m-1}$ and ${\lbrace \boldsymbol{Z}\_i \rbrace}\_{i=0}^{n-1}$, andd assume that $m < n$.

    1. Compute the expected squared discrepancy between these two sets of points for a general kernel, $K$, assuming that
        
        1. The two sets are independent.

        1. $\boldsymbol{X}_i = \boldsymbol{Z_i}$ for $i=0, \ldots, m-1$ and $m < n$.

    1. What is the rate at which the expected squared discrepancy tends to zero if $m$ and $n$ both tend to infinity with $r = m/n < 1$ fixed?

