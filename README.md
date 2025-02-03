# **Article Recommendation System**
## Overview:
This project aims to develop a personalized article recommendation system tailored for biomedical researchers and professionals. The system will leverage the **Entrez API** and **BioC API** to retrieve article metadata and abstracts from PubMed and PMC, enabling users to discover relevant literature efficiently. Using advanced natural language processing (NLP) techniques and similarity-based matching, the system recommends articles based on content relevance. The user-friendly Streamlit interface allows for dynamic filtering, keyword search, and article exploration, while all user and article metadata are stored in a robust Neo4j graph database for efficient authentication and querying. 
1. **Data Source and Retrieval**
The primary data sources are: 
+ Entrez API: Fetch metadata (e.g., article titles, abstracts, DOI, publication date) from PubMed and PMC using keyword-based or structured queries. 
+ BioC API: Retrieve full-text data for deeper analysis from PMC articles.  
2. **Data Storage and Handling**
The system employs a Neo4j graph database to efficiently store and manage user interactions, article metadata, and relationships. 
+ Nodes: Users (with properties like username and password). Articles (storing metadata such as title, abstract). 
+ Relationships: Semantic links between similar articles (SIMILAR_TO) based on cosine similarity. 
+ Preprocessing: spaCy for cleaning and tokenizing text data (e.g., abstracts).
+ Embeddings: Compute contextual BERT embeddings of article abstracts for similarity calculations. 
