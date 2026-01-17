#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
from io import BytesIO
import json
import csv
import PyPDF2
import sqlite3
from unidecode import unidecode
con = sqlite3.connect("test.db")
cur = con.cursor()

# cur.execute("DROP TABLE persons")
# cur.execute("DROP TABLE thesis")
# cur.execute("DROP TABLE directed")
# cur.execute("DROP TABLE jury")
# cur.execute("DROP TABLE reviewed")

if cur.execute("SELECT name FROM sqlite_master where name='persons'").fetchone() is None:
    cur.execute("CREATE TABLE persons(fullname, firstname, surname, ppn, UNIQUE(fullname))")

if cur.execute("SELECT name FROM sqlite_master where name='genders'").fetchone() is None:
    cur.execute("CREATE TABLE genders(firstname, gender, numbers, UNIQUE(firstname))")

if cur.execute("SELECT name FROM sqlite_master where name='thesis'").fetchone() is None:
    cur.execute("CREATE TABLE thesis(id PRIMARY KEY, fullname, domain, ppn, FOREIGN KEY (fullname) REFERENCES persons(fullname))")

    
if cur.execute("SELECT name FROM sqlite_master where name='directed'").fetchone() is None:
    cur.execute("CREATE TABLE directed(id, fullname, ppn, FOREIGN KEY (fullname) REFERENCES persons(fullname), FOREIGN KEY (id) REFERENCES thesis(id))")


if cur.execute("SELECT name FROM sqlite_master where name='jury'").fetchone() is None:
    cur.execute("CREATE TABLE jury(id, fullname, ppn, FOREIGN KEY (fullname) REFERENCES persons(fullname), FOREIGN KEY (id) REFERENCES thesis(id))")


if cur.execute("SELECT name FROM sqlite_master where name='reviewed'").fetchone() is None:
    cur.execute("CREATE TABLE reviewed(id, fullname, ppn, FOREIGN KEY (fullname) REFERENCES persons(fullname), FOREIGN KEY (id) REFERENCES thesis(id))")

# cur.execute("DROP TABLE cnu") 
if cur.execute("SELECT name FROM sqlite_master where name='cnu'").fetchone() is None:
    cur.execute("CREATE TABLE cnu(gender, fullname, firstname, surname, rank, section, ppn)")

if cur.execute("SELECT name FROM sqlite_master where name='years'").fetchone() is None:
    cur.execute("CREATE TABLE years(id, year, FOREIGN KEY (id) REFERENCES thesis(id))")

# cur.execute("DROP TABLE jury_poste")         
if cur.execute("SELECT name FROM sqlite_master where name='jury_poste'").fetchone() is None:
    cur.execute("CREATE TABLE jury_poste(rank, section, year, committee)")

# cur.execute("DROP TABLE is_in_jury_poste")     
if cur.execute("SELECT name FROM sqlite_master where name='is_in_jury_poste'").fetchone() is None:
    cur.execute("CREATE TABLE is_in_jury_poste(fullname, committee, FOREIGN KEY (fullname) REFERENCES cnu(fullname), FOREIGN KEY (committee) REFERENCES jury_poste(committee),   CONSTRAINT UC_in_jury UNIQUE (fullname,committee))")
    

    

def clean_up():
    distincts = cur.execute("SELECT DISTINCT id, fullname FROM reviewed").fetchall()
    cur.execute("DELETE FROM reviewed")
    cur.executemany("INSERT OR IGNORE INTO reviewed VALUES(?, ?)", distincts)
    con.commit()

    distincts = cur.execute("SELECT DISTINCT id, fullname FROM jury").fetchall()
    cur.execute("DELETE FROM jury")
    cur.executemany("INSERT OR IGNORE INTO jury VALUES(?, ?)", distincts)
    con.commit()

    distincts = cur.execute("SELECT DISTINCT id, fullname FROM directed").fetchall()
    cur.execute("DELETE FROM directed")
    cur.executemany("INSERT OR IGNORE INTO directed VALUES(?, ?)", distincts)
    con.commit()

    
    # 

    # persons = cur.execute("SELECT DISTINCT fullname FROM persons").fetchall()
    # for p in persons:
    #     fullname=p[0]
    #     nf = unidecode(fullname).lower()
    #     if "'" not in nf and "'" not in fullname:
    #         cur.execute("UPDATE OR IGNORE persons SET fullname='"+nf+"' where fullname='"+fullname+"'")        
    
    

