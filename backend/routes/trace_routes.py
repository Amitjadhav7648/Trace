
# =========================================================
# routes/trace_routes.py
# FULL UID + SERIAL TRACEABILITY
# =========================================================

from flask import Blueprint
from flask import jsonify

from db import get_db_connection

from psycopg2.extras import RealDictCursor

# =========================================================
# BLUEPRINT
# =========================================================

trace_bp = Blueprint(
    "trace",
    __name__
)

# =========================================================
# COMMON UID TRACE FUNCTION
# =========================================================

def get_uid_details(cur, uid):

    cur.execute("""

        SELECT

            um.*,

            pm.product_name

        FROM uid_master um

        LEFT JOIN product_master pm

        ON um.product_id = pm.product_id

        WHERE um.uid = %s

    """, (

        uid,

    ))

    uid_data = cur.fetchone()

    if not uid_data:

        return None

    uid_id = uid_data["uid_id"]

    line = uid_data["line"]

    # =====================================================
    # BATCH DETAILS
    # =====================================================

    cur.execute("""

        SELECT

            ubm.map_id,

            ubm.batch_id,

            ubm.uid_id,

            bs.batch_code,

            bs.line,

            ubm.batch_status AS status,

            cm.component_code,

            cm.component_name,

            cm.usage_station

        FROM uid_batch_map ubm

        LEFT JOIN batch_scan bs

        ON ubm.batch_id = bs.batch_id

        LEFT JOIN component_master cm

        ON ubm.component_id = cm.component_id

        WHERE ubm.uid_id = %s
        AND bs.line = %s

        ORDER BY ubm.map_id ASC

    """, (

        uid_id,
        line

    ))

    batches = cur.fetchall()

    torque_results = []

    test_results = []

    # =====================================================
    # ONLY LINE A HAS TORQUE + TEST
    # =====================================================

    if line == "A":

        cur.execute("""

            SELECT *

            FROM torque_results

            WHERE uid_id = %s

            ORDER BY station_id ASC

        """, (

            uid_id,

        ))

        torque_results = cur.fetchall()

        cur.execute("""

            SELECT *

            FROM test_results

            WHERE uid_id = %s

            ORDER BY station_id ASC

        """, (

            uid_id,

        ))

        test_results = cur.fetchall()

    return {

        "uid":
        uid_data["uid"],

        "line":
        uid_data["line"],

        "product_name":
        uid_data["product_name"],

        "created_at":
        uid_data["created_at"],

        "batches":
        batches,

        "torque_results":
        torque_results,

        "test_results":
        test_results

    }

# =========================================================
# TRACE UID
# =========================================================

@trace_bp.route(
    "/api/trace/<uid>",
    methods=["GET"]
)
def trace_uid(uid):

    try:

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        response = get_uid_details(
            cur,
            uid
        )

        if not response:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                "UID Not Found"

            }), 404

        cur.close()
        conn.close()

        return jsonify(response)

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500

# =========================================================
# TRACE SERIAL NUMBER
# =========================================================

@trace_bp.route(
    "/api/trace-serial/<serial_no>",
    methods=["GET"]
)
def trace_serial(serial_no):

    try:

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""

            SELECT *

            FROM final_serial_traceability

            WHERE serial_no = %s

        """, (

            serial_no,

        ))

        serial_data = cur.fetchone()

        if not serial_data:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                "Serial Number Not Found"

            }), 404

        response = {

            "serial_no":
            serial_data["serial_no"],

            "uid_line_a":
            get_uid_details(
                cur,
                serial_data["uid_line_a"]
            ),

            "uid_line_b":
            get_uid_details(
                cur,
                serial_data["uid_line_b"]
            ),

            "uid_line_c":
            get_uid_details(
                cur,
                serial_data["uid_line_c"]
            ),

            "uid_line_d":
            get_uid_details(
                cur,
                serial_data["uid_line_d"]
            )

        }

        cur.close()
        conn.close()

        return jsonify(response)

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500