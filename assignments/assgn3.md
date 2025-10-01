---
layout: default
title: Assignment 3
permalink: /assgn3/
---

# Assigment 3

Due: Friday, October 17, 2025


1.  Consider a Starbucks with one line.  
    * The time until the custormer arrives is an exponential random variable with a mean of $t_a$ minutes.  When a customer arrives, he or she joins the queue unless the queue is empty, in which case he or she goes to the cashier.

     * The time for the customer to receive his order once he or she reaches the cashier is a (isosceles) triangular shaped probability density with a minumum of $t_{\min}$ minutes and a maximum of $t_{\max}$ minutes.

     * The arrival times and service times for all customers are independent.

     In a Jupyter notebook or equivalent, create a Monte Carlo simulation for this situation, which runs for $N$ customers.

     a. Setting $t_{a} = 5$, $t_{\min} = 1$,  $t_{\max} = 5$, and $N=200$, find the probability that the queue reaches $10$ customers or more.

     b.  How small must $t_{\max}$ to make the probability of a $10$ or more person queue be less than $10\%$.  If this is impossible given the other parameter values, adjust $t_a$ to make this possible.

     c. Returning to the case in part a.  What is the effect on the probability that the queue reaches $10$ customers or more if there are two cashiers (and double the staff preparing drinks and food), each with the same triangular shaped density for service times.



