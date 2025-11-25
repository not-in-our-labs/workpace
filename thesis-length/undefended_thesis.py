#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
from io import BytesIO
import json
import csv
import PyPDF2
import sqlite3
import statistics
con = sqlite3.connect("test.db")
cur = con.cursor()

import matplotlib.pyplot as plt

if cur.execute("SELECT name FROM sqlite_master where name='undefended'").fetchone() is None:
    cur.execute("CREATE TABLE undefended(fullname, firstname, first_inscription_year, domain, UNIQUE(fullname))")


        
def load_cs_undefended():
    data = []
    with open('undefended-thesis-info-2015-2020.csv', 'r', encoding='utf-8', newline='') as name_file:
        undefended_thesis = csv.reader(name_file, delimiter=';')
        for row in undefended_thesis:
            surname, firstname =row[0].lower().split(",")
            firstname = firstname.split(" ")[0]
            date=row[1]
            fullname = firstname + " " + surname
            data += [(fullname, firstname, date, 'info')]
    cur.executemany("INSERT OR IGNORE INTO undefended VALUES(?, ?, ?, ?)", data)
    con.commit()
    


# init_db()

    
load_cs_undefended()



def gender_to_int(g):
    if g[0]=='H':
        return 0
    elif g[0]=='F':
        return 10
    else:
        return 20

def genders_to_int(l):    
    return [gender_to_int(g)  for g in l]

genders_thesis = genders_to_int(cur.execute("SELECT (genders.gender) from author LEFT JOIN genders ON author.firstname=genders.firstname").fetchall())


genders_undefended = genders_to_int(cur.execute("SELECT (genders.gender) from undefended LEFT JOIN genders ON undefended.firstname=genders.firstname").fetchall())

plt.hist(genders_thesis,bins=10, density=True, histtype="step", label="gender repartition for defended thesis")

plt.hist(genders_undefended,bins=10, density=True, histtype="step", label="gender repartition for udefended thesis")
plt.legend()
plt.show()



def pop_to_int(p):
    if p[0]:
        return p[0]
    else:
        return (-1000)

def pops_to_int(l):
    return [pop_to_int(g)  for g in l if g[0]]


name_popularity_thesis = pops_to_int(cur.execute("SELECT (genders.numbers) from author LEFT JOIN genders ON author.firstname=genders.firstname").fetchall())
avg_popularity_thesis=statistics.mean(name_popularity_thesis)

name_popularity_undefended = pops_to_int(cur.execute("SELECT (genders.numbers) from undefended LEFT JOIN genders ON undefended.firstname=genders.firstname").fetchall())
avg_popularity_undefended=statistics.mean(name_popularity_undefended)

print(name_popularity_undefended)

# print(cur.execute("SELECT (undefended.firstname) from undefended LEFT JOIN genders ON undefended.firstname=genders.firstname").fetchall())


plt.suptitle("Density function for name popularity in Computer Science")
plt.title(f"Average popularity of {avg_popularity_thesis} for defended thesis, and of {avg_popularity_undefended} for undefended", size="small")

plt.hist(name_popularity_thesis,bins=10, density=True, histtype="step", label="name popularity for defended thesis")

plt.hist(name_popularity_undefended,bins=10, density=True, histtype="step", label="name popularity for udefended thesis")

plt.legend()
plt.tight_layout()
plt.show()
