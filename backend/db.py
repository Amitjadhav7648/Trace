import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():

    conn = psycopg2.connect(

        host="localhost",
        database="honda_traceability",
        user="postgres",
        password="siri1234",

        cursor_factory=RealDictCursor
    )

    return conn