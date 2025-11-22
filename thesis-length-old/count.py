# thesis file extracted from 
# https://api.archives-ouvertes.fr/search/?q=*:*&fq=docType_s:THESE&fq=domain_t:info&fq=submittedDateY_i:[2015%20TO%202020]&fl=defenseDateY_i&fl=files_s&fl=authLastName_s&fl=authFirstName_s&fl=primaryDomain_s&rows=20000
# https://api.archives-ouvertes.fr/search/?q=*:*&fq=docType_s:THESE&fq=domain_t:info&fq=submittedDateY_i:[2021%20TO%20*]&fl=defenseDateY_i&fl=files_s&fl=authLastName_s&fl=authFirstName_s&fl=primaryDomain_s&rows=20000

# importing PyPDF2 library

import PyPDF2

import requests
from io import BytesIO
import json
import csv
import statistics 


# some invalid urls failing
invalid_urls = ['https://theses.hal.science/tel-02117886/file/Drieu_la_Rochelle_Armand_2018_ED414.pdf',
                'https://hal.science/tel-04471768/file/These_Nadir_Cherifi%20%281%29.pdf',
                'https://ubs.hal.science/tel-05025573/file/2012theseDuarteK.pdf',
                'https://hal.science/tel-04861440/file/Doctorat%20John%20Kingston%20%281%29.jpg',
                'https://theses.hal.science/tel-04709062/file/122987_GARNIER_2024_archivage.pdf',
                'https://theses.hal.science/tel-05033245/file/TH2024GIAMPICCOLOCAMILLE.pdf',
                'https://ubs.hal.science/tel-03105715/file/MushtaqM_these_remaniee.pdf',
                'https://hal.science/tel-04935803/file/GARCIA_MARTINEZ.pdf',
'https://enac.hal.science/tel-02453297/file/171115_VOUNDY_125qrkfd43qpml681ycyunl870whiuxh_TH.pdf',
'https://normandie-univ.hal.science/tel-02552250/file/ManuscritSamuelBovee.pdf',
'https://univ-pau.hal.science/tel-02437314/file/Final%20Thesis.pdf',
'https://univ-pau.hal.science/tel-02437294/file/AbdelTh%C3%A9se.pdf',
'https://hal.inrae.fr/tel-02841288/file/MLTAUPIN_1.pdf',
'https://hal.sorbonne-universite.fr/tel-02641309/file/these_katz.pdf',
'https://hal-lirmm.ccsd.cnrs.fr/tel-02418022/file/tese_tex_Jan16-02.pdf',
'https://univ-pau.hal.science/tel-02437337/file/Le%20memoire%20-%20latex.pdf',
'https://univ-pau.hal.science/tel-02437332/file/Final%20Thesis.pdf',
'https://univ-pau.hal.science/tel-02437303/file/th%C3%A8se%2001-02-2018.pdf',
'https://univ-pau.hal.science/tel-02437343/file/these_MK-final.pdf',
'https://theses.hal.science/tel-04731754/file/241007_ManuscritThese_CBolut_vfinale.pdf',
'https://theses.hal.science/tel-04521335/file/127283_ATHEUPE_GATCHEU_2023_archivage.pdf',
'https://hal.science/tel-05293793/file/thesis_Hohnadel.pdf',
'https://hal-lirmm.ccsd.cnrs.fr/tel-04301030/file/8.%20Tese%20Final_DSC_Heraldo.pdf',                
                'https://institut-agro-dijon.hal.science/tel-04186641/file/THESE1993%20MH%20GRAS%20micriobiologie%20salades.pdf',
                'https://hal.inrae.fr/tel-02787502/file/These_ECREPONT_Stephane2019_1']

def get_pages(url):
  if not url in invalid_urls:
    try:
      print("'" + url+"',")
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
       return None

with open('api.archives-ouvertes.fr_2015_2020.json', 'r') as file:
    data1 = json.load(file)

with open('api.archives-ouvertes.fr_2020_2025.json', 'r') as file:
    data2 = json.load(file)
    

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

import matplotlib.pyplot as plt
import numpy as np

        
def print_res_full(cond):

  H_pages = []
  F_pages = []
  None_pages = []

  
  for result in results:
    result=results[result]
    if result["gender"] == "H" and cond(result) :
        H_pages += [int(result["pages"])]
    elif result["gender"] == "F"  and cond(result):
        F_pages += [int(result["pages"])]
    else:
        None_pages += [int(result["pages"])]

  if H_pages==[] or F_pages==[]:
    return None
  
  counter_H = len(H_pages)
  counter_H_pages = sum(H_pages)
  
  counter_F = len(F_pages)
  counter_F_pages = sum(F_pages)

  
  
  median_H =  statistics.median(H_pages)
  median_F = statistics.median(F_pages)
  dev_H = statistics.pstdev(H_pages)
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

  return(H_pages, F_pages)
        



count=0
domains = set()

print("Checking entries: "+str(len(data1['response']['docs']+data2['response']['docs'])))
for entry in data1['response']['docs']+data2['response']['docs']:
    # we only keep entries with a single file
    # we lose ~
    if 'files_s' in entry and len(entry['files_s'])==1:
        nom=entry['authLastName_s'][0]
        prenom=entry['authFirstName_s'][0]
        url=entry['files_s'][0]
        date=entry['defenseDateY_i']           
        fullname = prenom+" "+nom
        domain = entry['primaryDomain_s']
        domains.add(domain)
        if not fullname in results:
            pages=None # get_pages(url)
            if pages:
                outfile = open('results.csv', 'a')                   
                outfile.write(';'.join(str(i) for i in [fullname, get_gender(prenom), date, url, pages])+"\n")
            else:
              count +=1
        else:
         # domain was added a posteriori, so we hack it into the results by hand
         results[fullname]['domain'] = domain                           
    else:
      count +=1

print("Ignored invalid entries: " + str(count))

None_pages = []

  
for result in results:
  result=results[result]
  if result["gender"] == "None": 
        None_pages += [int(result["pages"])]


print("Unknown gender (mostly due to non French surnameS) :"+str(len(None_pages)))


print(" Stats for all thesis that contain the domain info")
print("")
print("Stats for 2015 - 2019")
print_res_full( (lambda x : int(x['year']) < 2020))
print(" ")
print("Stats for 2020 - 2025")
print_res_full( (lambda x :  2020 <= int(x['year'])))
print(" ")
print("Stats for 2015 - 2025")
print_res_full( (lambda x : True))





print("")
print("Stats for all thesis that have info as primary domain info")
print("")

info_domains = [d for d in domains if "info." in d]

H,F = print_res_full( (lambda x : 'domain' in x and x['domain'] in info_domains))


plt.hist(H,bins=50,density=True,histtype="step")
plt.hist(F,bins=50,density=True,histtype="step")  

plt.show()


# prim_domains = set([d.split(".")[0] for d in domains])
# print(prim_domains)

# for d in prim_domains:
#   print("")
#   print("Stats for all thesis that have info as primary domain "+d)
#   print("")
  
#   print_res_full( (lambda x : 'domain' in x and x['domain'].split(".")[0]==d))

  


# print("")
# print("by domain")
# print("")

# for d in info_domains:
#   print("Stats for domain "+d)





