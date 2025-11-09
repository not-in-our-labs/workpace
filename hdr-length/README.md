# Is the length of the HDR biased by gender in computer science?

TLDR: probably not

HDR is an additional French diploma needed to be able to be a full professor, or be a standalone PhD advisor.

The script in this folder automatically found the length of the HDR in computer science. The two distrubtions are as follows.

Total number of male HDR scraped:1472
Total number of female HDR scraped:427 

## Number of pages
Mean (Male): 149.7975543478261
Mean (Female): 148.28103044496487
Median (Male): 135.0
Median (Female): 132
Standard dev (Male): 78.91712627881063
Standard dev (Female): 69.51168379115491

TtestResult(statistic=np.float64(0.3585790497608295), pvalue=np.float64(0.7199499221718594), df=np.float64(1897.0))
KstestResult(statistic=np.float64(0.033582374503614704), pvalue=np.float64(0.8344768637480245), statistic_location=np.int64(135), statistic_sign=np.int8(-1))

The density functions are as follows, with male distribution in blue  and female distribution in orange.

![density functions for the length of HDRs by gender ](hdr-length-density-function-M-blue-W-orange.png)


## Limitations

The gender of each authors is *approximated* and might be incorrect. The approximation is based on a French database of names, each being associated to its majority gender representation. This is of course incorrect, and further name does not to be linked with gender. Yet, in the current society, this enables to get an overall valid estimation. To note, there is also a bias, as some foreign names not contained in the database where excluded from the analysis.

However, for french authors, the estimation should be rather accurate.


