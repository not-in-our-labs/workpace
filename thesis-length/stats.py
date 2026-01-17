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


import sqlite3
con = sqlite3.connect('file:test.db?mode=ro', uri=True)
cur = con.cursor()
    

result_folder = "plots/"

def print_total_users():
    h=cur.execute("SELECT COUNT(author.docid) from author JOIN genders ON author.firstname=genders.firstname  where genders.gender='H'").fetchall()[0][0]
    f=cur.execute("SELECT COUNT(author.docid) from author JOIN genders ON author.firstname=genders.firstname  where genders.gender='F'").fetchall()[0][0]
    print("We have in store (assumed) %i female and %i male phd authors, for a total of %i." % (f, h, f+h))




    h_valid=cur.execute("SELECT COUNT(*) from author \
    JOIN genders ON author.firstname=genders.firstname \
    JOIN pages ON author.docid=pages.docid \
    where genders.gender='H'").fetchall()[0][0]
    f_valid=cur.execute("SELECT COUNT(*) from author \
    JOIN genders ON author.firstname=genders.firstname \
    JOIN pages ON author.docid=pages.docid \
    where genders.gender='F'").fetchall()[0][0]
    print("Successfully loaded %i female page counts and %i male page counts" % (f_valid,h_valid))

    h_sum=cur.execute("SELECT SUM(pages.length) from author \
    JOIN genders ON author.firstname=genders.firstname \
    JOIN pages ON author.docid=pages.docid \
    where genders.gender='H'").fetchall()[0][0]
    f_sum=cur.execute("SELECT SUM(pages.length) from author \
    JOIN genders ON author.firstname=genders.firstname \
    JOIN pages ON author.docid=pages.docid \
    where genders.gender='F'").fetchall()[0][0]
    print("Average of %i female page counts and %i male page counts" % (f_sum/f_valid,h_sum/h_valid))

    

    found_pages = cur.execute("SELECT COUNT(*) from author \
    JOIN pages ON author.docid=pages.docid").fetchall()[0][0]

    # boom = cur.execute("SELECT * from author \
    # LEFT JOIN pages ON author.docid=pages.docid").fetchall()
    # print(boom)
    
    missing_pages = cur.execute("SELECT COUNT(*) from author \
    JOIN genders ON author.firstname=genders.firstname \
    LEFT JOIN pages ON author.docid=pages.docid \
    where pages.length is null").fetchall()[0][0]

    print("Fetched %i thesis length, missing %i" % (found_pages, missing_pages))




    
    
print_total_users()

def get_main_domains():
    domains =  [i[0].split(".")[0] for i in cur.execute("SELECT DISTINCT(domain) from author").fetchall()]
    print(set(domains))

    domains_fullnames={}

    for dom in set(domains):    
        domains_fullnames[dom]=get_full_name(dom)
    print(domains_fullnames)    
    print(len(domains_fullnames))

    
with open('domains.json', 'r') as file:
    domains_fullnames = json.load(file)


def get_full_name(dom):
    if dom in domains_fullnames:
        return(domains_fullnames[dom])
    else:
        print("Need to fetch full domain name for" + dom)
        url="https://api.archives-ouvertes.fr/search/?q=*:*&fq=docType_s:THESE&fq=primaryDomain_s:%s&fl=en_domainAllCodeLabel_fs&row=1" % dom
        api_response = json.load(BytesIO(requests.get(url).content))
        entry = api_response['response']['docs'][0]
        return(entry['en_domainAllCodeLabel_fs'][0].split("_")[2])

    
# print(len(domains_fullnames))
# get_main_domains()

def get_full_domains():
    domains =  [i[0] for i in cur.execute("SELECT DISTINCT(domain) from author").fetchall()]

    # mdomains =  [i[0].split(".")[0] for i in cur.execute("SELECT DISTINCT(domain) from author").fetchall()]
    # for d in mdomains:
    #     if d not in domains:
    #         print(d)
    return(set(domains))



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
            last =b
            continue
        if not(found_non_small):
            nb.append(b)            
            found_non_small = True
        nc.append(c)
        nb.append(b)
    nc.reverse()
    nb.reverse()    

    return(nc,nb)

male_color = "purple"
female_color = "orange"

