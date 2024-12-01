import streamlit as st
import pandas as pd

st.title('Article Recommendation System')
st.info('This app recommends articles based on user search')

with st.expander('Data'):
    st.write('**Raw Data**')
    df = pd.read_csv('https://raw.githubusercontent.com/GokulPrakashK98/DataScienceProject/refs/heads/test-branch/Sample.csv?token=GHSAT0AAAAAAC2HKVXITY5SHOGYV636SVCAZ2MJ3CQ')
    df
