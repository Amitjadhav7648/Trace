from flask import Blueprint
from db import get_db_connection
from psycopg2.extras import RealDictCursor

comp_bp = Blueprint("comp", __name__)

@comp_bp.route("/api/components")
def components():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM component_master")
    data = cur.fetchall()

    cur.close()
    conn.close()

    return {"components": data}