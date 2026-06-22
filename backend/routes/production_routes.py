# =========================================================
# routes/production.py
# FULL UPDATED CODE
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

production_bp = Blueprint(
    "production",
    __name__
)

# =========================================================
# GET ACTIVE BATCHES
# =========================================================

@production_bp.route(
    "/api/get-batches",
    methods=["GET"]
)
def get_batches():

    try:

        line = request.args.get("line")
        product_id = request.args.get("product_id")

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""

            SELECT

                batch_id,
                batch_code,
                component_code,
                line,
                product_id,
                status

            FROM batch_scan

            WHERE line=%s
            AND product_id=%s
            AND status='ACTIVE'

            ORDER BY batch_id DESC

        """, (

            line,
            product_id

        ))

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(rows)

    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500

# =====================================================
# REJECT BATCH
# =====================================================
@production_bp.route(
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
# =====================================================
# FINISHED BATCH ALERT
# SHOW COMPLETED + REJECTED BATCHES
# =====================================================

@production_bp.route(
    "/api/finished-batches-alert",
    methods=["GET"]
)
def finished_batches_alert():

    try:

        line = request.args.get("line")
        product_id = request.args.get("product_id")

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute("""

            SELECT

                bs.batch_id,
                bs.batch_code,
                bs.remaining_quantity,
                bs.status,

                cm.component_code,
                cm.component_name

            FROM batch_scan bs

            LEFT JOIN component_master cm
            ON bs.component_id = cm.component_id

            WHERE bs.batch_id IN (

                SELECT MAX(batch_id)

                FROM batch_scan

                WHERE status IN (
                    'COMPLETED',
                    'REJECTED'
                )

                AND line = %s
                AND product_id = %s

                GROUP BY component_id

            )

            AND NOT EXISTS (

                SELECT 1

                FROM batch_scan active_bs

                WHERE active_bs.component_id =
                      bs.component_id

                AND active_bs.line =
                    bs.line

                AND active_bs.product_id =
                    bs.product_id

                AND active_bs.status =
                    'ACTIVE'

                AND active_bs.remaining_quantity > 0

            )

            ORDER BY bs.batch_id DESC

        """, (

            line,
            product_id

        ))

        finished_batches = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(
            finished_batches
        )

    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500

# =========================================================
# CREATE UID
# =========================================================

@production_bp.route(
    "/api/create-uid",
    methods=["POST"]
)
def create_uid():

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

        # =================================================
        # DB
        # =================================================

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

        # =================================================
        # NO COMPONENT MAPPED
        # =================================================

        if required_count == 0:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                "No Components Mapped"

            }), 400

        # =================================================
        # ACTIVE BATCHES
        # =================================================

        cur.execute("""

            SELECT *

            FROM batch_scan

            WHERE line=%s
            AND product_id=%s
            AND status='ACTIVE'

            ORDER BY batch_id ASC

        """, (

            line,

            product_id

        ))

        batches = cur.fetchall()

        # =================================================
        # VALIDATE BATCH COUNT
        # =================================================

        if len(batches) < required_count:

            cur.close()
            conn.close()

            return jsonify({

                "error":
                f"{required_count} Active Batches Required"

            }), 400

        # =================================================
        # CHECK FINISHED BATCH
        # =================================================

        finished_batches = []

        for batch in batches:

            if batch["remaining_quantity"] <= 0:

                finished_batches.append(
                    batch["batch_code"]
                )

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

            f"static/barcodes/"

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

            "CREATED"

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
        # UPDATE BATCH QUANTITY
        # =================================================

        for batch in batches:

            new_remaining = (

                batch["remaining_quantity"] - 1

            )

            new_used = (

                batch["used_quantity"] + 1

            )

            # =============================================
            # UPDATE QTY
            # =============================================

            cur.execute("""

                UPDATE batch_scan

                SET
                    remaining_quantity=%s,
                    used_quantity=%s

                WHERE batch_id=%s

            """, (

                new_remaining,

                new_used,

                batch["batch_id"]

            ))

            # =============================================
            # AUTO COMPLETE
            # =============================================

            if new_remaining <= 0:

                cur.execute("""

                    UPDATE batch_scan

                    SET status='COMPLETED'

                    WHERE batch_id=%s

                """, (

                    batch["batch_id"],

                ))

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
# STATION 1
# =========================================================

@production_bp.route(
    "/api/station-1",
    methods=["POST"]
)
def station_1():

    try:

        data = request.json

        uid = data.get("uid")

        conn = get_db_connection()
        conn.autocommit = False

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # =================================================
        # GET UID
        # =================================================

        cur.execute("""

            SELECT *

            FROM uid_master

            WHERE uid=%s

        """, (

            uid,

        ))

        uid_data = cur.fetchone()

        if not uid_data:

            return jsonify({

                "error":
                "Invalid UID"

            }), 404

        # =================================================
        # CHECK ALREADY MAPPED
        # =================================================

        cur.execute("""

            SELECT *

            FROM uid_batch_map

            WHERE uid_id=%s

        """, (

            uid_data["uid_id"],

        ))

        already = cur.fetchone()

        # =================================================
        # FIRST TIME MAP
        # =================================================

        if already is None:

            cur.execute("""

                SELECT

                    bs.batch_id,
                    bs.component_id,

                    cm.component_code,
                    bs.batch_code

                FROM batch_scan bs

                LEFT JOIN component_master cm
                ON bs.component_id = cm.component_id

                WHERE bs.status='ACTIVE'
                AND bs.line=%s
                AND bs.product_id=%s

            """, (

                uid_data["line"],

                uid_data["product_id"]

            ))

            batches = cur.fetchall()

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

                    uid_data["uid_id"],

                    batch["component_id"],

                    batch["batch_id"],

                    "ACTIVE"

                ))

            # =============================================
            # UPDATE STATION
            # =============================================

            cur.execute("""

                UPDATE uid_master

                SET current_station='ST1_DONE'

                WHERE uid_id=%s

            """, (

                uid_data["uid_id"],

            ))

            conn.commit()

        # =================================================
        # TABLE DATA
        # =================================================

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

            WHERE ubm.uid_id=%s

        """, (

            uid_data["uid_id"],

        ))

        table_data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({

            "message":
            "Batches Mapped",

            "table":
            table_data

        })

    except Exception as e:

     if 'conn' in locals():
        conn.rollback()

    return jsonify({
        "error": str(e)
    }), 500


