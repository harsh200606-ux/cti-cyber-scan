from flask import Blueprint, jsonify

from services.working_set_service import (
    insert_working_set,
    run_standard_range_queries
)

from services.monitoring_service import (
    get_cache_metrics_with_approximation
)


lab7_2_bp = Blueprint(
    "lab7_2",
    __name__,
    url_prefix="/api/lab7.2"
)


@lab7_2_bp.route("/insert", methods=["POST"])
def insert_documents():
    """
    Insert the 100,000 working-set documents.
    """

    try:

        result = insert_working_set(
            count=100000
        )

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@lab7_2_bp.route("/query-test", methods=["POST"])
def query_test():
    """
    Run the three working-set range queries.
    """

    try:

        results = run_standard_range_queries()

        return jsonify({
            "success": True,
            "results": results
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@lab7_2_bp.route("/cache", methods=["GET"])
def cache_metrics():
    """
    Return WiredTiger cache metrics.
    """

    try:

        metrics = get_cache_metrics_with_approximation()

        return jsonify({
            "success": True,
            "metrics": metrics
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500