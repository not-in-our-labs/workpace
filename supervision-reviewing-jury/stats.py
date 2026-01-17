#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
from io import BytesIO
import json
import csv
import PyPDF2
import statistics
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
import re

plt.rcParams['figure.dpi'] = 200

import sqlite3
con = sqlite3.connect('file:test.db?mode=ro', uri=True)
cur = con.cursor()
from unidecode import unidecode    

 
def like(a, b) :
    return unidecode(a).lower()==unidecode(b).lower()

con.create_function("likenoaccent", 2, like)        

result_folder = "plots/"

def print_total_users():
    h=cur.execute("SELECT COUNT(fullname) from persons JOIN genders ON LOWER(persons.firstname)=genders.firstname  where genders.gender='H'").fetchall()[0][0]
    f=cur.execute("SELECT COUNT(fullname) from persons JOIN genders ON LOWER(persons.firstname)=genders.firstname  where genders.gender='F'").fetchall()[0][0]
    tot = cur.execute("SELECT COUNT(fullname) from persons").fetchall()[0][0]
    print("We have in store (assumed) %i female and %i male persons, for a total of %i. (out of %i persons)" % (f, h, f+h, tot))

    
    # f_valid=cur.execute("SELECT COUNT(*) from author \
    # JOIN genders ON author.firstname=genders.firstname \
    # JOIN pages ON author.docid=pages.docid \
    # where genders.gender='F'").fetchall()[0][0]
    # print("Successfully loaded %i female page counts and %i male page counts" % (f_valid,h_valid))

    # h_sum=cur.execute("SELECT SUM(pages.length) from author \
    # JOIN genders ON author.firstname=genders.firstname \
    # JOIN pages ON author.docid=pages.docid \
    # where genders.gender='H'").fetchall()[0][0]
    # f_sum=cur.execute("SELECT SUM(pages.length) from author \
    # JOIN genders ON author.firstname=genders.firstname \
    # JOIN pages ON author.docid=pages.docid \
    # where genders.gender='F'").fetchall()[0][0]
    # print("Average of %i female page counts and %i male page counts" % (f_sum/f_valid,h_sum/h_valid))

    


    # found_pages = cur.execute("SELECT COUNT(*) from author \
    # JOIN pages ON author.docid=pages.docid").fetchall()[0][0]

    # # boom = cur.execute("SELECT * from author \
    # # LEFT JOIN pages ON author.docid=pages.docid").fetchall()
    # # print(boom)
    
    # missing_pages = cur.execute("SELECT COUNT(*) from author \
    # JOIN genders ON author.firstname=genders.firstname \
    # LEFT JOIN pages ON author.docid=pages.docid \
    # where pages.length is null").fetchall()[0][0]

    # print("Fetched %i thesis length, missing %i" % (found_pages, missing_pages))




    
    
print_total_users()



def trim(counts,bins,tmax,tmin):
    nc = []
    nb = []
    found_non_small = False
    co = list(counts)
    bi = list(bins)[:-1]
    co.reverse()
    bi.reverse()
          
    for c,b in zip(co,bi):
        if not(found_non_small) and c/tmax < tmin:
            continue
        found_non_small = True
        nc.append(c)
        nb.append(b)
    nc.reverse()
    nb.reverse()
    nb.append(nb[-1:][0]+1)
    return(nc,nb)

male_color = "purple"
female_color = "orange"

def do_hist(h_data, f_data, mrange=None):
    hist_alpha=0.4

    trim_min=0.005
    
    h_bins=range(min(h_data), max(h_data) + 1, 1)
    h_counts, h_bins = np.histogram(h_data, bins=h_bins, density=True,range=mrange)


    f_bins=range(min(f_data), max(f_data) + 1, 1)
    f_counts, f_bins = np.histogram(f_data, bins=f_bins, density=True,range=mrange)


    maximum = max([max(h_counts),max(f_counts)])
    
    h_ncounts, h_nbins = trim(h_counts,h_bins,maximum, trim_min)
    f_ncounts, f_nbins = trim(f_counts,f_bins,maximum, trim_min)   

    
    plt.stairs(np.array(h_ncounts),np.array(h_nbins), fill=True,color=f"tab:{male_color}", alpha=hist_alpha, label="male")
    plt.stairs(np.array(f_ncounts),np.array(f_nbins), fill=True,color=f"tab:{female_color}", alpha=hist_alpha, label="female")    

    



