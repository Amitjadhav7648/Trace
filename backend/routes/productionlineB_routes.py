
# =========================================================
# routes/productionlineB_routes.py
# FULL BACKEND
# LINE B
# =========================================================

import os
import uuid
import barcode

from barcode.writer import ImageWriter

from flask import Blueprint
from flask import request
from flask import jsonify

from psycopg2.extras import RealDictCursor

from db import get_db_connection

# =========================================================
# BLUEPRINT
# =========================================================

line_b_bp = Blueprint(
    "line_b_bp",
    __name__
)

@line_b_bp.route("/api/get-batches", methods=["GET"])
def get_batches():

    try:

        line = request.args.get("line")

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""

            SELECT
                batch_id,
                batch_code,
                component_code,
                line

            FROM batch_scan

            WHERE line = %s
            AND status = 'ACTIVE'

            ORDER BY batch_id DESC

        """, (line,))

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(rows)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# =====================================================
# FINISHED BATCH ALERT
# DISPLAY ONLY ZERO QTY BATCHES
# =====================================================

@line_b_bp.route(
    "/api/finished-batches-alert",
    methods=["GET"]
)
def finished_batches_alert():

    try:

        # =================================================
        # REQUEST
        # =================================================

        line = request.args.get("line")

        product_id = request.args.get(
            "product_id"
        )

        # =================================================
        # DB
        # =================================================

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # =================================================
        # QUERY
        # =================================================

        query = """

            SELECT

                bs.batch_id,

                bs.batch_code,

                bs.remaining_quantity,

                bs.status,

                cm.component_code,

                cm.component_name

            FROM batch_scan bs

            LEFT JOIN component_master cm

            ON bs.component_id =
               cm.component_id

            WHERE
                bs.remaining_quantity <= 0

            AND
                bs.status='COMPLETED'

        """

        values = []

        # =================================================
        # LINE FILTER
        # =================================================

        if line:

            query += """

                AND bs.line=%s

            """

            values.append(line)

        # =================================================
        # PRODUCT FILTER
        # =================================================

        if product_id:

            query += """

                AND bs.product_id=%s

            """

            values.append(product_id)

        # =================================================
        # ORDER
        # =================================================

        query += """

            ORDER BY bs.batch_id ASC

        """

        # =================================================
        # EXECUTE
        # =================================================

        cur.execute(

            query,

            tuple(values)

        )

        finished_batches = cur.fetchall()

        # =================================================
        # CLOSE
        # =================================================

        cur.close()

        conn.close()

        # =================================================
        # RESPONSE
        # =================================================

        return jsonify(
            finished_batches
        )

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500
# =====================================================
# REJECT BATCH
# =====================================================

@line_b_bp.route(
    "/api/reject-batch",
    methods=["POST"]
)
def reject_batch():

    try:

        data = request.json

        batch_ids = data.get(
            "batch_ids",
            []
        )

        reject_qty = int(
            data.get(
                "reject_qty",
                0
            )
        )

        full_reject = data.get(
            "full_reject",
            False
        )

        username = data.get(
            "username"
        )

        password = data.get(
            "password"
        )

        reject_reason = data.get(
            "reject_reason"
        )

        if username != "admin" or \
           password != "admin123":

            return jsonify({

                "error":
                "Invalid Username Or Password"

            }), 401

        conn = get_db_connection()

        conn.autocommit = False

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        for batch_id in batch_ids:

            cur.execute("""

                SELECT
                    batch_id,
                    batch_code,
                    remaining_quantity,
                    COALESCE(
                        reject_quantity,
                        0
                    ) AS reject_quantity

                FROM batch_scan

                WHERE batch_id=%s

            """, (

                batch_id,

            ))

            batch = cur.fetchone()

            if not batch:

                continue

            remaining_qty = batch[
                "remaining_quantity"
            ]

            current_reject_qty = batch[
                "reject_quantity"
            ]

            # =================================
            # FULL BATCH REJECT
            # =================================

            if full_reject:

                new_remaining_qty = 0

                new_reject_qty = (

                    current_reject_qty +

                    remaining_qty

                )

                batch_status = "REJECTED"

            # =================================
            # PARTIAL REJECT
            # =================================

            else:

                if reject_qty <= 0:

                    return jsonify({

                        "error":
                        "Enter Reject Quantity"

                    }), 400

                if reject_qty > remaining_qty:

                    return jsonify({

                        "error":
                        f"Reject Qty Greater Than Remaining Qty ({remaining_qty})"

                    }), 400

                new_remaining_qty = (

                    remaining_qty -

                    reject_qty

                )

                new_reject_qty = (

                    current_reject_qty +

                    reject_qty

                )

                batch_status = (

                    "REJECTED"

                    if new_remaining_qty == 0

                    else "ACTIVE"

                )

            cur.execute("""

                UPDATE batch_scan

                SET

                    remaining_quantity=%s,

                    reject_quantity=%s,

                    status=%s,

                    reject_reason=%s

                WHERE batch_id=%s

            """, (

                new_remaining_qty,

                new_reject_qty,

                batch_status,

                reject_reason,

                batch_id

            ))

        conn.commit()

        cur.close()

        conn.close()

        return jsonify({

            "message":
            "Batch Rejected Successfully"

        })

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500


# =========================================================
# GET PRODUCTS BY LINE
# =========================================================

@line_b_bp.route(
    "/api/line-products/<line>",
    methods=["GET"]
)
def get_line_products(line):

    try:

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""

            SELECT

                pm.product_id,
                pm.product_name,
                pm.product_code

            FROM line_product_map lpm

            LEFT JOIN product_master pm
            ON lpm.product_id = pm.product_id

            WHERE lpm.line=%s

            ORDER BY pm.product_name

        """, (

            line,

        ))

        products = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(products)

    except Exception as e:

        return jsonify({

            "error":
            str(e)

        }), 500

