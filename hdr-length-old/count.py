# HDR file extracted from 
# https://api.archives-ouvertes.fr/search/?q=*:*&fq=docType_s:HDR&fq=domain_t:info&fl=defenseDateY_i&fl=files_s&fl=authLastName_s&fl=authFirstName_s&rows=2500


# importing PyPDF2 library

import PyPDF2

import requests
from io import BytesIO
import json
import csv
import statistics 



# some invalid urls failing
invalid_urls = ['https://hal-lirmm.ccsd.cnrs.fr/tel-03985799/file/M%C3%A9moire%20de%20Synth%C3%A8se%20de%20Recherche.pdf']

def get_pages(url):
  if not url in invalid_urls:
      print("start download of "+url)
      file = BytesIO(requests.get(url).content)
      print("finished download of "+url)  
      # opened file as reading (r) in binary (b) mode
      # file = open('https://theses.hal.science/tel-00321615/file/Nguyen.Gia-Toan_1986_these.pdf',            'rb')
      # store data in pdfReader
      pdfReader = PyPDF2.PdfReader(file)
      # count number of pages
      totalPages = len(pdfReader.pages)
      # print number of pages
      return(totalPages)


with open('api.archives-ouvertes.fr.json', 'r') as file:
    data = json.load(file)



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
          # if name is less common, we ignore and skip
          if number<numbers[name]:
              continue
          
      # we initialize values for a new name    
      if g=='1':
         names[name]="H"
         numbers[name]=number
      elif g=='2':
         names[name]="F"
         numbers[name]=number         

# print(names)
    
def get_gender(name):
    """Prend chaque prénom individuellement sans prendre en compte le nom de famille"""
    # Convertir le nom en minuscules
    name_lower = name.lower()

    # Diviser le nom en parties en utilisant l'espace comme séparateur
    name_parts = name.split()

    for part_name in [part.lower() for part in name_parts[0:]]:
        if part_name in names:
            return names[part_name]

        
    return None


# A dictionnary, indexed by full name. for each key,  contains a sub list "Gender"  
results = {}

# this is stored in a csv: full name; gender; anne; url

with open('results.csv', 'r', encoding='utf-8', newline='') as result_file:
    result_reader = csv.reader(result_file, delimiter=';')
    for row in result_reader:
        results[row[0]] = {"gender":row[1], "year":row[2], "url":row[3], "pages":row[4]}

H_pages = []
F_pages = []



for result in results:
    result=results[result]
    if result["gender"] == "H":
        H_pages += [int(result["pages"])]

    if result["gender"] == "F":
        F_pages += [int(result["pages"])]

counter_H = len(H_pages)
counter_H_pages = sum(H_pages)
median_H = statistics.median(H_pages)
dev_H = statistics.pstdev(H_pages)

counter_F = len(F_pages)
counter_F_pages = sum(F_pages)
median_F = statistics.median(F_pages)
dev_F = statistics.pstdev(F_pages)

print("Counter H :"+str(counter_H)+" Counter H pages :"+str(counter_H_pages))
print("Counter F :"+str(counter_F)+" Counter F pages :"+str(counter_F_pages) )
print("Moyenne H :" + str(counter_H_pages/counter_H))
print("Moyenne F :" + str(counter_F_pages/counter_F))
print("Medianne H :" + str(median_H))
print("Medianne F :" + str(median_F))
print("Dev H :" + str(dev_H))
print("Dev F :" + str(dev_F))



from scipy import stats
print(stats.ttest_ind(H_pages, F_pages))
print(stats.ks_2samp(H_pages, F_pages))


import matplotlib.pyplot as plt
import numpy as np

plt.hist(H_pages,bins=50,density=True,histtype="step")
plt.hist(F_pages,bins=50,density=True,histtype="step")
plt.show()

for entry in data['response']['docs']:
    # we only keep entries with a single file
    # we lose ~
    if 'files_s' in entry and len(entry['files_s'])==1:
        nom=entry['authLastName_s'][0]
        prenom=entry['authFirstName_s'][0]
        url=entry['files_s'][0]
        date=entry['defenseDateY_i']           
        fullname = prenom+" "+nom
        if not fullname in results:
            pages=get_pages(url)
            if pages:
                outfile = open('results.csv', 'a')                   
                outfile.write(';'.join(str(i) for i in [fullname, get_gender(prenom), date, url, pages])+"\n")


                
