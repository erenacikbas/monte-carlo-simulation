# Monte Carlo Reservoir Simulation
When using Monte Carlo simulations to estimate Original Oil in Place (OOIP), Recoverable Oil in Place (ROIP), or Recoverable Gas in Place (RGIP), it is crucial to understand the uncertainty and variability of the reservoir parameters. This is where the different statistical distributions come into play. Here's how you should approach this:

### Inputs for Distributions:
### Gaussian (Normal) Distribution: 
Requires the mean (mu) and standard deviation (sigma). Often used for parameters that cluster around a mean.
### Log-Normal Distribution: 
Also needs a mean and standard deviation, but these refer to the underlying normal distribution of the logarithm of the variable. Suitable for parameters that cannot be negative and are skewed.
### Triangular Distribution: 
Needs the minimum (left), the most likely (mode), and the maximum (right) values. It is used when the data is limited but the boundaries and mode are known.
### Uniform Distribution: 
Requires the lower (min) and upper (max) limits for the variable. It assumes that any value within the range is equally likely.

### For reservoir parameters:
* Area: Generally uses uniform or triangular distributions if the extent is uncertain.
* Thickness: Can be normal or log-normal, depending on whether thickness measurements are symmetrically distributed or skewed.
* Porosity: Often modeled with normal or log-normal distributions, given that porosity values are bound between 0 and 1.
* Water Saturation: Typically uses a uniform distribution if little is known, or a normal/log-normal distribution if data is available.
* Formation Volume Factor (FVF): Could be modeled with any of the distributions based on data skewness and range.
* Choosing Distributions for OOIP and ROIP (or RGIP) in Monte Carlo Simulations:
* Data Analysis: Look at the historical data or analog data to determine the distribution of each parameter. Parameters may follow a certain distribution historically.
* Expert Judgment: In the absence of data, expert opinion can be utilized to determine likely distributions based on geological understanding.
* Parametric Tests: Perform tests such as Shapiro-Wilk, Kolmogorov-Smirnov, etc., to test the fit of different distributions to your data.
* Non-parametric Methods: If the data does not fit well into common distributions, non-parametric methods that don't assume a particular distribution can be used.

Finally, to estimate OOIP and ROIP with Monte Carlo simulations, you'll combine the random variables generated from their respective distributions to calculate the volume of hydrocarbons in place repeatedly, building a probability distribution of the OOIP and ROIP. This will help to understand the range and likelihood of different outcomes.

# Monte Carlo Reservoir Simulation Steps
1- Generate a PDF or CDF to obtain random continuous variables

For each parameter calculate the history and get PDF using numpy

2- Get a random sample containing each parameter

3- Apply the parameters into the transfer function

4 - Estimate the value of the transfer function

5 - Accumulate statistics

Uniform and Triangular