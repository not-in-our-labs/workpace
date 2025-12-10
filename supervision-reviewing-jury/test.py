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

if cur.execute("SELECT name FROM sqlite_master where name='persons'").fetchone() is None:
    cur.execute("CREATE TABLE persons(fullname, firstname, surname, UNIQUE(fullname))")

if cur.execute("SELECT name FROM sqlite_master where name='genders'").fetchone() is None:
    cur.execute("CREATE TABLE genders(firstname, gender, numbers, UNIQUE(firstname))")

if cur.execute("SELECT name FROM sqlite_master where name='thesis'").fetchone() is None:
    cur.execute("CREATE TABLE thesis(id PRIMARY KEY, fullname, domain, FOREIGN KEY (fullname) REFERENCES persons(fullname))")

    
if cur.execute("SELECT name FROM sqlite_master where name='directed'").fetchone() is None:
    cur.execute("CREATE TABLE directed(id, fullname, FOREIGN KEY (fullname) REFERENCES persons(fullname), FOREIGN KEY (id) REFERENCES thesis(id))")


if cur.execute("SELECT name FROM sqlite_master where name='jury'").fetchone() is None:
    cur.execute("CREATE TABLE jury(id, fullname, FOREIGN KEY (fullname) REFERENCES persons(fullname), FOREIGN KEY (id) REFERENCES thesis(id))")


if cur.execute("SELECT name FROM sqlite_master where name='reviewed'").fetchone() is None:
    cur.execute("CREATE TABLE reviewed(id, fullname, FOREIGN KEY (fullname) REFERENCES persons(fullname), FOREIGN KEY (id) REFERENCES thesis(id))")
    

# if cur.execute("SELECT name FROM sqlite_master where name='reviewed'").fetchone() is None:
#     cur.execute("CREATE TABLE reviewed(docid, fullname, UNIQUE(fullname))")


# if cur.execute("SELECT name FROM sqlite_master where name='juried'").fetchone() is None:
#     cur.execute("CREATE TABLE juried(docid, fullname, UNIQUE(fullname))")
    

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
            if row[2]=='periode': #skip first line
                continue
            name=row[1].lower()
            g=row[0]
            year=int(row[2])
            number=int(row[3])
            if year != 2020: # we only keep the data from 2020, average year in our dataset
                continue
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
    data=[(d, names[d], numbers[d]) for d in names]
    cur.executemany("INSERT OR IGNORE INTO genders VALUES(?, ?, ?)", data)
    con.commit()
    



load_probable_genders()    



    
step=10000

def mk_api_url(start,rows):
    base_url="https://theses.fr/api/v1/theses/recherche/?q=*%20AND%20dateSoutenance:(%5B2015-01-01%20TO%202025-11-20%5D)&tri=dateAsc"
    return(base_url+"&debut="+str(start)+"&nombre="+str(rows))


def mk_person(entry):
    surname = entry['nom']
    firstname = entry['prenom']
    fullname = firstname+" "+surname 
    return (fullname, firstname , surname )

def load_response(api_response):
    persons = set()
    thesis = []
    directed = []
    jury = []
    reviewed = []
    for entry in api_response['theses']:
            docid=entry['id']
            domain = entry['discipline']

            if len(entry['auteurs']) != 1:
                continue
            ppn, surname, firstname = mk_person(entry['auteurs'][0])
            persons.add((ppn, surname, firstname))

            thesis.append((docid, ppn, domain))

            
            for person in entry['directeurs']:
                ppn, surname, firstname = mk_person(person)
                persons.add((ppn, surname, firstname))
                
                directed.append((docid, ppn))


            for person in entry['rapporteurs']:
                ppn, surname, firstname = mk_person(person)
                persons.add((ppn, surname, firstname))
                
                reviewed.append((docid, ppn))

            for person in entry['examinateurs']:
                ppn, surname, firstname = mk_person(person)
                persons.add((ppn, surname, firstname))
                
            jury += [(docid, ppn)]                

    data=list(persons)
    print("saving")
    cur.executemany("INSERT OR IGNORE INTO persons VALUES(?, ?, ?)", data)

    cur.executemany("INSERT OR IGNORE INTO thesis VALUES(?, ?, ?)", thesis)
    
    cur.executemany("INSERT OR IGNORE INTO directed VALUES(?, ?)", directed)
    cur.executemany("INSERT OR IGNORE INTO jury VALUES(?, ?)", jury)
    cur.executemany("INSERT OR IGNORE INTO reviewed VALUES(?, ?)", reviewed)        
    con.commit()
    
def init_db():
    url=mk_api_url(0,5)
    print(url)
    init = json.load(BytesIO(requests.get(url).content))
    total_results = init["totalHits"]
    print(total_results)
    load_response(init)
    for i in range(0,int(total_results/step+1)):        
        start=i*step
        url=mk_api_url(start,step)
        print(url)
        res = json.load(BytesIO(requests.get(url).content))
        load_response(res)                

# init_db()


# def get_pages(docid):  
#     try:
#       url = cur.execute("SELECT  url from author WHERE docid=%i" % int(docid)).fetchall()[0][0]        
#       print(url)
#       file = BytesIO(requests.get(url).content)
#       # opened file as reading (r) in binary (b) mode
#       # file = open('https://theses.hal.science/tel-00321615/file/Nguyen.Gia-Toan_1986_these.pdf',            'rb')
#       # store data in pdfReader
#       pdfReader = PyPDF2.PdfReader(file)
#       # count number of pages
#       totalPages = len(pdfReader.pages)
#       # print number of pages
#       return(totalPages)
#     except (PyPDF2.errors.PdfReadError, requests.exceptions.SSLError):
#         cur.execute("INSERT OR IGNORE INTO invalidurls(docid) VALUES (%i)" % (docid))
#         con.commit()
#         return None