def make_graph(h_list, f_list, force_pic, long_name, short_name,with_range, action):
    line_alpha=0.6
    f_av = statistics.mean(f_list)
    h_av = statistics.mean(h_list)
    total_av = statistics.mean(h_list+f_list)
    abs_diff = (f_av-h_av)/total_av


    # print("Successfully loaded %i female page counts and %i male page counts" % (len(f_list),len(h_list)))    
    # print("Average of %i female page counts and %i male page counts" % (f_av,h_av))
    ad_test = stats.anderson_ksamp([h_list, f_list]) 
    # if p < 0.05, we reject the null hypothesis, that is, the hypothesis that the distributions are the same.
    # also, we only keep domains/subdomains with enough data point
    # We generate corresponding figures

    print(ad_test)        
    if force_pic or (ad_test.pvalue < 0.05 and len(h_list + f_list) > 500):

        print(long_name)

        plt.suptitle("Density function for number of %s per person\n %s" % (action, long_name))

        plt.title(f"Dataset of {len(h_list)} male vs {len(f_list)} female ({len(f_list)/len(f_list+h_list):.0%} females), France, 2015 to 2025\n \
Total of {sum(h_list)} male {action} vs {sum(f_list)} female ({sum(f_list)/sum(f_list+h_list):.0%} females)\n \
 Anderson-Darling test with pvalue {ad_test.pvalue:.5f} \n \
Female average {f_av:.2f}, male average {h_av:.2f}, f-h normalized difference : {abs_diff:.1%} \
", size="small")


      

        
        plt.xlabel(f"Number of {action}")
        plt.ylabel("Density")
        
                # add vertical line at median
        median = statistics.median(h_list)
        last_decile = np.percentile(h_list, 90)
        plt.axvline(median, color=f"tab:{male_color}", alpha=line_alpha, linestyle='--',label="male median")
        plt.axvline(last_decile, color=f"tab:{male_color}", alpha=line_alpha, linestyle=(0, (5, 5)),label="male last decile")

        do_hist(h_list, f_list, with_range)        

        # add vertical line at median
        median = statistics.median(f_list)
        last_decile = np.percentile(f_list, 90)        
        plt.axvline(median, color=f"tab:{female_color}", alpha=line_alpha, linestyle='--',label="female median")
        plt.axvline(last_decile,  color=f"tab:{female_color}",alpha=line_alpha,linestyle=(0, (5, 5)),label="female last decile")
        
        plt.legend()
        plt.tight_layout()
        plt.savefig(result_folder + short_name+".png", dpi=300)
        plt.clf()        

    # first_decile = np.percentile(h_list+f_list, 15)
    # last_decile =  np.percentile(h_list+f_list, 85)

    # h_list_first = [i for i in h_list if i <= first_decile]
    # h_list_middle = [i for i in h_list if  first_decile <= i and i <= last_decile]
    # h_list_end = [i for i in h_list if  last_decile <= i]

    # f_list_first = [i for i in f_list if i <= first_decile]
    # f_list_middle = [i for i in f_list if  first_decile <= i and i <= last_decile]
    # f_list_end = [i for i in f_list if  last_decile <= i]

    # if h_list_first!=[] and f_list_first!=[]:        
    #     make_graph(h_list_first, f_list_first, force_pic, long_name + " (only first decile of lengths)", "1-first-decile."+ short_name)
        
    # if h_list_end!=[] and f_list_end!=[]:        
    #     make_graph(h_list_end, f_list_end, force_pic, long_name + " (only last decile of lengths)", "2-last-decile."+ short_name)
    
    # if h_list_middle!=[] and f_list_middle!=[]:            
    #     make_graph(h_list_middle, f_list_middle, force_pic, long_name + " (without first and last decile of lengths)", "3-without-extrem-deciles."+ short_name)    
    
        # plt.show()            

# print_domain()

# # print subset of fulldomains


# # for dom in domains_fullnames:
# #      dom_fullname=get_full_name(dom)
# #      sql_cond = "AND author.domain LIKE '" + dom + "%'"
# #      print_domain(sql_cond, dom, dom_fullname, False,None)


# # for dom in domains_fullnames:
# #      if dom.split('.')[0] != 'info':
# #          continue
# #      dom_fullname=get_full_name(dom)
# #      sql_cond = "AND author.domain LIKE '" + dom + "%'"
# #      print_domain(sql_cond, dom, dom_fullname, True,None)



# def print_zoom(dom, rang):
#     dom_fullname=get_full_name(dom)
#     sql_cond = "AND author.domain LIKE '" + dom + "%'"
#     print_domain(sql_cond, dom+".zoom", dom_fullname, False,rang)

# print_zoom('info', (0,400))
# print_zoom('shs', (0,1000))




