# =====================================================
# routes/final_serial_routes.py
# =====================================================

from flask import Blueprint, request, jsonify
from psycopg2.extras import RealDictCursor
from db import get_db_connection

# =====================================================
# BLUEPRINT
# =====================================================

final_serial_bp = Blueprint(
    "final_serial",
    __name__
)

# =====================================================
# GET LATEST SERIAL FROM TESTER
# =====================================================
@final_serial_bp.route(
    "/api/get-latest-serial",
    methods=["GET"]
)
def get_latest_serial():

    try:

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""

            SELECT t.serial_no

            FROM tester_results t

            WHERE NOT EXISTS
            (
                SELECT 1
                FROM final_serial_traceability f
                WHERE f.serial_no = t.serial_no
            )

            ORDER BY t.id ASC

            LIMIT 1

        """)

        row = cur.fetchone()

        cur.close()
        conn.close()

        if not row:

            return jsonify({

                "serial_no": ""

            })

        return jsonify({

            "serial_no":
            row["serial_no"]

        })

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500

# =====================================================
# SAVE FINAL TRACEABILITY
# =====================================================

@final_serial_bp.route(
    "/api/save-final-serial",
    methods=["POST"]
)
def save_final_serial():

    try:

        data = request.json

        uid_line_a = data.get(
            "uid_line_a"
        )

        uid_line_b = data.get(
            "uid_line_b"
        )

        uid_line_c = data.get(
            "uid_line_c"
        )

        uid_line_d = data.get(
            "uid_line_d"
        )

        # ==========================================
        # VALIDATION
        # ==========================================

        if not uid_line_a:

            return jsonify({

                "error":
                "Scan Line A UID"

            }), 400

        if not uid_line_b:

            return jsonify({

                "error":
                "Scan Line B UID"

            }), 400

        if not uid_line_c:

            return jsonify({

                "error":
                "Scan Line C UID"

            }), 400

        if not uid_line_d:

            return jsonify({

                "error":
                "Scan Line D UID"

            }), 400

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # ==========================================
        # GET LATEST TESTER SERIAL
        # ==========================================

        cur.execute("""

            SELECT serial_no

            FROM tester_results

            ORDER BY id DESC

            LIMIT 1

        """)

        serial_row = cur.fetchone()

        if not serial_row:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                "Tester Serial Not Found"

            }), 404

        serial_no = serial_row[
            "serial_no"
        ]

        # ==========================================
        # CHECK DUPLICATE SERIAL
        # ==========================================

        cur.execute("""

            SELECT id

            FROM final_serial_traceability

            WHERE serial_no=%s

        """, (

            serial_no,

        ))

        duplicate = cur.fetchone()

        if duplicate:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                f"Serial Already Mapped : {serial_no}"

            }), 400

        # ==========================================
        # UID A VALIDATION
        # ==========================================

        cur.execute("""

            SELECT uid

            FROM uid_master

            WHERE uid=%s
                    
            AND line='A'

        """, (

            uid_line_a,

        ))

        if not cur.fetchone():

            cur.close()
            conn.close()

            return jsonify({

                "error":
                "Please scan a valid Line A UID"

            }), 400

        # ==========================================
        # UID B VALIDATION
        # ==========================================

        cur.execute("""

            SELECT uid

            FROM uid_master

            WHERE uid=%s
            
            AND line='B'

        """, (

            uid_line_b,

        ))

        if not cur.fetchone():

            cur.close()
            conn.close()

            return jsonify({

                "error":
               "Please scan a valid Line B UID"

            }), 400

        # ==========================================
        # UID C VALIDATION
        # ==========================================

        cur.execute("""

            SELECT uid

            FROM uid_master

            WHERE uid=%s
            
            AND line='C'

        """, (

            uid_line_c,

        ))

        if not cur.fetchone():

            cur.close()
            conn.close()

            return jsonify({

                "error":
                "Please scan a valid Line C UID"

            }), 400

        # ==========================================
        # UID D VALIDATION
        # ==========================================

        cur.execute("""

            SELECT uid

            FROM uid_master

            WHERE uid=%s
                    
            AND line='D'

        """, (

            uid_line_d,

        ))

        if not cur.fetchone():

            cur.close()
            conn.close()

            return jsonify({

                "error":
                "Please scan a valid Line D UID"

            }), 400

        # ==========================================
        # SAVE TRACEABILITY
        # ==========================================

        cur.execute("""

            INSERT INTO final_serial_traceability
            (
                serial_no,
                uid_line_a,
                uid_line_b,
                uid_line_c,
                uid_line_d
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )

            RETURNING *

        """, (

            serial_no,
            uid_line_a,
            uid_line_b,
            uid_line_c,
            uid_line_d

        ))

        saved_data = cur.fetchone()

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({

            "message":
            "Traceability Saved Successfully",

            "serial_no":
            serial_no,

            "data":
            saved_data

        })

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500


# =====================================================
# GET ALL FINAL SERIAL RECORDS
# =====================================================

@final_serial_bp.route(
    "/api/final-serial-records",
    methods=["GET"]
)
def get_final_serial_records():

    try:

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""

            SELECT *

            FROM final_serial_traceability

            ORDER BY id DESC

        """)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(rows)

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500
    

# =====================================================
# TRACE SERIAL
# =====================================================

@final_serial_bp.route(
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

            WHERE serial_no=%s

        """, (

            serial_no,

        ))

        trace = cur.fetchone()

        if not trace:

            return jsonify({

                "error":
                "Serial Not Found"

            }), 404

        return jsonify(trace)

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500

    finally:

        cur.close()
        conn.close()