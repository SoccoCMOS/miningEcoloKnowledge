# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 15:23:46 2019

@author: simoussi
"""

'''
Dependencies: pygbif, pymediawiki, python-datamuse, wordnik-py3

'''
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

###### Get list of immediate descendents ####
def get_subgroup(key,include_target=False):
    res=pd.DataFrame.from_dict(species.name_usage(key=key,data='children')['results'])
    
    return set(res['key'])

###### Get list of all parents ####
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


#### Oxford dictionary entry #####
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

#### Synonyms API ####
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
        res=response.json()
        if res['result_code']=='200':
            out=res['assoc_word_ex']
        else:
            out=[]
    else:
        out=[]
        
    return out

##WordsAPI
wordapi_url = "https://wordsapiv1.p.rapidapi.com/words/"
wa_headers = {
    'x-rapidapi-host': "wordsapiv1.p.rapidapi.com",
    'x-rapidapi-key': "edc0265f5emsh7214b262b9a5476p1ddaa6jsne4d261fb39d3"
    }

'''
Possible modes: 
    definitions
    synonyms
    antonyms
    examples
    typeOf
    hasTypes
    partOf
    hasParts
    instanceOf
    hasInstances
    memberOf
    hasMembers
    substanceOf
    hasSubstances
    hasAttribute
    inCategory
    hasCategories
    also
    entails
    pertainsTo
    similarTo
'''

def get_synonyms_wordapi(w,mode="synonyms"):
    queryurl=wordapi_url+w+"/"+mode
    response = requests.request("GET", queryurl, headers=wa_headers)
    if response.status_code==200:
        res=response.json()[mode]
    else:
        res=[]
        
    return res


##Datamuse API
from datamuse import datamuse
def suggest_word_datamuse(w,topics,max_res=100):
    datamuseapi = datamuse.Datamuse()  
    results=[]
    mean=pd.DataFrame.from_dict(datamuseapi.words(ml=w,topics=topics,max=max_res))
    mean['tag']='means'
    results.append(mean)
    syn=pd.DataFrame.from_dict(datamuseapi.words(rel_syn=w,topics=topics,max=max_res))
    syn['tag']='synonym'
    results.append(syn)
    typ=pd.DataFrame.from_dict(datamuseapi.words(rel_spc=w,topics=topics,max=max_res))
    typ['tag']='type'
    results.append(typ)
    exm=pd.DataFrame.from_dict(datamuseapi.words(rel_gen=w,topics=topics,max=max_res))
    exm['tag']='exampleOf'
    results.append(exm)
    comp=pd.DataFrame.from_dict(datamuseapi.words(rel_com=w,topics=topics,max=max_res))
    comp['tag']='hasComponent'
    results.append(comp)
    partof=pd.DataFrame.from_dict(datamuseapi.words(rel_par=w,topics=topics,max=max_res))
    partof['tag']='partOf'
    results.append(partof)
    
    output=pd.concat(results,ignore_index=True,sort=True)
    
    return output

##Wordnik API
from wordnik import swagger , WordApi
wordnik_key='71ov2rh3r2p6gpfr1aa7psv49iq90dkyzcb8gale1aduciaxd'
wordnik_url='http://api.wordnik.com/v4'

'''
Output contains following keys: 
    'cross-reference', 'has_topic', 'hypernym', 'rhyme', 'same-context', 'synonym', 'variant', 'verb-form'
'''

def related_wordnik(w,canonicform=True):
    client = swagger.ApiClient(wordnik_key, wordnik_url)
    wordApi = WordApi.WordApi(client)
    res=wordApi.getRelatedWords(w,useCanonical=canonicform)#,relationshipTypes=types,limitPerRelationshipType=limit)
    output=dict()
    if res!='null getRelatedWords result':
        for related in res:
            output.update({related.relationshipType:related.words})
            
    return output
    

    