def print_all():
    print("")    

    # h_valid= cur.execute("SELECT COUNT(*) from author \
    # JOIN genders ON author.firstname=genders.firstname \
    # JOIN pages ON author.docid=pages.docid \
    # where genders.gender='H' \
    # and author.domain LIKE '" + dom + "%'").fetchall()[0][0]

    # f_valid= cur.execute("SELECT COUNT(*) from author \
    # JOIN genders ON author.firstname=genders.firstname \
    # JOIN pages ON author.docid=pages.docid \
    # where genders.gender='F' \
    # and author.domain LIKE '" + dom + "%'").fetchall()[0][0]  
    # print("Successfully loaded %i female page counts and %i male page counts" % (f_valid,h_valid))


    h_directed= [p[1] for p in cur.execute("SELECT directed.fullname, COUNT(*) from directed \
    RIGHT JOIN persons ON persons.fullname=directed.fullname \
    RIGHT JOIN genders ON LOWER(persons.firstname)=genders.firstname \
    where genders.gender='H' \
    and directed.fullname is not Null\
    GROUP BY  directed.fullname").fetchall()]
    
    f_directed= [ p[1] for p in cur.execute("SELECT directed.fullname, COUNT(*) from directed \
    RIGHT JOIN persons ON persons.fullname=directed.fullname \
    RIGHT JOIN genders ON LOWER(persons.firstname)=genders.firstname \
    where genders.gender='F' \
    and directed.fullname is not Null \
    GROUP BY  directed.fullname").fetchall()]
    
    # if h_list==[] or f_list==[]:
    #     print("empty")
    #     return
    
    make_graph(h_directed, f_directed, False, "All domains", "supervised.all", None, "thesis supervision")



    h_jury= [ p[1] for p in cur.execute("SELECT jury.fullname, COUNT(*) from jury \
    RIGHT JOIN persons ON persons.fullname=jury.fullname \
    RIGHT JOIN genders ON LOWER(persons.firstname)=genders.firstname \
    where genders.gender='H' \
    and jury.fullname is not Null \
    GROUP BY  jury.fullname").fetchall()]
    
    f_jury= [ p[1] for p in cur.execute("SELECT jury.fullname, COUNT(*) from jury \
    RIGHT JOIN persons ON persons.fullname=jury.fullname \
    RIGHT JOIN genders ON LOWER(persons.firstname)=genders.firstname \
    where genders.gender='F' \
    and jury.fullname is not Null \
    GROUP BY  jury.fullname").fetchall()]
    
    # if h_list==[] or f_list==[]:
    #     print("empty")
    #     return


    
    make_graph(h_jury, f_jury, False, "All domains", "examiner.all", None, "thesis examination")




    h_reviewed= [ p[1] for p in cur.execute("SELECT reviewed.fullname, COUNT(*) from reviewed \
    RIGHT JOIN persons ON persons.fullname=reviewed.fullname \
    RIGHT JOIN genders ON LOWER(persons.firstname)=genders.firstname \
    where genders.gender='H' \
    and reviewed.fullname is not Null \
    GROUP BY  reviewed.fullname").fetchall()]
    
    f_reviewed= [ p[1] for p in cur.execute("SELECT reviewed.fullname, COUNT(*) from reviewed \
    RIGHT JOIN persons ON persons.fullname=reviewed.fullname \
    RIGHT JOIN genders ON LOWER(persons.firstname)=genders.firstname \
    where genders.gender='F' \
    and reviewed.fullname is not Null \
    GROUP BY  reviewed.fullname").fetchall()]
    
    # if h_list==[] or f_list==[]:
    #     print("empty")
    #     return


    
    make_graph(h_reviewed, f_reviewed, False, "All domains", "review.all", None, "thesis review")

# print_all()    



