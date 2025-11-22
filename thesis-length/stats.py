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

    

domains_fullnames = {'sdu': 'Sciences of the Universe [physics]', 'sde': 'Environmental Sciences', 'phys': 'Physics [physics]', 'scco': 'Cognitive science', 'math': 'Mathematics [math]', 'chim': 'Chemical Sciences', 'nlin': 'Nonlinear Sciences [physics]', 'shs': 'Humanities and Social Sciences', 'sdv': 'Life Sciences [q-bio]', 'stat': 'Statistics [stat]', 'info': 'Computer Science [cs]', 'spi': 'Engineering Sciences [physics]', 'qfin': 'Quantitative Finance [q-fin]'}


def get_full_name(dom):
    if dom in domains_fullnames:
        return(domains_fullnames[dom])
    else:
        url="https://api.archives-ouvertes.fr/search/?q=*:*&fq=docType_s:THESE&fq=primaryDomain_s:%s&fl=en_domainAllCodeLabel_fs&row=1" % dom
        api_response = json.load(BytesIO(requests.get(url).content))
        entry = api_response['response']['docs'][0]
        return(entry['en_domainAllCodeLabel_fs'][0].split("_")[2])

# print(len(domains_fullnames))
# get_main_domains()

def get_full_domains():
    domains =  [i[0] for i in cur.execute("SELECT DISTINCT(domain) from author").fetchall()]
    return(set(domains))


def print_domain(dom):
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
    where genders.gender='H' \
    and author.domain LIKE '" + dom + "%'").fetchall()]

    f_list= [ p[0] for p in cur.execute("SELECT pages.length from author \
    JOIN genders ON author.firstname=genders.firstname \
    JOIN pages ON author.docid=pages.docid \
    where genders.gender='F' \
    and author.domain LIKE '" + dom + "%'").fetchall()]

    if h_list==[] or f_list==[]:
        return
    
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
    # We generate corresponding figures
    if ks_test.pvalue < 0.05:
        dom_fullname=get_full_name(dom)
        print(dom_fullname)

        plt.suptitle("Density function for thesis length in pages\n %s" % (dom_fullname))

        plt.title(f"Dataset of {len(h_list)} male vs {len(f_list)} female PhD authors, in France, between 2015 and 2025\n \
Kolmogorov-Smirnov test with pvalue {ks_test.pvalue:.5f} \n \
Female page average {f_av:.0f}, male average {h_av:.0f}, f-h normalized difference : {abs_diff:.1%} \
", size="small")
        
        plt.xlabel("Page length")
        plt.ylabel("Density")
        
        plt.hist(h_list,bins="auto",color="tab:purple",
                 # range=(0,800),
                 density=True,histtype="step", label="male")
        plt.hist(f_list,bins="auto",color="tab:red",
                 # range=(0,800),
                 density=True,histtype="step", label="female")
        
        plt.legend()
        plt.tight_layout()
        plt.savefig(result_folder + dom+".png")
        plt.clf()        
        # plt.show()            

# print_domain("shs")

# print subset of fulldomains 
# for dom in domains_fullnames:        
#     print_domain(dom)
    

for dom in get_full_domains():
    print_domain(dom)
