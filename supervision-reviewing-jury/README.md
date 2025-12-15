In several domains and subdomains among chemical sciences, computer science, cognitive sciences, biology, geography, humanities and social sciences, history and physics, we find that the distribution of the length in pages of the PhD thesis are statistically different between men and women.

In all cases EXCEPT history, women's thesis are longer, from 2 to 9 percents longer on average.

In history, the situation is reversed, but only because men write more very long thesis of more than 1000 pages.

Figures illustrating the effects are available in ![plots](plots).

Concrete consequence: it might be worth to be vigilant with the pressure put on womens writing their PhDs, and make sure they don't feel pressured to write long thesis to prove their worth. (see next section for details)



# Interpretation

The effect and gap is not always very significant. However, when looking at Geography, or computer science, we clearly see a shift to the right of the distributions.

 ![geography plot](plots/shs.geo.png)

 ![computer science plot](plots/info.zoom.png)
 

 

This might be explained by the idea that women are more required to make more efforts to prove that they belong in academia, and length might be considered as a proof of work/productivity. Whether this is true, and whether it is caused by advisors with biases expectations, or self put pressure due to general society bias is unclear. A qualitative analysis would help understand the effect (TODO, biblio).




# Methodology
Thesis length were scrapped from a french archive, we have datapoints for all thesis defended in France between January 2015 and December 2025. 
The approximated gender is inferred from the firstname, with the gender of a firstname being assumed to be its most likely one in France in 2020, based on INSEE data.

The length distributions are compared using Kolmogorov-Smirnov test, with distribution deemed statistically distinct with p<0.05.

Possible bias:
 * thesis non available online might introduce a bias in some specific domains.
 * gender is only approximated.
 * using the french database of names makes it so that we are more likely to not be able to gender foreigners.
 * the pdf formatting of some thesis might makes them spuriously longer, or some files might be corrupted. 



