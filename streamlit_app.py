import streamlit as st
import pandas as pd
import helper_functions

st.title('Article Recommendation System')
st.info('This app recommends articles based on user search')

with st.sidebar:
    st.write('Select parameters')
    key_word = st.text_input('Enter the search keyword')
    mindate = st.date_input('Enter starting date')
    maxdate = st.date_input('Enter ending date')
    retmode = st.radio('Pick one', ['json', 'xml'])
    retmax = st.selectbox('Select:', [1, 2, 3])
    status = st.button('Proceed')

if status: 
    st.write(key_word)
    st.write(retmax)
    st.write(mindate)

# with st.expander('Data'):
#     st.write('**Raw Data**')
#     df = pd.read_csv('https://raw.githubusercontent.com/GokulPrakashK98/DataScienceProject/refs/heads/test-branch/Sample.csv?token=GHSAT0AAAAAAC2HKVXIPRP4XZE77M3SLGEMZ2MLIRQ')
#     df = df.head()
#     df

