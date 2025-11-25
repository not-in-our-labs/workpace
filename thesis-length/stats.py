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


def make_graph(h_list, f_list, force_pic, long_name, short_name,with_range):    
    f_av = statistics.mean(f_list)
    h_av = statistics.mean(h_list)
    total_av = statistics.mean(h_list+f_list)
    abs_diff = (f_av-h_av)/total_av
    print(abs_diff)

    # print("Successfully loaded %i female page counts and %i male page counts" % (len(f_list),len(h_list)))    
    # print("Average of %i female page counts and %i male page counts" % (f_av,h_av))
    ks_test = stats.ks_2samp(h_list, f_list)
    # print(ks_test)
    # if p < 0.05, we reject the null hypothesis, that is, the hypothesis that the distributions are the same.
    # we only keep domains/subdomains with enough data point
    # We generate corresponding figures
    if force_pic or (ks_test.pvalue < 0.05 and len(h_list + f_list) > 500):

        print(long_name)

        plt.suptitle("Density function for PhD thesis length in pages\n %s" % (long_name))

        plt.title(f"Dataset of {len(h_list)} male vs {len(f_list)} female PhD authors ({len(f_list)/len(f_list+h_list):.0%} females), France, 2015 to 2025\n \
Kolmogorov-Smirnov test with pvalue {ks_test.pvalue:.5f} \n \
Female page average {f_av:.0f}, male average {h_av:.0f}, f-h normalized difference : {abs_diff:.1%} \
", size="small")


      

        
        plt.xlabel("Page length")
        plt.ylabel("Density")
        plt.hist(h_list,bins="auto",color="tab:purple",
                 range=with_range,
                 density=True,histtype="step", label="male")            
                # add vertical line at median
        median = statistics.median(h_list)
        last_decile = np.percentile(h_list, 90)
        plt.axvline(median, color='tab:purple', linestyle='--',label="median")
        plt.axvline(last_decile, color='tab:purple', linestyle='--',label="last decile")

        
        plt.hist(f_list,bins="auto",color="tab:red",
                 range=with_range,
                 density=True,histtype="step", label="female")

        # add vertical line at median
        median = statistics.median(f_list)
        last_decile = np.percentile(f_list, 90)        
        plt.axvline(median, color='tab:red', linestyle='--')
        plt.axvline(last_decile, color='tab:red', linestyle='--')        
        
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

# print_domain("shs")

# print subset of fulldomains


# for dom in domains_fullnames:
#      dom_fullname=get_full_name(dom)
#      sql_cond = "AND author.domain LIKE '" + dom + "%'"
#      print_domain(sql_cond, dom, dom_fullname, False,None)


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

print_zoom('info', (0,400))
print_zoom('shs', (0,1000))

