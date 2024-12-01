import streamlit as st
import pandas as pd

st.title('Article Recommendation System')
st.info('This app recommends articles based on user search')

with st.expander('Data'):
    df = pd.read_csv('Sample.csv')
    df.head()
