# Ideas for experiments

In general finding out wat it means to evaluate the same model with Cellular Automatons
Possibly we need to do multiple runs to derive a distribution

## Scalabiltiy
Use an initial setting, say:
simulation = 10;
gamma = .10;
beta = 0.25.

_because it is quickly to much i.e. too long, lets take max three round of 10, 15, 20, 25, 30 and make a plot of the average runtime vs gridsize_

## I- or S-based against Mathematical model
Use a kind of default: beta = .35 and gamma similar, so R is around 1?
 * SIR model
 * SEIR model
 
## R_t investigations
in the paper of Textor, the model was fitted to the data, leading to R_t values, however, we don't fit the data and define our values our selves. Nontheless, is R = beta / gamma.

### gridsize
All experiments a to be conducted with grid size .... being the optimum between size and runtime.

Typical values for `beta` as demonstrated in [this work](https://science.sciencemag.org/content/368/6490/489), bibtext in the report: li2020substantial:
 * 0.52 (95% CI: 0.42–0.72) in period 1
 * 0.35 (95% CI: 0.28–0.45) in period 2
 
 Given these values, make ranges for beta= 0.3; 0.4; 0.5; 0.6; 0.7; 0.8; 0.9; including outliers to demonstrate the edges
 
 An indication for R is given in that paper as well, 2 - 3 roughly. I think R=1 is also interesting. So this gives a range for R. 

 Q: how should we limit the total number of combinations?
 
 A: take beta=[0.4:1.0] and R=[1, 2, 2.5, 3], leads already to 4*8=32 scenarios.
 
 ### what to show in the scenario's
 If we want resemble some experiments, we should take a Wuhan-type city, with the number of people in it and present e.g. the number of daily new cases and see whether this resembles to papers. Make a number of graphs for different values of R and show several lines in the plots? 
 
 
 ## Investigate Cellular Automata specifics
 Do experiments that show the effects of the various settings. Apply them on a default 
 
 * investigate the effect of `neighbours`: 
   * `radius` for different values, e.g. 1, 3, 5, 10, 20, 30, 50, 75
   * `gaus` for different values, e.g. 1, 3, 5, 10, 20, 30, 50, 75
   * `all` for different values, e.g. 1, 3, 5, 10, 20, 30, 50, 75
   * `random` for different values, e.g. 1, 3, 5, 10, 20, 30, 50, 75


Inspect variables
* infection rate 
