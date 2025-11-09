# Is the length of the PhD thesis manuscript biased by gender in French computer science?

TLDR: probably, on average, women writes a 10% longer thesis. (but this gap disappears at the HDR level, see ![hdr-length-results](../hdr-length/README.md)


The script in this folder automatically found the length of the French PhDs in computer science from 2015 to 2025. The two distrubtions are as follows.

Total number of PhDs successfully scraped: 10462 male and 4110 female.


## Number of pages of French thesis in computer sciences, by gender, from 2015 to 2025
```
Mean (Male): 193.07790097495698
Mean (Female): 214.21922141119222
Median (Male): 173.0
Median (Female): 181.0
Standard dev (Male): 87.41048539209191
Standard dev (Female): 119.22316831939166

TtestResult(statistic=np.float64(-11.785049774883824), pvalue=np.float64(6.50745349356456e-32), df=np.float64(14570.0))
KstestResult(statistic=np.float64(0.07327466195583965), pvalue=np.float64(3.177214593301979e-14), statistic_location=np.int64(218), statistic_sign=np.int8(1))
```

The density functions are as follows, with male distribution in blue and female distribution in orange. We observe a clear over abundance for females in the range 300-500 pages.

![density functions for the length of PhDs by gender ](thesis-length-distribution-M-blue-W-orange.png)


## Limitations

The gender of each author is *approximated* and might be incorrect. The approximation is based on a French database of names, each being associated to its majority gender representation. This is of course incorrect, and further name does not have to be linked with gender. Yet, in the current society, this enables to get an overall valid estimation. To note, there is also a bias, as some foreign names not contained in the database where excluded from the analysis (2078 entries).

However, for french authors, the estimation should be rather accurate. One question is: are the results biased by some sub-disciplines, which would have a very different gender distribution and thesis length?

The python script was implemented as a one shot thing, to get quick results. 


## Evolution?

By splitting the 10 year period into two, one does not see a very significant evolution w.r.t. the bias. Thesis are getting *slightly* shorter on average, losing 5 or 3 pages. Curiously, the standard devition for males is reducing, while it is increasing for females.

### 2015-2029

```
Mean (Male): 195.47825285661628
Mean (Female): 215.4007336084365
Median (Male): 174.0
Median (Female): 181.0
Standard dev (Male): 92.43607082825044
Standard dev (Female): 113.79406530196886

TtestResult(statistic=np.float64(-7.933647729408499), pvalue=np.float64(2.432214896811569e-15), df=np.float64(7605.0))
KstestResult(statistic=np.float64(0.06774335129328739), pvalue=np.float64(1.179184712249173e-06), statistic_location=np.int64(294), statistic_sign=np.int8(1))
```

### 2020-2025

```
Mean (Male): 190.49166004765686
Mean (Female): 212.88335925349924
Median (Male): 173.0
Median (Female): 181.0
Standard dev (Male): 81.5712393366595
Standard dev (Female): 125.06455099640182

TtestResult(statistic=np.float64(-8.744398928392792), pvalue=np.float64(2.7765903234642577e-18), df=np.float64(6963.0))
KstestResult(statistic=np.float64(0.08326837850936193), pvalue=np.float64(7.289572542072959e-09), statistic_location=np.int64(229), statistic_sign=np.int8(1))
```


