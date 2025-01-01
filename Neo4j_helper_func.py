from neo4j import GraphDatabase
import bcrypt
import streamlit as st

class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)
    
    def close(self):
        if self.__driver:
            self.__driver.close()
    
    def query(self, query, parameters=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session:
                session.close()
        return response
    
########### User Authentication #############
def register_user(conn, first, last, username, password):
    """Register a new user in Neo4j."""
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        conn.query("""
        CREATE CONSTRAINT user_unique_username IF NOT EXISTS
        FOR (u:User) REQUIRE u.username IS UNIQUE;
        """)
    except Exception as e:
        print("Constraint setup failed:", e)

    query = """
    CREATE (u:User {first_name:$first, last_name: $last, username: $username, password: $password})
    """
    conn.query(query, parameters={"username": username, "password": hashed_pw, 'first': first, 'last': last})
    return True

# def fetch_all(conn):
#     query = "MATCH (n) RETURN n"
#     result = conn.query(query)
    
#     name_lst = []
#     user_lst = []
#     passwd_lst = []
#     for node in result:
#         passwd_lst.append(node[0]["password"])
#         user_lst.append(node[0]['username'])
#         name_lst.append(node[0]['first_name'])
#     return name_lst, user_lst, passwd_lst

def fetch_all(conn):
    query = "MATCH (u:User) RETURN u.first_name AS name, u.username AS username, u.password AS password"
    results = conn.query(query)
    names = [record['name'] for record in results]
    usernames = [record['username'] for record in results]
    hashed_passwords = [record['password'] for record in results]
    return names, usernames, hashed_passwords

def verify_user(conn, username, password):
    """Verify user credentials."""
    query = """
    MATCH (u:User {username: $username})
    RETURN u.password AS password
    """
    result = conn.query(query, parameters={"username": username})
    if result:
        stored_password = result[0]["password"]
        return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
    return False

def add_selected(conn, selected, user, keyword):
    try:
        conn.query("""
        CREATE CONSTRAINT article_id IF NOT EXISTS
        FOR (a:Article) REQUIRE a.article_id IS UNIQUE;
        """)
    except Exception as e:
        print("Constraint setup failed:", e)

    # Adding selected article
    article_id = selected['pmcid']
    title = selected['Title']
    abstract = selected['Abstract']
    query = f"""
    MERGE (a:Article {{pmcid: $article_id}})
    ON CREATE SET a.title = $title, a.abstract = $abstract
    WITH a
    MATCH (u:User {{username: $user_name}})
    MERGE (u)-[:SELECTED {{keyword:$keyword}}]->(a)
    """
    # Run the query
    try:
        conn.query(query, parameters={
            'article_id': article_id,
            'title': title,
            'abstract': abstract,
            'user_name': user,
            'keyword':keyword
        })
    except Exception as e:
        print("Error adding article or relationship:", e)

def add_recommended(conn, recommended, selected, user):
    try:
        conn.query("""
        CREATE CONSTRAINT article_id IF NOT EXISTS
        FOR (r:RecomArticle) REQUIRE r.article_id IS UNIQUE;
        """)
    except Exception as e:
        print("Constraint setup failed:", e)
    selected_id  = selected['pmcid']
    for id, item in recommended.items():
        article_id = id
        similarity = round(item['similarity_score'], 4)
        title = item['title']
        abstract = item['abstract']

        query = f"""
        MERGE (r:RecomArticle {{article_id: $article_id}})
        ON CREATE SET r.title = $title, r.abstract = $abstract, r.similarity_score = $similarity
        WITH r
        MATCH (u:User {{username: $user_name}})-[:SELECTED]->(a:Article {{pmcid: $selected_id}})
        MERGE (a)-[:RECOMMENDED]->(r)
        """
        # Run the query
        try:
            conn.query(query, parameters={
                'article_id': article_id,
                'title': title,
                'abstract': abstract,
                'user_name': user,
                'similarity':similarity,
                'selected_id':selected_id
            })
        except Exception as e:
            print("Error adding article or relationship:", e)