def do_hist(h_data, f_data, mrange=None):
    hist_alpha=0.4

    trim_min=0.005
    
    h_bins=range(min(h_data), max(h_data) + 1, 1)
    h_counts, h_bins = np.histogram(h_data, bins='auto', density=True,range=mrange)


    f_bins=range(min(f_data), max(f_data) + 1, 1)
    f_counts, f_bins = np.histogram(f_data, bins='auto', density=True,range=mrange)


    maximum = max([max(h_counts),max(f_counts)])
    
    h_ncounts, h_nbins = trim(h_counts,h_bins,maximum, trim_min)
    f_ncounts, f_nbins = trim(f_counts,f_bins,maximum, trim_min)   

    
    plt.stairs(np.array(h_ncounts),np.array(h_nbins), fill=True,color=f"tab:{male_color}", alpha=hist_alpha, label="male")
    plt.stairs(np.array(f_ncounts),np.array(f_nbins), fill=True,color=f"tab:{female_color}", alpha=hist_alpha, label="female")    



def make_graph(h_list, f_list, force_pic, long_name, short_name,with_range):
    line_alpha=0.6
    
    f_av = statistics.mean(f_list)
    h_av = statistics.mean(h_list)
    total_av = statistics.mean(h_list+f_list)
    abs_diff = (f_av-h_av)/total_av
    print(abs_diff)


    if not(force_pic) and len(h_list + f_list) < 500:
        return
    # print("Successfully loaded %i female page counts and %i male page counts" % (len(f_list),len(h_list)))    
    # print("Average of %i female page counts and %i male page counts" % (f_av,h_av))
    ad_test = stats.anderson_ksamp([h_list, f_list]) 
    # print(ks_test)
    # if p < 0.05, we reject the null hypothesis, that is, the hypothesis that the distributions are the same.
    # we only keep domains/subdomains with enough data point
    # We generate corresponding figures
    if force_pic or (ad_test.pvalue < 0.05 and len(h_list + f_list) > 500):

        print(long_name)

        plt.suptitle("Density function for PhD thesis length in pages\n %s" % (long_name))

        plt.title(f"Dataset of {len(h_list)} male vs {len(f_list)} female PhD authors ({len(f_list)/len(f_list+h_list):.0%} females), France, 2015 to 2025\n \
 Anderson-Darling test with pvalue {ad_test.pvalue:.5f} \n \
Female page average {f_av:.0f}, male average {h_av:.0f}, f-h normalized difference : {abs_diff:.1%} \
", size="small")


      

        
        plt.xlabel("Page length")
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

def print_domain(sql_cond, short_name, long_name, force_pic, with_range):
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

    h_list= [ p[0] for p in cur.execute("SELECT pages.length from author \
    JOIN genders ON author.firstname=genders.firstname \
    JOIN pages ON author.docid=pages.docid \
    where genders.gender='H'" + sql_cond).fetchall()]

    f_list= [ p[0] for p in cur.execute("SELECT pages.length from author \
    JOIN genders ON author.firstname=genders.firstname \
    JOIN pages ON author.docid=pages.docid \
    where genders.gender='F'" + sql_cond).fetchall()]

    if h_list==[] or f_list==[]:
        print("empty")
        return


    make_graph(h_list, f_list, force_pic, long_name, short_name, with_range)


# print_domain("shs")

# print subset of fulldomains


for dom in domains_fullnames:
     dom_fullname=get_full_name(dom)
     sql_cond = "AND author.domain LIKE '" + dom + "%'"
     print_domain(sql_cond, dom, dom_fullname, False,None)


# for dom in domains_fullnames:
#      if dom.split('.')[0] != 'info':
#          continue
#      dom_fullname=get_full_name(dom)
#      sql_cond = "AND author.domain LIKE '" + dom + "%'"
#      print_domain(sql_cond, dom, dom_fullname, True,None)



def print_zoom(dom, rang):
    dom_fullname=get_full_name(dom)
    sql_cond = "AND author.domain LIKE '" + dom + "%'"
    print_domain(sql_cond, dom+".zoom", dom_fullname, False,rang)

# print_zoom('info', (0,400))
# print_zoom('shs', (0,1000))

def print_info_per_year():
    for i in range(2015,2026):
        h=cur.execute("SELECT COUNT(author.docid) from author JOIN genders ON author.firstname=genders.firstname  where genders.gender='H' AND author.domain LIKE '%info%' AND author.year="+str(i)).fetchall()[0][0]
        f=cur.execute("SELECT COUNT(author.docid) from author JOIN genders ON author.firstname=genders.firstname  where genders.gender='F' AND author.domain LIKE '%info%' AND author.year="+str(i)).fetchall()[0][0]
        print(f"For {i}, we have in store (assumed) {f}  female and {h} male phd authors, for a total of {f/(f+h):.1%}.")
    
print_info_per_year()



