# **Article Recommendation System**
## Overview:
This project aims to develop a personalized article recommendation system tailored for biomedical researchers and professionals. The system will leverage the **Entrez API** and **BioC API** to retrieve article metadata and abstracts from PubMed and PMC, enabling users to discover relevant literature efficiently. Using advanced natural language processing (NLP) techniques and similarity-based matching, the system recommends articles based on content relevance. The user-friendly Streamlit interface allows for dynamic filtering, keyword search, and article exploration, while all user and article metadata are stored in a robust Neo4j graph database for efficient authentication and querying.
## Functionalities
1. **Data Source and Retrieval**
The primary data sources are: 
+ *Entrez API*: Fetch metadata (e.g., article titles, abstracts, DOI, publication date) from PubMed and PMC using keyword-based or structured queries. 
+ *BioC API*: Retrieve full-text data for deeper analysis from PMC articles.  
2. **Data Storage and Handling**
The system employs a Neo4j graph database to efficiently store and manage user interactions, article metadata, and relationships. 
+ *Nodes*: Users (with properties like username and password). Articles (storing metadata such as title, abstract). 
+ *Relationships*: Semantic links between similar articles (SIMILAR_TO) based on cosine similarity. 
+ *Preprocessing*: spaCy for cleaning and tokenizing text data (e.g., abstracts).
+ *Embeddings*: Compute contextual BERT embeddings of article abstracts for similarity calculations. 
3. **Interface**
The front end will be a sleek, intuitive Streamlit application that allows users to:
+ *Register and Log In*: User credentials stored securely in Neo4j.
+ *Filter and Search*: Keyword-based article search and filtering by publication year.
+ *Recommendation Dashboard*: Dynamic display of recommended articles based on user preference.
4. **Statistical Analysis**
The system uses statistical methods to drive recommendations: 
+ *Cosine Similarity*: Measure similarity between article abstracts using their BERT contextual embeddings.
5. **Visualizations**
Interactive visualizations using Matplotlib and Plotly enhance user engagement:
+ *Article Categories*: Bar charts showing the availability of articles based on the search.
+ *Neo4j Graph Visualizations*: Showcase relationships between articles using graph-based tools.
## Tools and Libraries
1. APIs:
+ Entrez API: Fetch metadata and abstracts from PubMed.
+ BioC API: Access full-text articles from PMC.
2. Databases:
+ Neo4j: Store articles, categories, and their relationships. 
3. NLP and Similarity:
+ spaCy/NLTK: Preprocess text data (e.g., abstracts).
+ Scikit-learn: Vectorize abstracts using TF-IDF and compute cosine similarity.
4. Web Development:
+ Streamlit: Build an interactive and intuitive user interface.
5. Visualization:
+ Matplotlib: Create engaging visualizations for article availability.
## Group Details
