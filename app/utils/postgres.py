"""
"""

import os
import psycopg


CREATE_STATEMENTS = {
    'conversations' : """
        CREATE TABLE conversations (
            id TEXT PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            course TEXT NOT NULL,
            model_used TEXT NOT NULL,
            response_time FLOAT NOT NULL,
            relevance TEXT NOT NULL,
            relevance_explanation TEXT NOT NULL,
            prompt_tokens INTEGER NOT NULL,
            completion_tokens INTEGER NOT NULL,
            total_tokens INTEGER NOT NULL,
            eval_prompt_tokens INTEGER NOT NULL,
            eval_completion_tokens INTEGER NOT NULL,
            eval_total_tokens INTEGER NOT NULL,
            openai_cost FLOAT NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL
        );
    """.strip(),
    'feedback' : """
        CREATE TABLE feedback (
            id SERIAL PRIMARY KEY,
            conversation_id TEXT REFERENCES conversations(id),
            feedback INTEGER NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL
        )
    """.strip(),
}


def get_db_connection(autocommit=True, **conn_info):
    """
    """
    return psycopg.connect(
        host=conn_info.get("postgres_host"),
        dbname=conn_info.get("postgres_db"),
        user=conn_info.get("postgres_user"),
        password=conn_info.get("postgres_password"),
        port=conn_info.get("postgres_port"),
        autocommit=autocommit,
    )


def check_database_exists(conn, db_name):
    """
    """
    query = f"""
    SELECT EXISTS (
        SELECT 1 FROM pg_database WHERE datname='{db_name}'
    );
    """.strip()
    
    res = conn.execute(query)
    db_exists = res.fetchall()[0][0]

    return db_exists


def check_table_exists(conn, table_name):
    """
    """
    query = f"""
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = '{table_name}'
    );
    """
    
    res = conn.execute(query)
    table_exists = res.fetchall()[0][0]
            
    return bool(table_exists)


def init_db():
    """
    """
    conn_info = {
        'postgres_host':os.getenv("POSTGRES_HOST"),
        'postgres_user':os.getenv("POSTGRES_USER"),
        'postgres_password':os.getenv("POSTGRES_PASSWORD"),
        'postgres_port':os.getenv("POSTGRES_PORT"),
    }
    postgres_db = os.getenv("POSTGRES_DB")

    ## =====> Database
    with get_db_connection(**conn_info) as conn:
        if check_database_exists(conn, postgres_db):
            print(f'Database {postgres_db} already exists')
        else:
            conn.execute(f"create database {postgres_db};")
            print(f'Successfully created database {postgres_db}')

    ## =====> Tables
    conn_info['postgres_db'] = postgres_db
    with get_db_connection(**conn_info) as conn:
        for table_name in ['conversations', 'feedback']:
            if check_table_exists(conn, table_name):
                print(f'Table {table_name} already exists')
            else:
                conn.execute(CREATE_STATEMENTS[table_name])
                print(f'Successfully created table {table_name}')