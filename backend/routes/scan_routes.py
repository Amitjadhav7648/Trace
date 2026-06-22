# =====================================================
# routes/scan_batch_routes.py
# FULL FINAL WORKING CODE
# =====================================================

from flask import Blueprint
from flask import request
from flask import jsonify

from psycopg2.extras import RealDictCursor

from db import get_db_connection

scan_bp = Blueprint(
    "scan_batch",
    __name__
)

# =====================================================
# NORMALIZE
# =====================================================

def normalize(value):

    return (

        value
        .replace("\r", "")
        .replace("\n", "")
        .strip()
        .upper()

    )

# =====================================================
# GET PRODUCTS
# =====================================================

@scan_bp.route(
    "/api/get-products",
    methods=["GET"]
)
def get_products():

    try:

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""

            SELECT *

            FROM product_master

            ORDER BY product_name ASC

        """)

        products = cur.fetchall()

        
        cur.close()
        conn.close()

        return jsonify(products)

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500

# =====================================================
# SCAN BATCH
# =====================================================

@scan_bp.route(
    "/api/scan-batch",
    methods=["POST"]
)
def scan_batch():

    try:

        data = request.json

        scan_value = data.get(
            "scan_value"
        )

        line = data.get(
            "line"
        )

        product_id = data.get(
            "product_id"
        )

        # =================================================
        # VALIDATION
        # =================================================

        if not scan_value:

            return jsonify({

                "error":
                "Scan Value Required"

            }), 400

        if not product_id:

            return jsonify({

                "error":
                "Product Required"

            }), 400

        if not line:

            line = "A"

        # =================================================
        # SPLIT QR
        # =================================================

        values = scan_value.split("|")

        batch_code = ""
        component_code = ""
        quantity = 0

        for item in values:

            # =============================================
            # BATCH
            # =============================================

            if "BATCH:" in item:

                batch_code = normalize(

                    item.replace(
                        "BATCH:",
                        ""
                    )

                )

            # =============================================
            # COMPONENT
            # =============================================

            if "COMPONENT:" in item:

                component_code = normalize(

                    item.replace(
                        "COMPONENT:",
                        ""
                    )

                )

            # =============================================
            # QTY
            # =============================================

            if "QTY:" in item:

                quantity = int(

                    item.replace(
                        "QTY:",
                        ""
                    ).strip()

                )

        # =================================================
        # DB
        # =================================================

        conn = get_db_connection()

        conn.autocommit = False
        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # =================================================
        # GET COMPONENT
        # =================================================

        cur.execute("""

            SELECT *

            FROM component_master

            WHERE UPPER(component_code)=UPPER(%s)

        """, (

            component_code,

        ))

        component = cur.fetchone()

        if not component:

        
            cur.close()
            conn.close()

            return jsonify({

                "error":
                "Invalid Component"

            }), 400

        component_id = component["component_id"]

        # =================================================
        # VALIDATE MAPPING
        # =================================================

        cur.execute("""

            SELECT *

            FROM line_product_component_map

            WHERE product_id=%s
            AND component_id=%s
            AND line=%s

        """, (

            product_id,
            component_id,
            line

        ))

        mapping = cur.fetchone()

        if not mapping:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                f"{component_code} Not Mapped For Selected Product On Line {line}"

            }), 400

        # =================================================
        # DUPLICATE CHECK
        # =================================================

        cur.execute("""

            SELECT *

            FROM batch_scan

            WHERE UPPER(batch_code)=UPPER(%s)
                    
            FOR UPDATE        

        """, (

            batch_code,

        ))

        duplicate = cur.fetchone()

        if duplicate:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                f"Batch Already Exists : {batch_code}"

            }), 400

        # =================================================
        # REPLACE OLD ACTIVE
        # =================================================

        cur.execute("""

            UPDATE batch_scan

            SET status='REPLACED'

            WHERE component_id=%s
            AND line=%s
            AND status='ACTIVE'

        """, (

            component_id,
            line

        ))

        # =================================================
        # INSERT NEW BATCH
        # =================================================

        cur.execute("""

            INSERT INTO batch_scan
            (
                component_id,
                product_id,
                batch_code,
                line,
                total_quantity,
                used_quantity,
                remaining_quantity,
                status
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )

        """, (

            component_id,
            product_id,
            batch_code,
            line,
            quantity,
            0,
            quantity,
            "ACTIVE"

        ))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({

            "message":
            "Batch Scan Successfully"

        })

    except Exception as e:

     if 'conn' in locals():
        conn.rollback()
        conn.close()

    return jsonify({
        "error": str(e)
    }), 500

# =====================================================
# GET BATCHES
# =====================================================

@scan_bp.route(
    "/api/get-batches",
    methods=["GET"]
)
def get_batches():

    try:

        line = request.args.get("line")
        product_id = request.args.get("product_id")

        if not line or not product_id:

            return jsonify([])

        conn = get_db_connection()

        cur = conn.cursor(
        cursor_factory=RealDictCursor
)

        cur.execute("""

    SELECT

        bs.batch_id,
        bs.batch_code,
        bs.component_id,
        cm.component_code,
        cm.component_name,

        bs.line,
        bs.product_id,

        bs.total_quantity,
        bs.used_quantity,
        bs.remaining_quantity,

        bs.status

    FROM batch_scan bs

    LEFT JOIN component_master cm
    ON bs.component_id = cm.component_id

    WHERE bs.line=%s
    AND bs.product_id=%s
    AND bs.status='ACTIVE'

    ORDER BY bs.batch_id DESC

