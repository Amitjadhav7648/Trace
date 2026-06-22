# =====================================================
# routes/dashboard_routes.py
# =====================================================

from flask import Blueprint
from flask import jsonify

from psycopg2.extras import RealDictCursor

from db import get_db_connection

# =====================================================
# BLUEPRINT
# =====================================================

dashboard_bp = Blueprint(
    "dashboard_bp",
    __name__
)

# =====================================================
# TOTAL UID CREATED TODAY
# =====================================================

@dashboard_bp.route(
    "/api/today-uid-count",
    methods=["GET"]
)
def today_uid_count():

    try:

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""

            SELECT COUNT(*) AS total_uid

            FROM uid_master

            WHERE DATE(created_at)=CURRENT_DATE

        """)

        result = cur.fetchone()

        cur.close()
        conn.close()

        return jsonify({

            "total_uid":
            result["total_uid"]

        })

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500


# =====================================================
# UID COUNT BY LINE TODAY
# =====================================================

@dashboard_bp.route(
    "/api/today-line-wise-count",
    methods=["GET"]
)
def today_line_wise_count():

    try:

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""

            SELECT

                line,

                COUNT(*) AS total

            FROM uid_master

            WHERE DATE(created_at) = CURRENT_DATE

            GROUP BY line

            ORDER BY line

        """)

        rows = cur.fetchall()

        response = {

            "A": 0,
            "B": 0,
            "C": 0,
            "D": 0

        }

        for row in rows:

            response[row["line"]] = row["total"]

        cur.close()
        conn.close()

        return jsonify(response)

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500


# =====================================================
# DASHBOARD SUMMARY
# =====================================================

@dashboard_bp.route(
    "/api/dashboard-summary",
    methods=["GET"]
)
def dashboard_summary():

    try:

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # =============================================
        # TOTAL UID TODAY
        # =============================================

        cur.execute("""

            SELECT COUNT(*) AS total

            FROM uid_master

            WHERE DATE(created_at)=CURRENT_DATE

        """)

        total_uid = cur.fetchone()["total"]

        # =============================================
        # TOTAL SERIAL TODAY
        # =============================================

        cur.execute("""

            SELECT COUNT(*) AS total

            FROM final_serial_traceability

            WHERE DATE(created_at)=CURRENT_DATE

        """)

        serial_result = cur.fetchone()

        total_serial = serial_result["total"]

        # =============================================
        # LINE COUNTS
        # =============================================

        cur.execute("""

            SELECT

                line,

                COUNT(*) AS total

            FROM uid_master

            WHERE DATE(created_at)=CURRENT_DATE

            GROUP BY line

        """)

        rows = cur.fetchall()

        line_counts = {

            "A": 0,
            "B": 0,
            "C": 0,
            "D": 0

        }

        for row in rows:

            line_counts[row["line"]] = row["total"]

        cur.close()
        conn.close()

        return jsonify({

            "total_uid":
            total_uid,

            "total_serial":
            total_serial,

            "line_a":
            line_counts["A"],

            "line_b":
            line_counts["B"],

            "line_c":
            line_counts["C"],

            "line_d":
            line_counts["D"]

        })

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500