**Files and description**
Link to the network data can be found in the respective file.

**Survival_rate_with_AIDS_after_t_years.R**  
Survival rate x years after AIDS diagnosis, was reported by (Poorolajal et al., 2016) for x = 2,4,6 for AIDS patients that did not receive ART. To calculate the survival rate for any x >= 0,
the survival rate as function of time was fitted assuming it follows exponential decay.

**plots.py**  
Generating the data for the plot for one mode (e.g. "targeted_m_homo") takes ~35 min. on a medium-high 2016 PC build, totalling to a runtime of roughly 7 hours to generate all plots. 




**Parameters of the HIV model, description, reference.***  
`condom_usage`, proportion of sexual interactions that involve the use of condoms out of all interactions between two gender types, Reece et al. 2010.  
`condom_efficacy`, proportion of sexual interactions that do not result in the transmission of HIV out of all interactions that involve the use of condoms between two genders, Smith et al. 1999 and Weller et al. 1996.  

*If multiple empirical parameter values were reported, e.g. condom usage reported by heterosexual men and condom usage reported by heterosexual women, the mean of the reported values was assigned as parameter value.

**References**   
Reece, M., Herbenick, D., Schick, V., Sanders, S. A., Dodge, B., & Fortenberry, J. D. (2010). Condom use rates in a national probability sample of males and females ages 14 to 94 in the United States. The journal of sexual medicine, 7, 266-276.  
Poorolajal, J., Hooshmand, E., Mahjub, H., Esmailnasab, N., & Jenabi, E. (2016). Survival rate of AIDS disease and mortality in HIV-infected patients: a meta-analysis. Public health, 139, 3-12.
Smith, D. K., Herbst, J. H., Zhang, X., & Rose, C. E. (2015). Condom effectiveness for HIV prevention by consistency of use among men who have sex with men in the United States. Journal of acquired immune deficiency syndromes (1999), 68(3), 337–344.  
Weller, S. C., Davis‐Beaty, K., & Cochrane HIV/AIDS Group. (1996). Condom effectiveness in reducing heterosexual HIV transmission. Cochrane database of systematic reviews, 2012(3).  