# =========================================================
# CREATE UID
# =========================================================

@line_b_bp.route(
    "/api/line-b/create-uid",
    methods=["POST"]
)
def create_uid_line_b():

    try:

        data = request.json

        line = data.get("line")

        product_id = data.get("product_id")

        # =================================================
        # VALIDATION
        # =================================================

        if not line:

            return jsonify({

                "error":
                "Please Select Line"

            }), 400

        if not product_id:

            return jsonify({

                "error":
                "Please Select Product"

            }), 400

        conn = get_db_connection()
        conn.autocommit = False

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # =================================================
        # REQUIRED COMPONENT COUNT
        # =================================================

        cur.execute("""

            SELECT COUNT(*) AS total

            FROM line_product_component_map

            WHERE line=%s
            AND product_id=%s       

        """, (

            line,
            product_id

        ))

        required_count = cur.fetchone()["total"]

        if required_count == 0:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                "No Components Mapped"

            }), 400

        # =================================================
        # GET ACTIVE BATCHES
        # =================================================

        cur.execute("""

            SELECT

                bs.*,

                cm.component_code

            FROM batch_scan bs

            LEFT JOIN component_master cm
            ON bs.component_id = cm.component_id

            WHERE bs.status='ACTIVE'
            AND bs.line=%s
            AND bs.product_id=%s

            ORDER BY bs.batch_id ASC
            FOR UPDATE

        """, (

            line,
            product_id

        ))

        batches = cur.fetchall()

        # =================================================
        # VALIDATE COUNT
        # =================================================

        if len(batches) < required_count:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                f"{required_count} Active Batches Required"

            }), 400

        # =================================================
        # CHECK FINISHED BATCHES
        # =================================================

        finished_batches = []

        for batch in batches:

            if batch["remaining_quantity"] <= 0:

                finished_batches.append({

                    "batch_code":
                    batch["batch_code"],

                    "component_code":
                    batch["component_code"]

                })

        if len(finished_batches) > 0:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                "Replace Finished Batches",

                "finished_batches":
                finished_batches

            }), 400

        # =================================================
        # GENERATE UID
        # =================================================

        generated_uid = (

            f"{line}-UID-" +

            str(uuid.uuid4())[:8].upper()

        )

        # =================================================
        # BARCODE
        # =================================================

        barcode_folder = "static/barcodes"

        os.makedirs(
            barcode_folder,
            exist_ok=True
        )

        barcode_class = barcode.get_barcode_class(
            "code128"
        )

        barcode_instance = barcode_class(

            generated_uid,

            writer=ImageWriter()

        )

        barcode_file = (

            f"{barcode_folder}/"

            f"{generated_uid}"

        )

        barcode_instance.save(
            barcode_file
        )

        barcode_path = (

            f"static/barcodes/" +

            f"{generated_uid}.png"

        )

        # =================================================
        # INSERT UID
        # =================================================

        cur.execute("""

            INSERT INTO uid_master
            (
                uid,
                line,
                product_id,
                barcode_path,
                current_station
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

            generated_uid,
            line,
            product_id,
            barcode_path,
            "CUTTING"

        ))

        uid_id = cur.fetchone()["uid_id"]
       
        for batch in batches:

         cur.execute("""
        INSERT INTO uid_batch_map
        (
            uid_id,
            component_id,
            batch_id,
            batch_status,
            created_at
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            NOW()
        )
    """, (
        uid_id,
        batch["component_id"],
        batch["batch_id"],
        "ACTIVE"
    ))

        # =================================================
        # UPDATE QUANTITY
        # =================================================

        for batch in batches:


            cur.execute("""

                UPDATE batch_scan

                SET

                remaining_quantity =
            remaining_quantity - 1,

            used_quantity =
            used_quantity + 1

        WHERE batch_id=%s

            """, (

                batch["batch_id"]

            ))

            # =============================================
            # AUTO COMPLETE
            # =============================================


        conn.commit()

        cur.close()
        conn.close()

        return jsonify({

            "message":
            "UID Created Successfully",

            "uid":
            generated_uid,

            "barcode":
            barcode_path

        })

    except Exception as e:

     if 'conn' in locals():
        conn.rollback()

    return jsonify({
        "error": str(e)
    }), 500

# =========================================================
# GET UID MAPPED BATCHES
# =========================================================

@line_b_bp.route(
    "/api/line-b/uid-batches/<uid>",
    methods=["GET"]
)
def get_uid_batches(uid):

    try:

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""

            SELECT

                cm.component_code,
                bs.batch_code,
                ubm.batch_status

            FROM uid_batch_map ubm

            LEFT JOIN component_master cm
            ON ubm.component_id = cm.component_id

            LEFT JOIN batch_scan bs
            ON ubm.batch_id = bs.batch_id

            LEFT JOIN uid_master um
            ON ubm.uid_id = um.uid_id

            WHERE um.uid = %s

            ORDER BY cm.component_code

        """, (uid,))

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(rows)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
