from flask import Flask
from flask_cors import CORS

from routes.component_routes import comp_bp
from routes.scan_routes import scan_bp
#from routes.uid_routes import uid_bp
from routes.production_routes import production_bp
#from routes.test_routes import test_bp
#from routes.dashboard_routes import dash_bp
from routes.trace_routes import trace_bp
from routes.records_routes import records_bp
from routes.productionlineB_routes import line_b_bp
from routes.productionlineC_routes import line_c_bp
from routes.productionlineD_routes import line_d_bp
from routes.final_serial_routes import final_serial_bp
from routes.dashboard_routes import dashboard_bp


app = Flask(__name__)
CORS(app)

app.register_blueprint(comp_bp)
app.register_blueprint(scan_bp)
app.register_blueprint(records_bp)
#app.register_blueprint(uid_bp)
app.register_blueprint(production_bp)
#app.register_blueprint(test_bp)
#app.register_blueprint(dash_bp)
app.register_blueprint(trace_bp)
app.register_blueprint(line_b_bp)
app.register_blueprint(line_c_bp)
app.register_blueprint(line_d_bp)
app.register_blueprint(final_serial_bp)
app.register_blueprint(dashboard_bp)


@app.route("/")
def home():
    return "Traceability System Running"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        threaded=True
    )