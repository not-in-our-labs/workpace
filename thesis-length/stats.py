#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
from io import BytesIO
import json
import csv
import PyPDF2
import sqlite3
con = sqlite3.connect('file:test.db?mode=ro', uri=True)
cur = con.cursor()
    


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

def get_domains():
    domains =  [i[0].split(".")[0] for i in cur.execute("SELECT DISTINCT(domain) from author").fetchall()]
    print(set(domains))

    domains_fullnames={}

    for dom in set(domains):    
        url="https://api.archives-ouvertes.fr/search/?q=*:*&fq=docType_s:THESE&fq=primaryDomain_s:%s&fl=en_domainAllCodeLabel_fs&row=1" % dom
        api_response = json.load(BytesIO(requests.get(url).content))
        entry = api_response['response']['docs'][0]
        domains_fullnames[dom]=entry['en_domainAllCodeLabel_fs'].split("_")[2]
    print(domain_fullnames)    



domains_fullnames = {'sdu': 'Sciences of the Universe [physics]', 'sde': 'Environmental Sciences', 'phys': 'Physics [physics]', 'scco': 'Cognitive science', 'math': 'Mathematics [math]', 'chim': 'Chemical Sciences', 'nlin': 'Nonlinear Sciences [physics]', 'shs': 'Humanities and Social Sciences', 'sdv': 'Life Sciences [q-bio]', 'stat': 'Statistics [stat]', 'info': 'Computer Science [cs]', 'spi': 'Engineering Sciences [physics]', 'qfin': 'Quantitative Finance [q-fin]'}


def get_or_z(l):
    try:
        return l[0]
    except:
        return 0

def print_domain(dom):
    print("")
    print(domains_fullnames[dom])
    h_valid= cur.execute("SELECT COUNT(*) from author \
    JOIN genders ON author.firstname=genders.firstname \
    JOIN pages ON author.docid=pages.docid \
    where genders.gender='H' \
    and author.domain LIKE '" + dom + "%'").fetchall()[0][0]

    f_valid= cur.execute("SELECT COUNT(*) from author \
    JOIN genders ON author.firstname=genders.firstname \
    JOIN pages ON author.docid=pages.docid \
    where genders.gender='F' \
    and author.domain LIKE '" + dom + "%'").fetchall()[0][0]  
    print("Successfully loaded %i female page counts and %i male page counts" % (f_valid,h_valid))

    h_sum= cur.execute("SELECT SUM(pages.length) from author \
    JOIN genders ON author.firstname=genders.firstname \
    JOIN pages ON author.docid=pages.docid \
    where genders.gender='H' \
    and author.domain LIKE '" + dom + "%'").fetchall()[0][0]

    f_sum= cur.execute("SELECT SUM(pages.length) from author \
    JOIN genders ON author.firstname=genders.firstname \
    JOIN pages ON author.docid=pages.docid \
    where genders.gender='F' \
    and author.domain LIKE '" + dom + "%'").fetchall()[0][0]

    if h_valid==0:
        h_av = 0
    else:
        h_av=h_sum/h_valid

    if f_valid==0:
        f_av = 0
    else:
        f_av=f_sum/f_valid
        

    print("Average of %i female page counts and %i male page counts" % (f_av,h_av))
for dom in domains_fullnames:        
    print_domain(dom)
    
    