def print_domain(dom):
    sdom= " ".join(re.findall("[a-zA-Z]+", dom))
    ldom= dom.replace("'", "''")
    print("Managing "+dom)

    # h_valid= cur.execute("SELECT COUNT(*) from author \
    # JOIN genders ON author.firstname=genders.firstname \
    # JOIN pages ON author.docid=pages.docid \
    # where genders.gender='H' \
    # and author.domain LIKE '" + dom + "%'").fetchall()[0][0]

    # f_valid= cur.execute("SELECT COUNT(*) from author \
    # JOIN genders ON author.firstname=genders.firstname \
    # JOIN pages ON author.docid=pages.docid \
    # where genders.gender='F' \
    # and author.domain LIKE '" + dom + "%'").fetchall()[0][0]  
    # print("Successfully loaded %i female page counts and %i male page counts" % (f_valid,h_valid))


    h_directed= [ p[1] for p in cur.execute("SELECT directed.fullname, COUNT(*) from directed \
    RIGHT JOIN persons ON persons.fullname=directed.fullname \
    RIGHT JOIN thesis ON thesis.id=directed.id \
    RIGHT JOIN genders ON LOWER(persons.firstname)=genders.firstname \
    where genders.gender='H' \
    and directed.fullname is not Null\
    AND LOWER(thesis.domain) LIKE '%"+ldom.lower()+"%' \
    GROUP BY directed.fullname").fetchall()]
    
    f_directed= [ p[1] for p in cur.execute("SELECT directed.fullname, COUNT(*) from directed \
    RIGHT JOIN persons ON persons.fullname=directed.fullname \
    RIGHT JOIN thesis ON thesis.id=directed.id \
    RIGHT JOIN genders ON LOWER(persons.firstname)=genders.firstname \
    where genders.gender='F' \
    and directed.fullname is not Null\
    AND LOWER(thesis.domain) LIKE '%"+ldom.lower()+"%' \
    GROUP BY  directed.fullname").fetchall()]
    
    # if h_list==[] or f_list==[]:
    #     print("empty")
    #     return

    
    make_graph(h_directed, f_directed, False, dom, "supervised."+sdom, None, "thesis supervision")



    h_jury= [ p[1] for p in cur.execute("SELECT jury.fullname, COUNT(*) from jury \
    RIGHT JOIN persons ON persons.fullname=jury.fullname \
    RIGHT JOIN thesis ON thesis.id=jury.id \
    RIGHT JOIN genders ON LOWER(persons.firstname)=genders.firstname \
    where genders.gender='H' \
    and jury.fullname is not Null \
    AND LOWER(thesis.domain) LIKE '%"+ldom.lower()+"%' \
    GROUP BY  jury.fullname").fetchall()]
    
    f_jury= [ p[1] for p in cur.execute("SELECT jury.fullname, COUNT(*) from jury \
    RIGHT JOIN persons ON persons.fullname=jury.fullname \
    RIGHT JOIN thesis ON thesis.id=jury.id \
    RIGHT JOIN genders ON LOWER(persons.firstname)=genders.firstname \
    where genders.gender='F' \
    and jury.fullname is not Null \
    AND LOWER(thesis.domain) LIKE '%"+ldom.lower()+"%' \
    GROUP BY  jury.fullname").fetchall()]
    
    # if h_list==[] or f_list==[]:
    #     print("empty")
    #     return


    make_graph(h_jury, f_jury, False, dom, "examiner."+sdom, None, "thesis examination")




    h_reviewed= [ p[1] for p in cur.execute("SELECT reviewed.fullname, COUNT(*) from reviewed \
    RIGHT JOIN persons ON persons.fullname=reviewed.fullname \
    RIGHT JOIN thesis ON thesis.id=reviewed.id \
    RIGHT JOIN genders ON LOWER(persons.firstname)=genders.firstname \
    where genders.gender='H' \
    and reviewed.fullname is not Null \
    AND LOWER(thesis.domain) LIKE '%"+ldom.lower()+"%' \
    GROUP BY  reviewed.fullname").fetchall()]
    
    f_reviewed= [ p[1] for p in cur.execute("SELECT reviewed.fullname, COUNT(*) from reviewed \
    RIGHT JOIN persons ON persons.fullname=reviewed.fullname \
    RIGHT JOIN thesis ON thesis.id=reviewed.id \
    RIGHT JOIN genders ON LOWER(persons.firstname)=genders.firstname \
    where genders.gender='F' \
    and reviewed.fullname is not Null \
    AND LOWER(thesis.domain) LIKE '%"+ldom.lower()+"%' \
    GROUP BY  reviewed.fullname").fetchall()]
    
    # if h_list==[] or f_list==[]:
    #     print("empty")
    #     return


    
    make_graph(h_reviewed, f_reviewed, False, dom, "review."+sdom, None, "thesis review")        


domains =  [p[0] for p in cur.execute("SELECT domain, COUNT(id) as num_t from thesis GROUP BY domain ORDER BY num_t DESC ").fetchall() if p[1] > 400]

# for domain in domains:
#     # if domain != 'Informatique':
#     #     continue
#     print_domain(domain)




# f_jury=cur.execute("SELECT * from jury \
# RIGHT JOIN persons ON persons.fullname=jury.fullname \
# RIGHT JOIN thesis ON thesis.id=jury.id \
# where jury.fullname is not Null \
# AND LOWER(thesis.domain) LIKE '%informatique%' \
# AND persons.surname LIKE '%%'").fetchall()
# print(f_jury)



        
# f_jury=cur.execute("SELECT * from jury \
# RIGHT JOIN persons ON persons.fullname=jury.fullname \
# RIGHT JOIN thesis ON thesis.id=jury.id \
# where jury.fullname is not Null \
# AND thesis.id = ''").fetchall()
# print(f_jury)




