from flask import Flask, render_template

from routes.threat_routes import threat_bp

from routes.lab7_1_routes import lab7_1_bp
from routes.lab7_2_routes import lab7_2_bp
from routes.monitoring_routes import monitoring_bp


app = Flask(__name__)


# Register API routes
app.register_blueprint(lab7_1_bp)
app.register_blueprint(lab7_2_bp)
app.register_blueprint(monitoring_bp)
app.register_blueprint(threat_bp)


# Home page
@app.route("/")
def index():
    return render_template("index.html")


# Lab 7.1 page
@app.route("/lab7.1")
def lab7_1_page():
    return render_template("lab7_1.html")


# Lab 7.2 page
@app.route("/lab7.2")
def lab7_2_page():
    return render_template("lab7_2.html")


# Monitoring page
@app.route("/monitoring")
def monitoring_page():
    return render_template("monitoring.html")


# Threat Analysis page
@app.route("/threat")
def threat_page():
    return render_template("threat_analysis.html")


if __name__ == "__main__":
    app.run(debug=True)