# =========================================================
# STATION 2
# =========================================================

@production_bp.route(
    "/api/station-2",
    methods=["POST"]
)
def station_2():

    try:

        data = request.json

        uid = data.get("uid")

        torque = data.get("torque")

        conn = get_db_connection()
        conn.autocommit = False

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # =================================================
        # GET UID
        # =================================================

        cur.execute("""

            SELECT *

            FROM uid_master

            WHERE uid=%s

        """, (

            uid,

        ))

        uid_data = cur.fetchone()

        if not uid_data:

            return jsonify({

                "error":
                "First Scan UID"

            }), 404
    
            
            
        # =================================================
        # STATION 1 CHECK
        # =================================================

        cur.execute("""

            SELECT *

            FROM uid_batch_map

            WHERE uid_id=%s

            LIMIT 1

        """, (

            uid_data["uid_id"],

        ))

        station1_done = cur.fetchone()

        if station1_done is None:

            return jsonify({

                "error":
                "Complete Station 1 First"

            }), 400

        # =================================================
        # DUPLICATE CHECK
        # =================================================

        cur.execute("""

            SELECT *

            FROM torque_results

            WHERE uid_id=%s

        """, (

            uid_data["uid_id"],

        ))

        already_done = cur.fetchone()

        if already_done:

            return jsonify({

                "error":
                "Torque Already Saved"

            }), 400

        # =================================================
        # RESULT
        # =================================================

        result = "OK"

        if float(torque) < 10 or \
           float(torque) > 15:

            result = "NG"

        # =================================================
        # INSERT TORQUE
        # =================================================

        cur.execute("""

            INSERT INTO torque_results
            (
                uid_id,
                station_id,
                torque_value,
                result,
                line
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

            uid_data["uid_id"],

            "2",

            torque,

            result,

            uid_data["line"]

        ))

        torque_data = cur.fetchone()

        # =================================================
        # UPDATE STATION
        # =================================================

        cur.execute("""

            UPDATE uid_master

            SET current_station='ST2_DONE'

            WHERE uid_id=%s

        """, (

            uid_data["uid_id"],

        ))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({

            "message":
            "Torque Saved",

            "torque_value":
            torque_data["torque_value"],

            "result":
            torque_data["result"]

        })

    except Exception as e:

     if 'conn' in locals():
        conn.rollback()

    return jsonify({
        "error": str(e)
    }), 500


# =========================================================
# STATION 3
# =========================================================

@production_bp.route(
    "/api/station-3",
    methods=["POST"]
)
def station_3():

    try:

        data = request.json

        uid = data.get("uid")

        resistance = data.get("resistance")

        continuity = data.get("continuity")

        actuator = data.get("actuator")

        conn = get_db_connection()
        conn.autocommit = False

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # =================================================
        # GET UID
        # =================================================

        cur.execute("""

            SELECT *

            FROM uid_master

            WHERE uid=%s

        """, (

            uid,

        ))

        uid_data = cur.fetchone()

        if not uid_data:

            return jsonify({

                "error":
                "First Scan UID"

            }), 404
        
    
        # =================================================
        # STATION 2 CHECK
        # =================================================

        cur.execute("""

            SELECT *

            FROM torque_results

            WHERE uid_id=%s

        """, (

            uid_data["uid_id"],

        ))

        station2_done = cur.fetchone()

        if station2_done is None:

            return jsonify({

                "error":
                "Complete Station 2 First"

            }), 400

        # =================================================
        # DUPLICATE CHECK
        # =================================================

        cur.execute("""

            SELECT *

            FROM test_results

            WHERE uid_id=%s

            LIMIT 1

        """, (

            uid_data["uid_id"],

        ))

        already_done = cur.fetchone()

        if already_done:

            return jsonify({

                "error":
                f"{uid} Electrical Already Saved"

            }), 400

        # =================================================
        # RESULT
        # =================================================

        result = "OK"

        if float(resistance) > 5:

            result = "NG"

        if continuity == "NG":

            result = "NG"

        if actuator == "NG":

            result = "NG"

        # =================================================
        # INSERT RESULT
        # =================================================

        cur.execute("""

            INSERT INTO test_results
            (
                uid_id,
                station_id,
                resistance,
                continuity,
                actuator,
                result,
                line
            )

            VALUES
            (
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

            uid_data["uid_id"],

            "3",

            resistance,

            continuity,

            actuator,

            result,

            uid_data["line"]

        ))

        electrical_data = cur.fetchone()

        # =================================================
        # UPDATE STATION
        # =================================================

        cur.execute("""

            UPDATE uid_master

            SET current_station='COMPLETED'

            WHERE uid_id=%s

        """, (

            uid_data["uid_id"],

        ))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({

            "message":
            "Electrical Saved",

            "resistance":
            electrical_data["resistance"],

            "continuity":
            electrical_data["continuity"],

            "actuator":
            electrical_data["actuator"],

            "result":
            electrical_data["result"]

        })

    except Exception as e:

     if 'conn' in locals():
        conn.rollback()

    return jsonify({
        "error": str(e)
    }), 500