# Limitations:
# some homonyms are present on theses.fr, + theses.fr not always link person with its ppn

def print_cnu(section):
    sectiontext=section
    section=section.replace("'","")
    secstripped = section.replace("(","").replace(")","").replace(",","")
    sdom= f"sec{secstripped}"
    ldom= f"Section cnu {section}"
    dom=ldom
    print("Managing "+ldom)


    h_cnu = cur.execute(f"SELECT cnu.fullname from cnu \
    where cnu.gender='H' and cnu.section IN {section} ").fetchall()
    print(f"Number of male: {len(h_cnu)}")

    f_cnu = cur.execute(f"SELECT cnu.fullname from cnu \
    where cnu.gender='F' and cnu.section IN {section}").fetchall()
    print(f"Number of female: {len(f_cnu)}")


    h_cnu_pu = cur.execute(f"SELECT cnu.fullname from cnu \
    where cnu.gender='H' and cnu.rank='PU' and cnu.section IN {section} ").fetchall()
    print(f"Number of male PU: {len(h_cnu_pu)}")

    f_cnu_pu = cur.execute(f"SELECT cnu.fullname from cnu \
    where cnu.gender='F' and cnu.rank='PU' and cnu.section IN {section}").fetchall()
    print(f"Number of female PU: {len(f_cnu_pu)}")


    h_cnu_mcf = cur.execute(f"SELECT cnu.fullname from cnu \
    where cnu.gender='H' and cnu.rank='MCF' and cnu.section IN {section} ").fetchall()
    print(f"Number of male MCF: {len(h_cnu_mcf)}")

    f_cnu_mcf = cur.execute(f"SELECT cnu.fullname from cnu \
    where cnu.gender='F' and cnu.rank='MCF' and cnu.section IN {section}").fetchall()
    print(f"Number of female MCF: {len(f_cnu_mcf)}")


    
    h_directed= [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(directed.fullname) from cnu \
    JOIN directed ON cnu.ppn=directed.ppn \
    where cnu.gender='H'  and cnu.section IN {section} \
    GROUP BY directed.fullname").fetchall()]
    
    f_directed= [ p[1] for p in cur.execute(f"SELECT directed.fullname, COUNT(*) from directed \
    JOIN cnu ON cnu.ppn=directed.ppn \
    where cnu.gender='F' and cnu.section IN {section} \
    GROUP BY directed.fullname").fetchall()]
    
    
    # if h_list==[] or f_list==[]:
    #     print("empty")
    #     return
    h_directed += [0 for i in range(0,len(h_cnu) - len(h_directed))]
    f_directed += [0 for i in range(0,len(f_cnu) - len(f_directed))]        

    
    make_graph(h_directed, f_directed, False, dom, "supervised."+sdom, None, "thesis supervision")

        
    h_directed_mcf= [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(directed.fullname) from cnu \
    JOIN directed ON cnu.ppn=directed.ppn \
    where cnu.gender='H'  and cnu.rank='MCF'  and cnu.section IN {section} \
    GROUP BY directed.fullname").fetchall()]
    
    f_directed_mcf= [ p[1] for p in cur.execute(f"SELECT directed.fullname, COUNT(*) from directed \
    JOIN cnu ON cnu.ppn=directed.ppn \
    where cnu.gender='F' and cnu.rank='MCF'  and cnu.section IN {section} \
    GROUP BY directed.fullname").fetchall()]
    
    
    # if h_list==[] or f_list==[]:
    #     print("empty")
    #     return
    h_directed_mcf += [0 for i in range(0,len(h_cnu_mcf) - len(h_directed_mcf))]
    f_directed_mcf += [0 for i in range(0,len(f_cnu_mcf) - len(f_directed_mcf))]        

    
    make_graph(h_directed_mcf, f_directed_mcf, False, dom, "supervised.mcf."+sdom, None, "thesis supervision from MCF")


    h_directed_pu= [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(directed.fullname) from cnu \
    JOIN directed ON cnu.ppn=directed.ppn \
    where cnu.gender='H'  and cnu.rank='PU'  and cnu.section IN {section} \
    GROUP BY directed.fullname").fetchall()]
    
    f_directed_pu= [ p[1] for p in cur.execute(f"SELECT directed.fullname, COUNT(*) from directed \
    JOIN cnu ON cnu.ppn=directed.ppn \
    where cnu.gender='F' and cnu.rank='PU'  and cnu.section IN {section} \
    GROUP BY directed.fullname").fetchall()]
    
    
    # if h_list==[] or f_list==[]:
    #     print("empty")
    #     return
    h_directed_pu += [0 for i in range(0,len(h_cnu_pu) - len(h_directed_pu))]
    f_directed_pu += [0 for i in range(0,len(f_cnu_pu) - len(f_directed_pu))]        

    
    make_graph(h_directed_pu, f_directed_pu, False, dom, "supervised.pu."+sdom, None, "thesis supervision from PU")    


    h_jury= [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(jury.fullname) from cnu \
    JOIN jury ON cnu.ppn=jury.ppn \
    where cnu.gender='H'  and cnu.section IN {section} \
    GROUP BY jury.fullname").fetchall()]
    
    f_jury= [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(jury.fullname) from cnu \
    JOIN jury ON cnu.ppn=jury.ppn \
    where cnu.gender='F' and cnu.section IN {section} \
    GROUP BY jury.fullname").fetchall()]
    
    # if h_list==[] or f_list==[]:
    #     print("empty")
    #     return
    h_jury += [0 for i in range(0,len(h_cnu) - len(h_jury))]
    f_jury += [0 for i in range(0,len(f_cnu) - len(f_jury))]        

    h_over_tw = len([p for p in h_jury if 20 <= p])
    f_over_tw = len([p for p in f_jury if 20 <= p])
    print(f"Women over twenty jury: {f_over_tw}, {f_over_tw/len(f_jury):.0%} ")
    print(f"Men over twenty jury: {h_over_tw}, {h_over_tw/len(h_jury):.0%}")
    
    make_graph(h_jury, f_jury, False, dom, "examiner."+sdom, None, "thesis examination")

    # make_graph(h_jury, f_jury, False, dom, "examiner.zoom1."+sdom, (0,25), "thesis examination")
    # make_graph(h_jury, f_jury, False, dom, "examiner.zoom2."+sdom, (25,60), "thesis examination")    


    h_jury_pu= [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(jury.fullname) from cnu \
    JOIN jury ON cnu.ppn=jury.ppn \
    where cnu.gender='H' and cnu.rank='PU'  and cnu.section IN {section} \
    GROUP BY jury.fullname").fetchall()]
    
    f_jury_pu= [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(jury.fullname) from cnu \
    JOIN jury ON cnu.ppn=jury.ppn \
    where cnu.gender='F' and cnu.rank='PU' and cnu.section IN {section} \
    GROUP BY jury.fullname").fetchall()]
    
    h_jury_pu += [0 for i in range(0,len(h_cnu_pu) - len(h_jury_pu))]
    f_jury_pu += [0 for i in range(0,len(f_cnu_pu) - len(f_jury_pu))]        
    
    h_jury_mcf= [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(jury.fullname) from cnu \
    JOIN jury ON cnu.ppn=jury.ppn \
    where cnu.gender='H' and cnu.rank='MCF'  and cnu.section IN {section} \
    GROUP BY jury.fullname").fetchall()]
    
    f_jury_mcf= [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(jury.fullname) from cnu \
    JOIN jury ON cnu.ppn=jury.ppn \
    where cnu.gender='F' and cnu.rank='MCF' and cnu.section IN {section} \
    GROUP BY jury.fullname").fetchall()]

    h_jury_mcf += [0 for i in range(0,len(h_cnu_mcf) - len(h_jury_mcf))]
    f_jury_mcf += [0 for i in range(0,len(f_cnu_mcf) - len(f_jury_mcf))]        
    

    make_graph(h_jury_pu, f_jury_pu, True, dom, "examiner.pu."+sdom, None, "thesis examination from PU")

    make_graph(h_jury_mcf, f_jury_mcf, True, dom, "examiner.mcf."+sdom, None, "thesis examination from MCF")        
    
    h_reviewed=  [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(reviewed.fullname) from cnu \
    JOIN reviewed ON cnu.ppn=reviewed.ppn \
    where cnu.gender='H'  and cnu.section IN {section} \
    GROUP BY reviewed.fullname").fetchall()]
    
    f_reviewed= [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(reviewed.fullname) from cnu \
    JOIN reviewed ON cnu.ppn=reviewed.ppn \
    where cnu.gender='F'  and cnu.section IN {section} \
    GROUP BY reviewed.fullname").fetchall()]

    h_reviewed += [0 for i in range(0,len(h_cnu) - len(h_reviewed))]
    f_reviewed += [0 for i in range(0,len(f_cnu) - len(f_reviewed))]            

    
    make_graph(h_reviewed, f_reviewed, False, dom, "review."+sdom, None, "thesis review")


    h_jury_poste=  [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(is_in_jury_poste.fullname) from cnu \
    JOIN is_in_jury_poste ON cnu.fullname=is_in_jury_poste.fullname \
    where cnu.gender='H'  and cnu.section IN {section} \
    GROUP BY is_in_jury_poste.fullname").fetchall()]
    
    f_jury_poste= [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(is_in_jury_poste.fullname) from cnu \
    JOIN is_in_jury_poste ON cnu.fullname=is_in_jury_poste.fullname \
    where cnu.gender='F'  and cnu.section IN {section} \
    GROUP BY is_in_jury_poste.fullname").fetchall()]

    h_jury_poste += [0 for i in range(0,len(h_cnu) - len(h_jury_poste))]
    f_jury_poste += [0 for i in range(0,len(f_cnu) - len(f_jury_poste))]            

    h_over_tw = len([p for p in h_jury_poste if 5 <= p])
    f_over_tw = len([p for p in f_jury_poste if 5 <= p])

    total=cur.execute(f"SELECT COUNT(*) from jury_poste where section IN {sectiontext}").fetchall()[0][0]
    empty=cur.execute(f"SELECT COUNT(*) from jury_poste where section IN {sectiontext} and committee='\\n'").fetchall()[0][0]
    
    print(f"Proportion of unregistered committees {empty/total:.0%}")
    print(f"Women over five committee: {f_over_tw}, {f_over_tw/len(f_jury_poste):.0%} ")
    print(f"Men over five committee: {h_over_tw}, {h_over_tw/len(h_jury_poste):.0%}")
    
    make_graph(h_jury_poste, f_jury_poste, False, dom, "jury_poste."+sdom, None, "hiring committee participation")



    h_jury_poste_pu=  [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(is_in_jury_poste.fullname) from cnu \
    JOIN is_in_jury_poste ON cnu.fullname=is_in_jury_poste.fullname \
    where cnu.gender='H' and cnu.rank='PU'  and cnu.section IN {section} \
    GROUP BY is_in_jury_poste.fullname").fetchall()]
    
    f_jury_poste_pu= [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(is_in_jury_poste.fullname) from cnu \
    JOIN is_in_jury_poste ON cnu.fullname=is_in_jury_poste.fullname \
    where cnu.gender='F'  and cnu.rank='PU' and cnu.section IN {section} \
    GROUP BY is_in_jury_poste.fullname").fetchall()]

    h_jury_poste_pu += [0 for i in range(0,len(h_cnu_pu) - len(h_jury_poste_pu))]
    f_jury_poste_pu += [0 for i in range(0,len(f_cnu_pu) - len(f_jury_poste_pu))]            


    h_jury_poste_mcf=  [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(is_in_jury_poste.fullname) from cnu \
    JOIN is_in_jury_poste ON cnu.fullname=is_in_jury_poste.fullname \
    where cnu.gender='H' and cnu.rank='MCF'  and cnu.section IN {section} \
    GROUP BY is_in_jury_poste.fullname").fetchall()]
    
    f_jury_poste_mcf= [ p[1] for p in cur.execute(f"SELECT cnu.fullname, COUNT(is_in_jury_poste.fullname) from cnu \
    JOIN is_in_jury_poste ON cnu.fullname=is_in_jury_poste.fullname \
    where cnu.gender='F'  and cnu.rank='MCF' and cnu.section IN {section} \
    GROUP BY is_in_jury_poste.fullname").fetchall()]

    h_jury_poste_mcf += [0 for i in range(0,len(h_cnu_mcf) - len(h_jury_poste_mcf))]
    f_jury_poste_mcf += [0 for i in range(0,len(f_cnu_mcf) - len(f_jury_poste_mcf))]            
    
    make_graph(h_jury_poste_pu, f_jury_poste_pu, True, dom, "jury_poste.pu."+sdom, None, "hiring committee \n participation from PU")
    make_graph(h_jury_poste_mcf, f_jury_poste_mcf, True, dom, "jury_poste.mcf."+sdom, None, "hiring committee \n participation from MCF")
    

def eval_gender_guessing():
    f_cnu =  [p[0] for p in cur.execute("SELECT cnu.firstname from cnu WHERE cnu.gender='F'").fetchall()]

    f_guessed = [p[0] for p in cur.execute("SELECT cnu.firstname from cnu JOIN genders ON LOWER(cnu.firstname)=genders.firstname WHERE genders.gender='F'").fetchall()]


    h_cnu =  [p[0] for p in cur.execute("SELECT cnu.firstname from cnu WHERE cnu.gender='H'").fetchall()]

    h_guessed = [p[0] for p in cur.execute("SELECT cnu.firstname from cnu JOIN genders ON LOWER(cnu.firstname)=genders.firstname WHERE genders.gender='H'").fetchall()]
    
    print(f"Comparing with the official cnu section 25,26 and 27 data, we are guessing correctly {len(f_guessed)/len(f_cnu):.3%} of females and {len(h_guessed)/len(h_cnu):.3%} of males")

# eval_gender_guessing()          

print_cnu("('27')")
print_cnu("('26')")
print_cnu("('25')")
print_cnu("('25','26','27')")

def print_info_per_year():
    for i in range(2014,2026):
        h=cur.execute(f"SELECT COUNT(thesis.id) from thesis JOIN persons ON persons.fullname=thesis.fullname \
        JOIN genders ON persons.firstname=genders.firstname \
        JOIN years on thesis.id=years.id \
        where genders.gender='H' AND thesis.domain LIKE '%informatique%' AND years.year='{i}'").fetchall()[0][0]
        
        f=cur.execute(f"SELECT COUNT(thesis.id) from thesis JOIN persons ON persons.fullname=thesis.fullname \
        JOIN genders ON persons.firstname=genders.firstname \
        JOIN years on thesis.id=years.id \
        where genders.gender='F' AND thesis.domain LIKE '%informatique%' AND years.year='{i}'").fetchall()[0][0]
        if f != 0 and h != 0:
            print(f"For {i}, we have in store (assumed) {f}  female and {h} male phd authors, for a total of {f/(f+h):.1%}.")
    
# print_info_per_year() 

def print_info_per_year_cnu(section):
    
    for i in range(2014,2026):
        h=cur.execute(f"SELECT COUNT(thesis.id) from thesis JOIN persons ON persons.fullname=thesis.fullname \
        JOIN genders ON persons.firstname=genders.firstname \
        JOIN years on thesis.id=years.id \
        JOIN directed on directed.id=thesis.id \
        JOIN cnu on cnu.ppn=directed.ppn \
        where genders.gender='H' and years.year='{i}' and cnu.section={section}").fetchall()[0][0]
        
        f=cur.execute(f"SELECT COUNT(thesis.id) from thesis JOIN persons ON persons.fullname=thesis.fullname \
        JOIN genders ON persons.firstname=genders.firstname \
        JOIN years on thesis.id=years.id \
        JOIN directed on directed.id=thesis.id \
        JOIN cnu on cnu.ppn=directed.ppn \
        where genders.gender='F' AND years.year='{i}' and cnu.section={section}").fetchall()[0][0]
        if f != 0 and h != 0:
            print(f"For {i}, we have in store (assumed) {f}  female and {h} male phd authors for thesis in cnu section {section}, for a total of {f/(f+h):.1%}.")
    
# print_info_per_year_cnu(27)
# print_info_per_year_cnu(26)
# print_info_per_year_cnu(25)

def print_info_cnu_ppn(rank, sec):

    f_pu = cur.execute(f"SELECT COUNT(cnu.fullname) from cnu\
        where cnu.gender='F' and rank='{rank}' and cnu.section={sec}").fetchall()[0][0]

    f_pu_no_ppn= cur.execute(f"SELECT COUNT(cnu.fullname), cnu.ppn from cnu\
        where cnu.gender='F' and rank='{rank}' and cnu.section={sec} and   (cnu.ppn is null or not cnu.ppn)").fetchall()[0][0]

    h_pu = cur.execute(f"SELECT COUNT(cnu.fullname), cnu.ppn from cnu\
        where cnu.gender='H' and rank='{rank}' and cnu.section={sec}").fetchall()[0][0]

    
    h_pu_no_ppn= cur.execute(f"SELECT COUNT(cnu.fullname), cnu.ppn from cnu\
        where cnu.gender='H' and rank='{rank}' and cnu.section={sec} and   (cnu.ppn is null or not cnu.ppn)").fetchall()[0][0]

    print(f"We have {f_pu_no_ppn/f_pu:.1%} of women {rank} sec {sec} without ppn, vs {h_pu_no_ppn/h_pu:.1%} for men ")

# print_info_cnu_ppn("PU", 27)
# print_info_cnu_ppn("MCF", 27)
# print_info_cnu_ppn("PU", 26)
# print_info_cnu_ppn("MCF", 26)
# print_info_cnu_ppn("PU", 25)
# print_info_cnu_ppn("MCF", 25)
