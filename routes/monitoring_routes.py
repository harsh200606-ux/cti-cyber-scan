from flask import Blueprint, jsonify

from config.connection import check_connection

from services.monitoring_service import (
    get_wiredtiger_cache_metrics
)


monitoring_bp = Blueprint(
    "monitoring",
    __name__,
    url_prefix="/api"
)


@monitoring_bp.route("/status", methods=["GET"])
def status():
    """
    Check whether MongoDB is reachable.
    """

    connection = check_connection()

    return jsonify(connection)


@monitoring_bp.route("/monitoring", methods=["GET"])
def monitoring():
    """
    Return current WiredTiger cache metrics.
    """

    try:

        metrics = get_wiredtiger_cache_metrics()

        return jsonify({
            "success": True,
            "metrics": metrics
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500