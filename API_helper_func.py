from requests.exceptions import RequestException
import pandas as pd
import requests
import numpy as np
import json
from Bio import Entrez

# Fetch article ids based on keywords
def fetch_article_id(keyword, mindate, maxdate, db='pmc', retmax=20, retmode='json'):
    """
    Fetch article IDs from the PubMed Central (PMC) database based on a keyword search.
    Parameters:
        keyword (str): The search term for finding relevant articles.
        mindate (str): The minimum publication date (YYYY/MM/DD format).
        maxdate (str): The maximum publication date (YYYY/MM/DD format).
        db (str): The database to search (default is 'pmc').
        retmax (int): Maximum number of article IDs to return (default is 20).
        retmode (str): The format of the returned data (default is 'json').
    Returns:
        tuple: A tuple containing the raw response data and a list of article IDs.
    """  
    Entrez.email = "rameshsreelakshmi214@gmail.com"
    Entrez.api_key = "6a7330828c7e43fa66ecd8c1167f36433c08"
    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {
        'db': db,
        'term': keyword,
        'retmax': retmax,
        'retmode': retmode,
        'mindate': mindate,
        'maxdate': maxdate
    }

    response =requests.get(esearch_url, params=params)
    if response.status_code == 200:
        data = response.json()
        article_ids = data['esearchresult']['idlist']
    return data, article_ids


# Fetch meta data of the collected articles
def fetch_data(id):
    """
    Fetch data of an full text article using its PMC ID.
    Parameters:
        id (str): The PMC ID of the article.
    Returns:
        dict or None: The metadata in JSON format, or None if an error occurs.
    """
    format = 'json'
    encode = 'unicode'
    url = f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_{format}/PMC{id}/{encode}'
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() 
        try:
            json_data = response.json()
            return json_data
        except ValueError as e:
            print(f"JSON parsing error: {e}")
            return None
    except RequestException as e:
        print(f"Request failed: {e}")
        return None

# Parse the article info 
def parse_article_info(json_data):
    """
    Extracts relevant article information from the JSON response.
    Parameters:
        json_data (dict): The JSON data containing article details.
    Returns:
        dict: A dictionary with extracted article details such as title, abstract, 
        introduction, methods, results, and discussion.
    """
    article_info = {}
    intro_lst = []
    results_lst = []
    discussion_lst = []
    abstract_lst = []
    methods_lst = []
    title = ''

    # Iterate over documents and passages 
    for documents in json_data[0].get('documents', []):
        for passage in documents.get('passages', []):
            infons = passage.get('infons', {})
            if 'article-id_doi' in infons or 'article-id_pmc' in infons or 'article-id_pmid' in infons:
                doi = infons.get('article-id_doi', None)
                pmcid = infons.get('article-id_pmc', None)
                pmid = infons.get('article-id_pmid', None)

            # Get the section type (eg. 'Introduction')
            section_type = infons.get('section_type', '').lower()
            passage_type = infons.get('type', '').lower()

            # Parsing title & abstracts
            if section_type == 'title':
                title = passage.get('text', '')
            elif section_type == 'abstract' and passage_type == 'abstract':
                abstract = passage.get('text', '')
                abstract_lst.append(abstract)

            # Parsing other sections
            elif section_type == 'intro' and passage_type == 'paragraph':
                intro = passage.get('text', '')
                intro_lst.append(intro)

            elif section_type == 'methods' and passage_type == 'paragraph':
                methods = passage.get('text', '')
                methods_lst.append(methods)

            elif section_type == 'discuss' and passage_type == 'paragraph':
                discuss = passage.get('text', '')
                discussion_lst.append(discuss)

            elif section_type == 'results' and passage_type == 'paragraph':
                results = passage.get('text', '')
                results_lst.append(results)

    abstract = ' '.join(abstract_lst)
    introduction = ' '.join(intro_lst)
    methods = ' '.join(methods_lst)
    discussion = ' '.join(discussion_lst)
    results = ' '.join(results_lst)

    if pmcid:
        article_info[pmcid] = {'PMID': pmid,
                            'Title': title,
                            'Abstract': abstract,
                            'Introduction': introduction,
                            'Methods': methods,
                            'Results': results,
                            'Discussion': discussion,
                            'DOI': doi}
        
    return article_info


# Clean and store the article info in a dataframe
def run_script(ids):
    """
    Fetches and processes metadata for a list of PMC article IDs.
    Parameters:
        ids (list): A list of PMC article IDs.
    Returns:
        pandas.DataFrame: A DataFrame containing processed article information.
    """
    info = {}
    for id in ids:
        try: 
            data = fetch_data(id)
            if data:
                article_data = parse_article_info(data)
                info.update(article_data)
        except Exception as e:
            print(f'Error: {e}')

    df_article = pd.DataFrame.from_dict(info, orient='index')
    df_article.reset_index(inplace=True)
    df_article.rename(columns={'index': 'pmcid'}, inplace=True)
    df_article['pmcid'] = df_article['pmcid'].apply(lambda x: 'PMC' + str(x) if not str(x).startswith('PMC') else x)
    df_article.dropna(subset=['Title', 'Abstract', 'Introduction'], inplace=True)
    return df_article