# def has_invalid_url(docid):
#     res=cur.execute("SELECT  * from invalidurls WHERE docid=%i" % (docid)).fetchall()
#     return(res != [])
    


# def fetch_pages(docid):
#     current_pages = cur.execute("SELECT * from pages WHERE docid=%i" % (docid)).fetchall()
#     if current_pages == []:
#         if has_invalid_url(docid):
#             print("Ignoring doc %i due to invalid url" % docid)
#         else:
#             length=get_pages(docid)
#             if length:
#                 cur.execute("INSERT OR IGNORE INTO pages(docid,length) VALUES (%i, %i)" % (docid, length))
#                 con.commit()
#     else:
#         print("Document %i has %i pages." % (docid, current_pages[0][1]))
        
        


# def test(test):
#     user=cur.execute("SELECT  * from author WHERE url='%s'"%test).fetchall()
#     docid= int(user[0][0])
#     fetch_pages(docid)
    


# def print_total_users():
#     full=cur.execute("SELECT COUNT(author.docid) from author").fetchall()[0][0]
#     h=cur.execute("SELECT COUNT(author.docid) from author JOIN genders ON author.firstname=genders.firstname  where genders.gender='H'").fetchall()[0][0]
#     f=cur.execute("SELECT COUNT(author.docid) from author JOIN genders ON author.firstname=genders.firstname  where genders.gender='F'").fetchall()[0][0]
#     print("We have in store (assumed) %i female and %i male phd authors, for a total of %i usable thesis. (out of %i total thesis)" % (f, h, f+h, full))




#     h_valid=cur.execute("SELECT COUNT(*) from author \
#     JOIN genders ON author.firstname=genders.firstname \
#     JOIN pages ON author.docid=pages.docid \
#     where genders.gender='H'").fetchall()[0][0]
#     f_valid=cur.execute("SELECT COUNT(*) from author \
#     JOIN genders ON author.firstname=genders.firstname \
#     JOIN pages ON author.docid=pages.docid \
#     where genders.gender='F'").fetchall()[0][0]
#     print("Successfully loaded %i female page counts and %i male page counts" % (f_valid,h_valid))

#     h_sum=cur.execute("SELECT SUM(pages.length) from author \
#     JOIN genders ON author.firstname=genders.firstname \
#     JOIN pages ON author.docid=pages.docid \
#     where genders.gender='H'").fetchall()[0][0]
#     f_sum=cur.execute("SELECT SUM(pages.length) from author \
#     JOIN genders ON author.firstname=genders.firstname \
#     JOIN pages ON author.docid=pages.docid \
#     where genders.gender='F'").fetchall()[0][0]
#     print("Average of %i female page counts and %i male page counts" % (f_sum/f_valid,h_sum/h_valid))

    

#     found_pages = cur.execute("SELECT COUNT(*) from author \
#     JOIN pages ON author.docid=pages.docid").fetchall()[0][0]

#     # boom = cur.execute("SELECT * from author \
#     # LEFT JOIN pages ON author.docid=pages.docid").fetchall()
#     # print(boom)
    
#     missing_pages = cur.execute("SELECT COUNT(*) from author \
#     JOIN genders ON author.firstname=genders.firstname \
#     LEFT JOIN pages ON author.docid=pages.docid \
#     where pages.length is null").fetchall()[0][0]

#     print("Fetched %i thesis length, missing %i" % (found_pages, missing_pages))


    
    
# print_total_users()

# docid_missing_pages = cur.execute("SELECT author.docid from author \
#     JOIN genders ON author.firstname=genders.firstname \
#     LEFT JOIN pages ON author.docid=pages.docid \
#     where pages.length is null").fetchall()

# for d in docid_missing_pages:
#     docid = d[0]
#     fetch_pages(docid)    



    
# step=1000

# def mk_theses_id_api_url(start,rows):
#     base_url="https://api.archives-ouvertes.fr/search/?q=*:*&fq=docType_s:THESE&fq=defenseDateY_i:[2015%20TO%202025]&fl=committee_s&fl=director_s&fl=docid&sort=docid asc"
#     return(base_url+"&start="+str(start)+"&rows="+str(rows))
#     # remark: we use HAL, but note that theses.fr returns a similar number of thesis that are accessible online for the same time period.


# def load_jury_response(api_response):
#     data=[]
#     for entry in api_response['response']['docs']:
#         docid=entry['docid']        
#         for director in entry['director_s']:
#             d = director.split(" ")
#             firstname = d[0].lower()
#             surname = " ".join(d[1::]).lower()
            
#         if '_s' in entry:

#             surname=entry['authLastName_s'][0]
#             firstname=entry['authFirstName_s'][0]
#             url=entry['files_s'][0]
#             date=entry['defenseDateY_i']           
#             fullname = firstname+" "+surname
#             domain = entry['primaryDomain_s']
#             data+=[(docid,fullname,firstname.lower(),date,url,domain)]
#     cur.executemany("INSERT OR IGNORE INTO author VALUES(?, ?, ?, ?, ?, ?)", data)
#     con.commit()
    
# def init_db():
#     url=mk_jury_api_url(0,5)
#     print(url)
#     init = json.load(BytesIO(requests.get(url).content))
#     total_results = init["response"]["numFound"]
#     print(total_results)
#     load_response(init)
#     for i in range(0,int(total_results/step+1)):        
#         start=i*step
#         url=mk_api_url(start,1000)
#         print(url)
#         res = json.load(BytesIO(requests.get(url).content))
#         load_response(res)                