# if cur.execute("SELECT name FROM sqlite_master where name='juried'").fetchone() is None:
#     cur.execute("CREATE TABLE juried(docid, fullname, UNIQUE(fullname))")
    

def get_gender(name,names):
    name_lower = name.lower()    
    name_parts = name.split()

    for part_name in [part.lower() for part in name_parts[0:]]:
        if part_name in names:
            return names[part_name]

        
    return None


def load_probable_genders_no_accent():
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

def load_probable_genders_no_accent():
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
            if year < 1960: # we don't keep overly old data
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
    data=[(unidecode(d), names[d], numbers[d]) for d in names]
    cur.executemany("INSERT OR IGNORE INTO genders VALUES(?, ?, ?)", data)
    con.commit()
    



# load_probable_genders()    

# load_probable_genders_no_accent()    


    
step=10000

def mk_api_url(start,rows):
    base_url="https://theses.fr/api/v1/theses/recherche/?q=*%20AND%20dateSoutenance:(%5B2015-01-01%20TO%202025-11-20%5D)&tri=dateAsc"
    return(base_url+"&debut="+str(start)+"&nombre="+str(rows))


def mk_person(entry):
    surname = unidecode(entry['nom']).lower()
    firstname = unidecode(entry['prenom']).lower()
    ppn = entry['ppn']
    if ppn:
        fullname = firstname+" "+surname + " " + ppn
    else:
        fullname = firstname+" "+surname        
    return (fullname, firstname , surname, ppn)

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
            fppn, surname, firstname, ppn = mk_person(entry['auteurs'][0])
            persons.add((fppn, surname, firstname, ppn))

            thesis.append((docid, fppn, domain, ppn))

            
            for person in entry['directeurs']:
                fppn, surname, firstname, ppn = mk_person(person)
                persons.add((fppn, surname, firstname, ppn))
                
                directed.append((docid, fppn, ppn))


            for person in entry['rapporteurs']:
                fppn, surname, firstname, ppn = mk_person(person)
                persons.add((fppn, surname, firstname,ppn))
                
                reviewed.append((docid, fppn, ppn))

            for person in entry['examinateurs']:
                fppn, surname, firstname, ppn= mk_person(person)
                persons.add((fppn, surname, firstname, ppn))                
                jury.append((docid, fppn, ppn))

    data=list(persons)
    print("saving")
    cur.executemany("INSERT OR IGNORE INTO persons VALUES(?, ?, ?, ?)", data)

    cur.executemany("INSERT OR IGNORE INTO thesis VALUES(?, ?, ?, ?)", thesis)
    
    cur.executemany("INSERT OR IGNORE INTO directed VALUES(?, ?, ?)", directed)
    cur.executemany("INSERT OR IGNORE INTO jury VALUES(?, ?, ?)", jury)
    cur.executemany("INSERT OR IGNORE INTO reviewed VALUES(?, ?, ?)", reviewed)        
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


def print_total_users():
    h=cur.execute("SELECT COUNT(fullname) from persons JOIN genders ON LOWER(persons.firstname)=genders.firstname  where genders.gender='H'").fetchall()[0][0]
    f=cur.execute("SELECT COUNT(fullname) from persons JOIN genders ON LOWER(persons.firstname)=genders.firstname  where genders.gender='F'").fetchall()[0][0]
    tot = cur.execute("SELECT COUNT(fullname) from persons").fetchall()[0][0]
    print("We have in store (assumed) %i female and %i male persons, for a total of %i. (out of %i persons)" % (f, h, f+h, tot))

    # reviews=cur.execute("SELECT COUNT(*) from jury").fetchall()[0][0]
    # print(f"We have {reviews} thesis review")



    
print_total_users()    

def improve_gender():
    import gender_guesser.detector as gender

    missing =[(p[0],p[1]) for p in cur.execute("SELECT persons.firstname, persons.fullname from persons LEFT JOIN genders ON LOWER(persons.firstname)=genders.firstname where genders.gender is Null").fetchall()]

    new = []
    for (fname,fullname) in missing:
        d = gender.Detector()
        name = fname.split(" ")[0]
        guess=d.get_gender(name)
        if guess=='male':
            res='H'
        elif guess=='female':
            res='F'
        else:
            continue
        print(fname)
        cur.execute("INSERT OR IGNORE INTO genders VALUES(?, ?, ?)", (fname.lower(), res, 1))
        con.commit()


