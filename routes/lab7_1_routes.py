from flask import Blueprint, jsonify, request

from services.schema_service import (
    get_blog_posts,
    get_blog_post_count,
    get_comment_statistics
)

from services.bson_service import (
    get_all_document_sizes,
    calculate_size_statistics
)

from bson import BSON


lab7_1_bp = Blueprint(
    "lab7_1",
    __name__,
    url_prefix="/api/lab7.1"
)


@lab7_1_bp.route("/data", methods=["GET"])
def get_data():
    """
    Return all blog/threat-intelligence documents
    stored in MongoDB.
    """

    try:
        posts = get_blog_posts()

        return jsonify({
            "success": True,
            "count": len(posts),
            "data": posts
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@lab7_1_bp.route("/analyze", methods=["POST"])
def analyze():
    """
    Perform BSON size and comment analysis.
    """

    try:
        documents = get_all_document_sizes()

        size_stats = calculate_size_statistics()

        comment_stats = get_comment_statistics()

        return jsonify({
            "success": True,

            "documents": documents,

            "size_statistics": size_stats,

            "comment_statistics": comment_stats,

            "document_limit": {
                "bytes": 16 * 1024 * 1024,
                "megabytes": 16
            }
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@lab7_1_bp.route("/simulate", methods=["POST"])
def simulate():
    """
    Simulate BSON document growth with
    100, 1,000 and 10,000 comments.
    """

    try:

        results = []

        comment_counts = [
            100,
            1000,
            10000
        ]

        for count in comment_counts:

            document = {
                "title": "Popular Post",
                "author": "celebrity",
                "comments": [
                    {
                        "author": f"user{i}",
                        "text": f"Comment number {i}"
                    }
                    for i in range(count)
                ]
            }

            # Calculate BSON size locally using PyMongo
            size = len(BSON.encode(document))

            exceeds_limit = (
                size > 16 * 1024 * 1024
            )

            results.append({
                "comments": count,
                "bson_size": size,
                "exceeds_16_mib": exceeds_limit
            })

        return jsonify({
            "success": True,
            "results": results,
            "document_limit_bytes": 16 * 1024 * 1024
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@lab7_1_bp.route("/count", methods=["GET"])
def count():

    try:

        total = get_blog_post_count()

        return jsonify({
            "success": True,
            "count": total
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500