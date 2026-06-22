# =====================================================
# routes/records_routes.py
# =====================================================

from flask import Blueprint
from flask import jsonify
from flask import request

from psycopg2.extras import RealDictCursor

from db import get_db_connection

records_bp = Blueprint(
    "records",
    __name__
)

# =====================================================
# GET RECORDS
# =====================================================

@records_bp.route(
    "/api/get-records",
    methods=["GET"]
)
def get_records():

    try:

        from_date = request.args.get(
            "from_date"
        )

        to_date = request.args.get(
            "to_date"
        )

        uid = request.args.get(
            "uid"
        )

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        query = """

            SELECT

                um.uid,
                um.line,

                pm.product_name,

                tr.torque_value,
                tr.result AS torque_result,

                er.resistance,
                er.continuity,
                er.actuator,
                er.result AS electrical_result,

                um.created_at

            FROM uid_master um

            LEFT JOIN torque_results tr
            ON um.uid_id = tr.uid_id

            LEFT JOIN test_results er
            ON um.uid_id = er.uid_id

            LEFT JOIN product_master pm
            ON um.product_id = pm.product_id

            WHERE 1=1

        """

        params = []

        # =================================================
        # FROM DATE
        # =================================================

        if from_date:

            query += """

                AND DATE(um.created_at) >= %s

            """

            params.append(from_date)

        # =================================================
        # TO DATE
        # =================================================

        if to_date:

            query += """

                AND DATE(um.created_at) <= %s

            """

            params.append(to_date)

        # =================================================
        # UID
        # =================================================

        if uid:

            query += """

                AND UPPER(um.uid)=UPPER(%s)

            """

            params.append(uid)

        query += """

            ORDER BY um.uid_id DESC

        """

        cur.execute(query, params)

        records = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(records)

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500