def improve_gender_cnu():
    import gender_guesser.detector as gender

    missing =[(p[0],p[1]) for p in cur.execute("SELECT cnu.firstname, cnu.fullname from cnu LEFT JOIN genders ON LOWER(cnu.firstname)=genders.firstname where genders.gender is Null").fetchall()]

    new = []
    for (fname,fullname) in missing:
        name = fname.split(" ")[0]
        name = name.split("-")[0]
        print(name)        
        gender  = cur.execute(f"SELECT genders.gender from genders where genders.firstname='{name}'").fetchall()
        if gender:
            print(gender[0][0])
            
            cur.execute("INSERT OR IGNORE INTO genders VALUES(?, ?, ?)", (fname.lower(), gender[0][0], 1))
            con.commit()

def improve_gender_bis():
    import gender_guesser.detector as gender


    missing =[(p[0],p[1]) for p in cur.execute("SELECT persons.firstname, persons.fullname from persons LEFT JOIN genders ON LOWER(persons.firstname)=genders.firstname where genders.gender is Null").fetchall()]

    new = []
    for (fname,fullname) in missing:
        name = fname.split(" ")[0]
        name = name.split("-")[0].replace("'","''")
        print(name)        
        gender  = cur.execute(f"SELECT genders.gender from genders where genders.firstname='{name}'").fetchall()
        if gender:
            print(gender[0][0])
            
            cur.execute("INSERT OR IGNORE INTO genders VALUES(?, ?, ?)", (fname.lower(), gender[0][0], 1))
            con.commit()
                    

    
# init_db()


# improve_gender()

# improve_gender_bis()     
    

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


        
def load_cnu(f, allow_dup, year, section):
    data = []
    persons = set()
 
    # name list from INSEE
    with open(f, 'r', encoding='utf-8', newline='') as name_file:
        name_reader = csv.reader(name_file, delimiter=',')
        for row in name_reader:
            if len(row) < 12:
                continue
            if row[1] == 'Civilité':
                continue
            if row[1]=='M.':
                gender='H'
            elif row[1]=='Mme':
                gender='F'
            else :
                print(row[1])
            if row[9]=='Professeur des Universités':
                rank='PU'
            elif row[9]=='Maître de conférences':
                rank='MCF'
            else:
                rank='Other'
            surname=unidecode(row[3].lower())
            firstname=unidecode(row[7].lower())
            college=row[11]
            fullname=firstname + " " + surname
            fn = fullname.replace("'","''")
            if allow_dup or (not cur.execute(f"SELECT * from cnu where cnu.fullname='{fn}'").fetchall()):
                data.append( (gender,firstname + " " + surname,firstname,surname, rank, section, None))

    cur.executemany("INSERT OR IGNORE INTO cnu VALUES(?, ?, ?, ?, ?, ?, ?)", data)
    con.commit()


def link_cnu(domain):
    # after running load cnu, cnu.fullname jsut contains the full name, while persons.fullname might contain in addition the thesis.fr ppn identifier
    cnu = [p[0] for p in cur.execute("SELECT cnu.fullname from cnu").fetchall()]

    info_jury= cur.execute(f"SELECT persons.fullname, persons.ppn, COUNT(jury.fullname) as jnum from persons \
    JOIN jury ON persons.fullname=jury.fullname \
    RIGHT JOIN thesis ON thesis.id=jury.id \
    WHERE LOWER(thesis.domain) LIKE '%{domain}%' \
    GROUP BY persons.fullname ORDER BY jnum ").fetchall()


    rev_jury= cur.execute(f"SELECT persons.fullname, persons.ppn, COUNT(reviewed.fullname) as jnum from persons \
    JOIN reviewed ON persons.fullname=reviewed.fullname \
    RIGHT JOIN thesis ON thesis.id=reviewed.id \
    WHERE LOWER(thesis.domain) LIKE '%{domain}%' \
    GROUP BY persons.fullname ORDER BY jnum ").fetchall()


    dir_jury= cur.execute(f"SELECT persons.fullname, persons.ppn, COUNT(directed.fullname) as jnum from persons \
    JOIN directed ON persons.fullname=directed.fullname \
    RIGHT JOIN thesis ON thesis.id=directed.id \
    WHERE LOWER(thesis.domain) LIKE '%{domain}%' \
    GROUP BY persons.fullname ORDER BY jnum ").fetchall()
    
    cs_pers = {}
    ppn_pers = {}
    
    for p in info_jury+rev_jury+dir_jury:
        name = p[0]
        score = p[2]
        ppn_pers[name] = p[1]
        if name in cs_pers:
            cs_pers[name] += score
        else:
            cs_pers[name] = score                

    cs_pers.pop(None)

    data = []
    for person in cnu:
        options = [p for p in cs_pers if person==p or person+" " in p]
        if options:
            cur_opt = options[0]
            for opt in options[1::]:
                if cs_pers[opt] > cs_pers[cur_opt]:
                    cur_opt=opt
            data.append((person, cur_opt))
            cs_pers.pop(cur_opt)

    for pers in data:
        old = pers[0].replace("'", "''")
        target = ppn_pers[pers[1]]
        print(old)
        print(target)
        cur.execute(f"UPDATE cnu set ppn='{target}' where cnu.fullname='{old}'")

    con.commit()    

    




