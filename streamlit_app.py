import streamlit as st
import pandas as pd
from API_helper_func import *
from Recommend_helper_func import *
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="Article Recommendation System", layout="centered") # "wide"
st.logo(image="icon.png", 
        icon_image="icon.png", size='large') # setting the icon

# Multiple tabs for recommendation & NLP tasks
tab1, tab2 = st.tabs(["Home", "NLP"])
with tab1:
    st.title('Article Recommendation System')
    with st.expander('Info'):
        st.info('''
    This project aims to develop a personalized article recommendation system tailored for biomedical
    researchers and professionals. The system will leverage the Entrez API and BioC API to retrieve
    article metadata and abstracts from PubMed and PMC, enabling users to discover relevant literature
    efficiently. Using advanced natural language processing (NLP) techniques and similarity-based
    matching, the system recommends articles based on content relevance.
    ''')

    # API query parameters
    with st.sidebar:
        st.write('Select parameters')
        key_word = st.text_input('Enter the search keyword')
        mindate = st.date_input('Enter starting date')
        maxdate = st.date_input('Enter ending date')
        retmode = st.radio('Pick one', ['json', 'xml'])
        retmax = st.selectbox('Select:', [10, 20, 50, 100])
        status = st.button('Proceed')

    if "article_df" not in st.session_state:
        st.session_state.article_df = pd.DataFrame()

    if status:
        mindate = str(mindate.strftime("%d/%m/%Y"))
        maxdate = str(maxdate.strftime("%d/%m/%Y"))

        params = {
            'keyword': key_word or 'plant', 
            'mindate': mindate or '01/01/2024', 
            'maxdate': maxdate or '01/12/2024', 
            'retmode': retmode, 
            'retmax': retmax
        }

        if retmode == "json":
            # API calls
            data, article_ids = fetch_article_id(**params)
            article_df = run_script(article_ids)
            # data = api_output(**params)

            # Save the DataFrame to session state
            st.session_state.article_df = article_df
            st.session_state.data = data

        else:
            st.warning("Work in progress for XML format...")

    article_df = st.session_state.article_df

    # Visualizing Data Expander
    with st.expander("Data"):
        if not article_df.empty:
            st.dataframe(article_df)
        else:
            st.warning("No data available. Please search to load data.")

    # Information about total hits and data retrieved
    with st.expander('Visualisation'):
        col1, col2 = st.columns(2)
        try:
            if 'data' in st.session_state and st.session_state['data']:
                data = st.session_state['data'] 
                total_results = int(data['esearchresult']['count'])
                returned_results = int(data['esearchresult']['retmax'])

                # API Metrics
                with col2:
                    st.metric(label="Total Results", value=total_results)
                    st.metric(label="Returned Results", value=returned_results)

                # Bar graph
                with col1:
                    st.subheader("Total vs Returned Results")
                    fig, ax = plt.subplots(figsize=(4, 5))
                    ax.bar(["Total Results", "Returned Results"], [total_results, returned_results], color=["blue", "orange"])
                    ax.set_ylabel("Count")
                    ax.set_title("Total vs Returned Results")
                    st.pyplot(fig)

        except Exception as e:
            st.error(f"Error generating visualization: {e}")

    # Initializing the button 'look'
    if "look" not in st.session_state:
        st.session_state.look = False

    # Abstract Viewer Expander
    with st.expander("Section"):
        section = st.selectbox(
        "Pick a section:", ['Abstract', 'Introduction', 'Methods', 'Results', 'Discussion'], 
        index=0,
        key="section_selectbox")

        if not article_df.empty:
            # Use session state to retain the slider value
            if "slider_val" not in st.session_state:
                st.session_state.slider_val = 1 

            # Slider for selecting an abstract
            val = st.slider(
                "Select Article Index", 
                min_value=1, 
                max_value=min(retmax, len(article_df)), 
                value=st.session_state.slider_val, 
                key="slider_val",
                step=1
            )

            # Fetch the selected article details
            if "selected_article" not in st.session_state:
                st.session_state.selected_article = None

            selected_article = article_df.iloc[val - 1]
            st.write(f"**Title:** {selected_article['Title']}")
            st.write(f"**PMCID:** {selected_article['pmcid']}")
            st.text_area(f"**{section}:**", selected_article[section], height=300)
            
            if st.button('Look for similar articles', key=f'similar_articles_{val}'):
                st.session_state.look = True
                st.session_state.selected_article = selected_article

        else:
            st.warning("No articles to display abstracts.")

    # Recommend articles based on cosine similarity
    if st.session_state.look:
        with st.expander("Recommended articles"):
            st.write('Looking for similar articles...')
            article = st.session_state.selected_article
            article = article['Abstract']
            all_abstracts = article_df['Abstract'].to_list()

            # Vectorization and cosine similarity
            similarity = get_similar_articles(article, all_abstracts, method='bert')
            recommend = get_recommendation(similarity, article_df)

            # Recommend articles in different tabs
            rec1, rec2, rec3, rec4, rec5 = st.tabs(['Article 1', 'Article 2', 'Article 3', 'Article 4', 'Article 5'])
            # Adding keys to session state
            if 'keys' not in st.session_state:
                st.session_state.keys = None
            keys = list(recommend.keys())
            st.session_state.keys = keys
            section = st.selectbox(
                    "Pick a section:", ['Abstract', 'Introduction', 'Methods', 'Results', 'Discussion'], 
                    index=0,
                    key="recommendation_section_selectbox")
            
            ################# Recommended Article tabs ###############
            # Article 1
            df = article_df[article_df['pmcid']==keys[1]]
            rec1.write(recommend[keys[1]])
            rec1.text_area(f"**{section}:**", df[section].iloc[0], height=250)

            # Article 2
            df = article_df[article_df['pmcid']==keys[2]]
            rec2.write(recommend[keys[2]])
            rec2.text_area(f"**{section}:**", df[section].iloc[0], height=250)

            # Article 3
            df = article_df[article_df['pmcid']==keys[3]]
            rec3.write(recommend[keys[3]])
            rec3.text_area(f"**{section}:**", df[section].iloc[0], height=250)

            # Article 3
            df = article_df[article_df['pmcid']==keys[4]]
            rec4.write(recommend[keys[4]])
            rec4.text_area(f"**{section}:**", df[section].iloc[0], height=250)

            # Article 3
            df = article_df[article_df['pmcid']==keys[5]]
            rec5.write(recommend[keys[5]])
            rec5.text_area(f"**{section}:**", df[section].iloc[0], height=250)

with tab2:
    st.title("NLP tasks")
    with st.expander('Info'):
        st.info("""
        This is a workspace to perform various basic NLP tasks. The following tasks can be performed using **spaCy base models**:
        
        - **Tokenization**: Breaks a text into smaller units such as words or sentences.
        - **Named Entity Recognition (NER)**: Identifies and classifies entities (e.g., names, dates, locations) in the text.
        - **Part-of-Speech (POS) Tagging**: Assigns grammatical labels (e.g., noun, verb) to words in a text.
        - **Dependency Parsing**: Analyzes the grammatical structure of a sentence by identifying relationships between words.
        - **Sentence Boundary Detection (SBD)**: Automatically detects sentence boundaries in a given text.
        - **Lemmatization**: Converts words to their base or dictionary form (e.g., "running" → "run").
        
        These tasks leverage the power of spaCy’s efficient and pretrained pipelines, which are optimized for multiple languages.

        Explore these tasks and more using spaCy and other NLP tools!
        """)