#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import csv


        
def load_cnu(f):
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
            surname=row[5].lower()
            firstname=row[7].lower()
            year=2023
            college=row[11]
            section=27
            fullname=firstname + " " + surname
            data.append( (gender,firstname + " " + surname,firstname,year,college,section))

 
    f_cnu = len([p for p in data if p[0] == 'F'])
    h_cnu = len([p for p in data if p[0] == 'H'])

    f_cnua = len([p for p in data if p[0] == 'F' and p[4]=='A'])
    h_cnua = len([p for p in data if p[0] == 'H' and p[4]=='A'])


    f_cnub = len([p for p in data if p[0] == 'F' and p[4]=='B'])
    h_cnub = len([p for p in data if p[0] == 'H' and p[4]=='B'])
    
    
    print(f"We had a total of {f_cnu} female voters, {h_cnu} male voters, so {f_cnu/(f_cnu+h_cnu):.1%} female")
    print(f"College A: {f_cnua} female voters, {h_cnua} male voters, so {f_cnua/(f_cnua+h_cnua):.1%} female")
    print(f"College B: {f_cnub} female voters, {h_cnub} male voters, so {f_cnub/(f_cnub+h_cnub):.1%} female")

print("2023 elections for cnu 27")    
load_cnu('cnu_27_2023.csv')     

print("")
print("2019 elections for cnu 27")    
load_cnu('cnu_27_2019.csv')     