def link_manual_cnu():
 
    # name list from INSEE
    with open("manual_links.csv", 'r', encoding='utf-8', newline='') as name_file:
        name_reader = csv.reader(name_file, delimiter=',')
        for row in name_reader:
            old = row[0]
            target = row[1]
            cur.execute(f"UPDATE cnu set ppn='{target}' where cnu.fullname='{old}'")            
        con.commit()

# get_all_pers= cur.execute("SELECT * from persons \
#     JOIN jury ON persons.fullname=jury.fullname \
#     JOIN reviewed ON persons.fullname=reviewed.fullname \
#     JOIN directed ON directed.fullname=reviewed.fullname \
#     WHERE persons.fullname=").fetchall()



def load_year(api_response):
    data=[]
    for entry in api_response['theses']:
            docid=entry['id']

            year=entry['dateSoutenance'].split("/")[2]
            data.append((docid,year))
    cur.executemany("INSERT OR IGNORE INTO years VALUES(?, ?)", data)
    con.commit()
    
def init_year():
    url=mk_api_url(0,5)
    print(url)
    init = json.load(BytesIO(requests.get(url).content))
    total_results = init["totalHits"]
    print(total_results)
    load_year(init)
    for i in range(0,int(total_results/step+1)):        
        start=i*step
        url=mk_api_url(start,step)
        print(url)
        res = json.load(BytesIO(requests.get(url).content))
        load_year(res)                


        

# init_year()            

def load_op_poste():
    data = []
    for year in range(2015, 2026):
        f = f"operation_poste/{year}.csv"
        # name list from INSEE
        with open(f, 'r', encoding='utf-8', newline='') as name_file:
            poste_reader = csv.reader(name_file, delimiter=',')
            for row in poste_reader:
                if row[0] != "nature":
                    rank=row[0]
                    section=row[1]
                    committee=unidecode(row[4].lower())
                    print(committee)

                    data.append((rank,section,year,committee))
    cur.executemany("INSERT OR IGNORE INTO jury_poste VALUES(?, ?, ?, ?)", data)
    con.commit()

# load_op_poste()    

def link_op_poste_cnu():
    cnu_names = cur.execute("SELECT cnu.fullname, cnu.surname, cnu.firstname from cnu").fetchall()
    
    fullnames = [c[0] for c in cnu_names]    
    surnames = [c[1] for c in cnu_names]
    
    # duplicate_surnames = [i for i in set(surnames) if surnames.count(i) > 1]
    duplicate_fullnames = [i for i in set(fullnames) if fullnames.count(i) > 1]

    unique_fullnames = [c for c in cnu_names if c[0] not in duplicate_fullnames]
    
    committees = cur.execute("SELECT committee from jury_poste").fetchall()

    for c in unique_fullnames:
        fn1 = c[1] + " " + c[2]
        fn2 = c[2] + " " + c[1]
        # is_unique_surname = c[1] not in duplicate_surnames
        for com in committees:
            if fn1 in com[0] or fn2 in com[0]:
                print("found match")
                cur.execute("INSERT OR IGNORE INTO is_in_jury_poste VALUES(?, ?)", (c[0],com[0]))
                con.commit()                
            # elif (is_unique_surname and (" "+c[1]+" " in com[0])):
            #     print(f"{c} is in {com[0]}")
            

# link_op_poste_cnu()    
    





# load_cnu('cnu_27_2023.csv', False, 2023, 27)
# load_cnu('cnu_26_2023.csv', False, 2023, 26)
# load_cnu('cnu_25_2023.csv', False, 2023, 25)


# load_cnu('cnu_27_2019.csv', False, 2019, 27)
# load_cnu('cnu_26_2019.csv', False, 2019, 26)
# load_cnu('cnu_25_2019.csv', False, 2019, 25)

    
# link_cnu("informatique")
# link_cnu("mathématiques")


# link_manual_cnu()

