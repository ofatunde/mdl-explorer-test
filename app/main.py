import streamlit as st
from utils import set_bg,read_data, read_data_alt, head, body, NLP4Dev, calculate_relevance


st.set_page_config(
    page_title='MDL Dataset Explorer',
    page_icon='assets/icon.png'
)

#set_bg('assets/official_background.png')
set_bg('assets/black.png')

head()

dataset_id = st.text_input("Enter the dataset number", "")
# st.text_input(label = "Enter the dataset number"
#                            , value=""
#                            , max_chars=None
#                            , key=None
#                            , type="default"
#                            , help="Type an integer value (e.g., 123)"
#                            , autocomplete=None
#                            , on_change=None
#                            , args=None
#                            , kwargs=None
#                            ,
#                            *
#                            , placeholder=None
#                            , disabled=False
#                            , label_visibility="visible") #change to dropdown
if dataset_id:
    abstract_or_fulltext = 'abstract_only'
    reference_data = read_data_alt('data/overview_all_datasets_2022_categorized.csv')
    SS_output = read_data('data/streamlitdemo.csv') #specific to 189. Need to generalize, Also, need to move inside body function
    sample = read_data('data/sample_results.csv')
    body(reference_data,SS_output,dataset_id,sample)
    
