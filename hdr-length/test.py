#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
from io import BytesIO
import json
import csv
import PyPDF2
import sqlite3
con = sqlite3.connect("test.db")
cur = con.cursor()

if cur.execute("SELECT name FROM sqlite_master where name='author'").fetchone() is None:
    cur.execute("CREATE TABLE author(docid INTEGER PRIMARY KEY, fullname, firstname, year, url, domain)")

if cur.execute("SELECT name FROM sqlite_master where name='genders'").fetchone() is None:
    cur.execute("CREATE TABLE genders(firstname, gender, UNIQUE(firstname))")

if cur.execute("SELECT name FROM sqlite_master where name='pages'").fetchone() is None:
    cur.execute("CREATE TABLE pages(docid INTEGER PRIMARY KEY, length)")

if cur.execute("SELECT name FROM sqlite_master where name='invalidurls'").fetchone() is None:
    cur.execute("CREATE TABLE invalidurls(docid INTEGER PRIMARY KEY)")


    
step=1000

def mk_api_url(start,rows):
    base_url="https://api.archives-ouvertes.fr/search/?q=*:*&fq=docType_s:HDR&fq=defenseDateY_i:[2000%20TO%202025]&fl=defenseDateY_i&fl=files_s&fl=authLastName_s&fl=authFirstName_s&fl=primaryDomain_s&fl=docid&sort=docid asc"
    return(base_url+"&start="+str(start)+"&rows="+str(rows))


def load_response(api_response):
    data=[]
    for entry in api_response['response']['docs']:
        if 'files_s' in entry:
            docid=entry['docid']
            surname=entry['authLastName_s'][0]
            firstname=entry['authFirstName_s'][0]
            url=entry['files_s'][0]
            date=entry['defenseDateY_i']           
            fullname = firstname+" "+surname
            domain = entry['primaryDomain_s']
            data+=[(docid,fullname,firstname.lower(),date,url,domain)]
    cur.executemany("INSERT OR IGNORE INTO author VALUES(?, ?, ?, ?, ?, ?)", data)
    con.commit()
    
def init_db():
    url=mk_api_url(0,5)
    print(url)
    init = json.load(BytesIO(requests.get(url).content))
    total_results = init["response"]["numFound"]
    print(total_results)
    load_response(init)
    for i in range(0,int(total_results/step+1)):        
        start=i*step
        url=mk_api_url(start,1000)
        print(url)
        res = json.load(BytesIO(requests.get(url).content))
        load_response(res)                

def get_gender(name,names):
    name_lower = name.lower()    
    name_parts = name.split()

    for part_name in [part.lower() for part in name_parts[0:]]:
        if part_name in names:
            return names[part_name]

        
    return None


        
def load_probable_genders():
    names = {}

    numbers = {}    
    # name list from INSEE
    with open('prenoms-2024-liste.csv', 'r', encoding='utf-8', newline='') as name_file:
        name_reader = csv.reader(name_file, delimiter=';')
        for row in name_reader:
            name=row[1].lower()
            g=row[0]
            number=row[3]
            if name in names:
                # if name is less common for this gender, we ignore and skip
                if number<numbers[name]:
                    continue
                
                # we initialize values for a new name    
            if g=='1':
                names[name]="H"
                numbers[name]=number
            elif g=='2':
                names[name]="F"
                numbers[name]=number         
    data=[(d, names[d]) for d in names]
    cur.executemany("INSERT OR IGNORE INTO genders VALUES(?, ?)", data)
    con.commit()
    


# init_db()

    
# load_probable_genders()    




def get_pages(docid):  
    try:
      url = cur.execute("SELECT  url from author WHERE docid=%i" % int(docid)).fetchall()[0][0]        
      print(url)
      file = BytesIO(requests.get(url).content)
      # opened file as reading (r) in binary (b) mode
      # file = open('https://theses.hal.science/tel-00321615/file/Nguyen.Gia-Toan_1986_these.pdf',            'rb')
      # store data in pdfReader
      pdfReader = PyPDF2.PdfReader(file)
      # count number of pages
      totalPages = len(pdfReader.pages)
      # print number of pages
      return(totalPages)
    except PyPDF2.errors.PdfReadError:
        cur.execute("INSERT OR IGNORE INTO invalidurls(docid) VALUES (%i)" % (docid))
        con.commit()
        return None

def has_invalid_url(docid):
    res=cur.execute("SELECT  * from invalidurls WHERE docid=%i" % (docid)).fetchall()
    return(res != [])
    


def fetch_pages(docid):
    current_pages = cur.execute("SELECT * from pages WHERE docid=%i" % (docid)).fetchall()
    if current_pages == []:
        if has_invalid_url(docid):
            print("Ignoring doc %i due to invalid url" % docid)
        else:
            length=get_pages(docid)
            if length:
                cur.execute("INSERT OR IGNORE INTO pages(docid,length) VALUES (%i, %i)" % (docid, length))
                con.commit()
    else:
        print("Document %i has %i pages." % (docid, current_pages[0][1]))
        



def test(test):
    user=cur.execute("SELECT  * from author WHERE url='%s'"%test).fetchall()
    docid= int(user[0][0])
    fetch_pages(docid)
    


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

docid_missing_pages = cur.execute("SELECT author.docid from author \
    JOIN genders ON author.firstname=genders.firstname \
    LEFT JOIN pages ON author.docid=pages.docid \
    where pages.length is null").fetchall()

for d in docid_missing_pages:
    docid = d[0]
    fetch_pages(docid)    
