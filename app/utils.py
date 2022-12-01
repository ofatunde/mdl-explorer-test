import pandas as pd
import streamlit as st
import base64
import requests
#import numpy as np
#from semanticscholar import SemanticScholar
#import re
#from collections import Counter
#import preprocessor as p
#import time

#@st.experimental_memo(suppress_st_warning=True)
def read_data(path):
    return pd.read_csv(path)

def read_data_alt(path):
    return pd.read_csv(path,encoding='cp1252')

@st.cache(allow_output_mutation=True)
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_bg(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = """
        <style>
        .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        }
        </style>
    """ % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)
    
def head():
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: -35px;'>
        MDL Dataset Citation Explorer
        </h1>
    """, unsafe_allow_html=True
    )
    
    st.caption("""
        <p style='text-align: center'>
        by <a href='https://www.jointdatacenter.org/'>JDC</a>
        </p>
    """, unsafe_allow_html=True
    )
    
    st.write(
        "This tool allows you to understand the downstream usage of datasets in the UNHCR microdata library. ",
        "Click the button to select a dataset."
    )

def NLP4Dev(abstract_or_fulltext,text_source):
    if(abstract_or_fulltext == 'PDF'):
        #extract output using "Analyze_file" endpoint
        url = "https://www.nlp4dev.org/nlp/models/mallet/analyze_file"
        payload={"model_id": "6fd8b418cbe4af7a1b3d24debfafa1ee"}
        files=[('file',('mdl-explorer-app/data/02637758211070565.pdf',open('data/02637758211070565.pdf','rb'),'application/pdf'))]
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        resp = eval(response.text)
        topic_distribution = resp.get('doc_topic_words')
        country_distribution = resp.get('country_details')
        tag_distribution = resp.get('jdc_tag_counts')
    elif(abstract_or_fulltext == 'parsed_PDF'):
        #extract output using "Analyze_text" endpoint on full extracted text
        url = "https://www.nlp4dev.org/nlp/models/mallet/analyze_text"
        payload = { "model_id": "6fd8b418cbe4af7a1b3d24debfafa1ee", "text": text_source }
        headers = { 'Content-Type': 'application/x-www-form-urlencoded',}
        response = requests.request("POST", url, headers=headers, data=payload)
        resp = eval(response.text)
        topic_distribution = resp.get('doc_topic_words')
        country_distribution = resp.get('country_details')
        tag_distribution = resp.get('jdc_tag_counts')
    elif(abstract_or_fulltext == 'abstract_only'):
        #extract output using "Analyze_text" endpoint on abstract text
        url = "https://www.nlp4dev.org/nlp/models/mallet/analyze_text"
        payload = { "model_id": "6fd8b418cbe4af7a1b3d24debfafa1ee", "text": text_source }
        headers = { 'Content-Type': 'application/x-www-form-urlencoded',}
        response = requests.request("POST", url, headers=headers, data=payload)
        resp = eval(response.text)
        topic_distribution = pd.DataFrame(resp.get('doc_topic_words'))
        country_distribution = pd.DataFrame(resp.get('country_details'))
        tag_distribution = pd.DataFrame(resp.get('jdc_tag_counts'))
        
        topic_39_percentage = topic_distribution.loc[topic_distribution['topic_id'] == 39,'value'][0]
        #majority_country = country_distribution.loc['name'][0] #change to whichmax
        
        
        if len(country_distribution) > 0:
            df_indexid = country_distribution.set_index('count')
            majority_country = df_indexid.loc[max(country_distribution['count'])]['name']
        else:
            majority_country = 'NONE'
        
        jdc_tag_count = len(tag_distribution)

        
    return(topic_distribution
           ,country_distribution
           ,tag_distribution
           ,topic_39_percentage
           ,majority_country
           ,jdc_tag_count)
    
def calculate_relevance(ref,dataset,paper_title,topic_39_percentage,jdc_tag_count,majority_country,relevance_threshold):

    #dataset_country = ref.loc[ref['id'] == dataset, 'nation']
    df_indexid = ref.set_index('id')
    dataset_country = df_indexid.loc[dataset]['nation']
    dataset_title = df_indexid.loc[dataset]['title']

    if((topic_39_percentage > relevance_threshold) and (majority_country == dataset_country)):
        relevance = 1
    elif((topic_39_percentage > relevance_threshold) and (majority_country != dataset_country)):
        relevance = 0.5
    else:
        relevance = 0
        
    final_output = pd.DataFrame(list(zip([dataset_title],[paper_title],[relevance]
                    ,[topic_39_percentage]
                    ,[jdc_tag_count]))
                               # ,columns = ["dataset_title", "paper_title","relevance","topic_39_percentage", "jdc_tag_count"]
)
    
    return final_output
       
def body(ref,SS_output,text_entry,sample):
    st.write("Dataset name:",sample['dataset_title'][0])
    st.write("This project uses a set of topics defined by [NLP4Dev](https://www.nlp4dev.org/explore/subcategories/filtering-by-topic-share/). Our primary topic of focus is Topic 39, which is characterized by the following keywords: 'refugee, programme, country, migration, migrant, labour, remittance, population'")
    st.write("Relevance codes:")
    st.write(
        "1: At least ten percent of paper content is relevant to Topic 39, and the abstract text indicates a focus on the same country used in the dataset")
    st.write(
        "0.5: At least ten percent of paper content is relevant to Topic 39, but the abstract text focuses on a different country")
    st.write(
        "O: All other scenarios."
    )
    #st.write(ref)
    #st.write(text_entry)
    #st.write("Number of Semantic Scholar results:", len(SS_output))
#     output = pd.DataFrame()
#     #NLP_output = []
#     dataset_number = text_entry
#     # extract SS API list of 16
#     # SS_output = pd.DataFrame() #read in file here
#     for i in range(len(SS_output)):
#         #NLP_output.append(NLP4Dev('abstract_only',SS_output['abstract'][i])) #change to input from API1
#         try:
#             (topic_distribution,country_distribution,tag_distribution,topic_39_percentage,majority_country,jdc_tag_count) = NLP4Dev('abstract_only',SS_output['abstract'][i])   
#             paper = SS_output['title'][i]
#             mini_table = calculate_relevance(ref,dataset_number,paper,topic_39_percentage,jdc_tag_count,majority_country,.10)
#             output = pd.concat([output,mini_table],axis = 0)
#         except:
#             pass
#         #output.append(mini_table)
#     #return output
    st.dataframe(sample.drop(columns = 'dataset_title'))
