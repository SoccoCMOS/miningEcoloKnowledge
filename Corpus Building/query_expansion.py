# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 15:23:46 2019

@author: simoussi
"""

from pygbif import species
import pandas as pd
import numpy as np
import requests

ranks=np.array(["KINGDOM","PHYLUM","CLASS","ORDER","FAMILY","GENUS","SPECIES","SUBSPECIES"])

###### Matching names to taxonomy ####
def search_taxa(q):
    res=pd.DataFrame.from_dict(species.name_suggest(q))
    return res


def get_taxonomy(name):
    res=species.name_backbone(name)
    return res


def parse_name(name):
    res=species.name_parser(name)[0]
    return res


###### Get list of parents ####
def get_tax_path(q,include_target=False):
    n=parse_name(q)['scientificName'].capitalize()
    tax=get_taxonomy(n)
    
    r=tax['rank']
    rn=np.where(ranks==r)[0][0]
    
    if include_target:
        rn+=1
    
    asc=dict()
    for i in range(rn):
        l=ranks[i].lower()
        asc.update({l:(tax[l+'Key'],tax[l])})
    
    return asc

def get_subgroup(key,include_target=False):
    res=pd.DataFrame.from_dict(species.name_usage(key=key,data='children')['results'])
    
    return set(res['key'])

def get_supergroup(key,include_target=False):
    res=pd.DataFrame.from_dict(species.name_usage(key=key,data='parents'))
    
    return set(res['key'])

###### Navigating across name usages ####
def get_common_name(key=None,langs='eng',usage='vernacularName'):
    res=pd.DataFrame.from_dict(species.name_usage(key=key,data=usage)['results'])
    if langs!='all':
        res=res.query('language in @langs')
    
    return set(res[usage])

def get_name(key=None):
    name=species.name_usage(key=key)['scientificName']
    return name


###### Querying wikispecies API ####
from mediawiki import MediaWiki

wikisource=MediaWiki(url='https://wikispecies.org/w/api.php')
wikisource.user_agent='sara.simoussi@gmail.com'


def get_wikispecies_data(name="bacteria",nbq=1):
    titles=list(set(wikisource.search(name,results=nbq)))
    results=[]
    for t in titles:
        p=wikisource.page(t)
        info=dict(title=p.title,url=p.url)
        red=[x for x in p.redirects if x not in titles]
        titles.extend(red)
        
        results.append(info)
    
    return results
        
 
###### Querying iNaturalist ####
inat_endpoint="https://api.inaturalist.org/v1/search?"
def query_inaturalist(q):
    r=requests.get(inat_endpoint+"q="+q+"&sources=taxa")
    if r.status_code==200:
        data=r.json()
        
    output=dict()
    if data['total_results']>0:
        results=data['results'][0]['record']   ###Use highest scoring result
        for x in ['name','preferred_common_name','rank','wikipedia_url']:
            output.update({x:results[x]})
        
    else:
        results=None
    
    return output


#### Dictionary entry #####
endpoint="https://od-api.oxforddictionaries.com/api/v2"
app_id = "6f7a92e5"
app_key = "1a37250a2aa39ee277041035778fe77f"
language = "en-gb"

od_headers={"app_id": app_id, "app_key": app_key}

def get_dict_entry(word_id):
    url = "https://od-api.oxforddictionaries.com:443/api/v2/entries/" + language + "/" + word_id.lower()
    r = requests.get(url, headers=od_headers) 
    if r.status_code==200:
        res=r.json()['results']
        
    return res

#### Synonyms API ###
##Twinword
twinword_url = "https://twinword-word-graph-dictionary.p.rapidapi.com/association/"
tw_headers = {
    'x-rapidapi-host': "twinword-word-graph-dictionary.p.rapidapi.com",
    'x-rapidapi-key': "4b214f1a8dmsh6dc278560127cf3p19cc77jsn6578924ce8bd"
    }

def get_synonyms_twinword(w):
    querystring = {"entry":w}
    response = requests.request("GET", twinword_url, headers=tw_headers, params=querystring)
    if response.status_code==200:
        res=response.json()['assoc_word_ex']
    else:
        res=[]
        
    return res

##WordsAPI
wordapi_url = "https://wordsapiv1.p.rapidapi.com/words/"
wa_headers = {
    'x-rapidapi-host': "wordsapiv1.p.rapidapi.com",
    'x-rapidapi-key': "edc0265f5emsh7214b262b9a5476p1ddaa6jsne4d261fb39d3"
    }

def get_synonyms_wordapi(w,mode="synonyms"):
    queryurl=wordapi_url+w+"/"+mode
    response = requests.request("GET", queryurl, headers=wa_headers)
    if response.status_code==200:
        res=response.json()mode]
    else:
        res=[]
        
    return res

   