""", (

    line,
    product_id

))
        batches = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(batches)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
# =====================================================
# REPLACE ALL ACTIVE BATCHES
# =====================================================

@scan_bp.route(
    "/api/reset-active-batches",
    methods=["POST"]
)
def reset_active_batches():

    try:

        data = request.json

        line = data.get("line")

        if not line:

            return jsonify({

                "error":
                "Please Select Line"

            }), 400

        conn = get_db_connection()

        conn.autocommit = False

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # =============================================
        # UPDATE ACTIVE BATCHES FOR SELECTED LINE ONLY
        # =============================================

        cur.execute("""

            UPDATE batch_scan

            SET status='REPLACED'

            WHERE status='ACTIVE'
            AND line=%s

        """, (

            line,

        ))

        conn.commit()

        affected_rows = cur.rowcount

        cur.close()
        conn.close()

        return jsonify({

            "message":
            f"{affected_rows} Active Batches Replaced Successfully For Line {line}"

        })

    except Exception as e:

     if 'conn' in locals():
        conn.rollback()
        conn.close()

    return jsonify({
        "error": str(e)
    }), 500
# =====================================================
# CHANGE SINGLE BATCH
# =====================================================

@scan_bp.route(
    "/api/change-single-batch",
    methods=["POST"]
)
def change_single_batch():

    try:

        data = request.json

        old_batch_id = data.get(
            "old_batch_id"
        )

        scan_value = data.get(
            "scan_value"
        )

        line = data.get(
            "line"
        )

        product_id = data.get(
            "product_id"
        )

        # =================================================
        # VALIDATION
        # =================================================

        if not old_batch_id:

            return jsonify({

                "error":
                "Old Batch Required"

            }), 400

        if not scan_value:

            return jsonify({

                "error":
                "New Batch QR Required"

            }), 400

        # =================================================
        # SPLIT QR
        # =================================================

        values = scan_value.split("|")

        batch_code = ""
        component_code = ""
        quantity = 0

        for item in values:

            # =============================================
            # BATCH
            # =============================================

            if "BATCH:" in item:

                batch_code = normalize(

                    item.replace(
                        "BATCH:",
                        ""
                    )

                )

            # =============================================
            # COMPONENT
            # =============================================

            if "COMPONENT:" in item:

                component_code = normalize(

                    item.replace(
                        "COMPONENT:",
                        ""
                    )

                )

            # =============================================
            # QTY
            # =============================================

            if "QTY:" in item:

                quantity = int(

                    item.replace(
                        "QTY:",
                        ""
                    ).strip()

                )

        # =================================================
        # DB
        # =================================================

        conn = get_db_connection()

        conn.autocommit = False

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # =================================================
        # GET OLD BATCH
        # =================================================

        cur.execute("""

            SELECT *

            FROM batch_scan

            WHERE batch_id=%s

        """, (

            old_batch_id,

        ))

        old_batch = cur.fetchone()

        if not old_batch:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                "Old Batch Not Found"

            }), 404

        # =================================================
        # CHECK DUPLICATE
        # =================================================

        cur.execute("""

            SELECT *

            FROM batch_scan

            WHERE UPPER(batch_code)=UPPER(%s)
          
            FOR UPDATE

        """, (

            batch_code,

        ))

        duplicate = cur.fetchone()

        if duplicate:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                f"Batch Already Exists : {batch_code}"

            }), 400

        # =================================================
        # GET COMPONENT
        # =================================================

        cur.execute("""

            SELECT *

            FROM component_master

            WHERE UPPER(component_code)=UPPER(%s)

        """, (

            component_code,

        ))

        component = cur.fetchone()

        if not component:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                "Invalid Component"

            }), 400

        component_id = component["component_id"]

        # =================================================
        # VALIDATE SAME COMPONENT
        # =================================================

        if component_id != old_batch["component_id"]:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                "Component Mismatch"

            }), 400

        # =================================================
        # OLD BATCH -> REPLACED
        # =================================================

        cur.execute("""

            UPDATE batch_scan

            SET status='REPLACED'

            WHERE batch_id=%s

        """, (

            old_batch_id,

        ))

        # =================================================
        # INSERT NEW ACTIVE BATCH
        # =================================================

        cur.execute("""

            INSERT INTO batch_scan
            (
                component_id,
                product_id,
                batch_code,
                line,
                total_quantity,
                used_quantity,
                remaining_quantity,
                status
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )

            RETURNING *

        """, (

            component_id,
            product_id,
            batch_code,
            line,
            quantity,
            0,
            quantity,
            "ACTIVE"

        ))

        new_batch = cur.fetchone()

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({

            "message":
            "Batch Replaced Successfully",

            "batch":
            new_batch

        })
    
    except Exception as e:

     if 'conn' in locals():
        conn.rollback()
        conn.close()

    return jsonify({
        "error": str(e)
    }), 500