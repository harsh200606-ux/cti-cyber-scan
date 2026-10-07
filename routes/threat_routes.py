from flask import Blueprint, render_template, request, jsonify

from services.threat_api_service import (
    analyze_ip_with_virustotal,
    analyze_url_with_virustotal
)

from services.threat_db_service import (
    find_threat_result,
    save_threat_result,
    get_threat_collection
)

import ipaddress
import re


# ==================================================
# BLUEPRINT
# ==================================================

threat_bp = Blueprint(
    "threat",
    __name__,
    url_prefix="/threat"
)


# ==================================================
# THREAT ANALYZER PAGE
# ==================================================

@threat_bp.route("/")
def threat_page():

    return render_template(
        "threat_analysis.html"
    )


# ==================================================
# THREAT HISTORY PAGE
# ==================================================

@threat_bp.route("/history")
def history_page():

    return render_template(
        "threat_history.html"
    )


# ==================================================
# ANALYZE THREAT
# ==================================================

@threat_bp.route(
    "/analyze",
    methods=["POST"]
)
def analyze_threat():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        indicator = data.get(
            "indicator",
            ""
        ).strip()


        # --------------------------------------------------
        # EMPTY INPUT
        # --------------------------------------------------

        if not indicator:

            return jsonify({

                "success": False,

                "error":
                    "Please enter an IP address or URL."

            }), 400


        # --------------------------------------------------
        # DETECT IP OR URL
        # --------------------------------------------------

        try:

            ip = str(
                ipaddress.ip_address(
                    indicator
                )
            )

            indicator_type = "IP"

        except ValueError:

            ip = None

            indicator_type = "URL"


        # --------------------------------------------------
        # VALIDATE URL
        # --------------------------------------------------

        if indicator_type == "URL":

            url_pattern = re.compile(
                r"^https?://.+",
                re.IGNORECASE
            )

            if not url_pattern.match(
                indicator
            ):

                return jsonify({

                    "success": False,

                    "error":
                        "Please enter a valid IP address "
                        "or URL starting with http:// or https://"

                }), 400


        # ==================================================
        # STEP 1: CHECK MONGODB
        # ==================================================

        stored_result = find_threat_result(
            indicator
        )


        # --------------------------------------------------
        # RESULT FOUND IN MONGODB
        # --------------------------------------------------

        if stored_result:

            malicious = stored_result.get(
                "malicious",
                0
            )

            suspicious = stored_result.get(
                "suspicious",
                0
            )


            # Calculate threat level if missing

            if not stored_result.get(
                "threat_level"
            ):

                if malicious >= 5:

                    stored_result[
                        "threat_level"
                    ] = "CRITICAL"

                elif malicious >= 2:

                    stored_result[
                        "threat_level"
                    ] = "HIGH"

                elif malicious == 1:

                    stored_result[
                        "threat_level"
                    ] = "MEDIUM"

                elif suspicious >= 3:

                    stored_result[
                        "threat_level"
                    ] = "HIGH"

                elif suspicious >= 1:

                    stored_result[
                        "threat_level"
                    ] = "MEDIUM"

                else:

                    stored_result[
                        "threat_level"
                    ] = "LOW"


            return jsonify({

                "success": True,

                "source": "mongodb",

                "result": stored_result

            })


        # ==================================================
        # STEP 2: VIRUSTOTAL ANALYSIS
        # ==================================================

        if indicator_type == "IP":

            result = analyze_ip_with_virustotal(
                ip
            )

        else:

            result = analyze_url_with_virustotal(
                indicator
            )


        # --------------------------------------------------
        # VIRUSTOTAL ERROR
        # --------------------------------------------------

        if not result.get(
            "success"
        ):

            return jsonify({

                "success": False,

                "error": result.get(
                    "error",
                    "VirusTotal request failed."
                )

            }), 502


        # ==================================================
        # STEP 3: SAVE RESULT TO MONGODB
        # ==================================================

        save_threat_result(
            result
        )


        # ==================================================
        # STEP 4: PREPARE FRONTEND RESULT
        # ==================================================

        if indicator_type == "IP":

            frontend_result = {

                "indicator":
                    result.get("ip"),

                "type":
                    "IP",

                "country":
                    result.get("country"),

                "continent":
                    result.get("continent"),

                "as_owner":
                    result.get("as_owner"),

                "asn":
                    result.get("asn"),

                "reputation":
                    result.get("reputation"),

                "malicious":
                    result.get(
                        "malicious",
                        0
                    ),

                "suspicious":
                    result.get(
                        "suspicious",
                        0
                    ),

                "harmless":
                    result.get(
                        "harmless",
                        0
                    ),

                "undetected":
                    result.get(
                        "undetected",
                        0
                    ),

                "threat_level":
                    result.get("threat_level")
            }

        else:

            frontend_result = {

                "indicator":
                    result.get("url"),

                "type":
                    "URL",

                "title":
                    result.get("title"),

                "last_final_url":
                    result.get(
                        "last_final_url"
                    ),

                "reputation":
                    result.get("reputation"),

                "malicious":
                    result.get(
                        "malicious",
                        0
                    ),

                "suspicious":
                    result.get(
                        "suspicious",
                        0
                    ),

                "harmless":
                    result.get(
                        "harmless",
                        0
                    ),

                "undetected":
                    result.get(
                        "undetected",
                        0
                    ),

                "threat_level":
                    result.get("threat_level")
            }


        # ==================================================
        # RETURN RESULT
        # ==================================================

        return jsonify({

            "success": True,

            "source": "virustotal",

            "result": frontend_result

        })


    except Exception as error:

        print(
            "Threat analysis error:",
            error
        )

        return jsonify({

            "success": False,

            "error":
                str(error)

        }), 500


# ==================================================
# THREAT HISTORY DATA
# ==================================================

@threat_bp.route(
    "/history/data",
    methods=["GET"]
)
def threat_history_data():

    try:

        collection = get_threat_collection()


        records = list(

            collection.find(

                {},

                {
                    "_id": 0
                }

            ).sort(

                "updated_at",
                -1

            )

        )


        return jsonify({

            "success": True,

            "count":
                len(records),

            "results":
                records

        })


    except Exception as error:

        print(
            "History error:",
            error
        )


        return jsonify({

            "success": False,

            "error":
                str(error)

        }), 500


# ==================================================
# THREAT DETAILS API
# ==================================================

@threat_bp.route(
    "/details/<path:indicator>",
    methods=["GET"]
)
def threat_details(indicator):

    try:

        # --------------------------------------------------
        # FIND THREAT RECORD
        # --------------------------------------------------

        result = find_threat_result(
            indicator
        )


        # --------------------------------------------------
        # RECORD NOT FOUND
        # --------------------------------------------------

        if not result:

            return jsonify({

                "success": False,

                "error":
                    "Threat analysis record not found."

            }), 404


        # --------------------------------------------------
        # RETURN COMPLETE RESULT
        # --------------------------------------------------

        return jsonify({

            "success": True,

            "result": result

        })


    except Exception as error:

        print(
            "Threat details error:",
            error
        )


        return jsonify({

            "success": False,

            "error":
                str(error)

        }), 500


# ==================================================
# THREAT DETAILS HTML PAGE
# ==================================================

@threat_bp.route(
    "/details/view/<path:indicator>",
    methods=["GET"]
)
def threat_details_page(indicator):

    try:

        # --------------------------------------------------
        # FIND RECORD IN MONGODB
        # --------------------------------------------------

        result = find_threat_result(
            indicator
        )


        # --------------------------------------------------
        # RECORD NOT FOUND
        # --------------------------------------------------

        if not result:

            return """

                <html>

                    <head>

                        <title>
                            Threat Not Found
                        </title>

                        <style>

                            body {
                                background: #0f1117;
                                color: white;
                                font-family: Arial;
                                padding: 50px;
                                text-align: center;
                            }

                            a {
                                color: #60a5fa;
                                text-decoration: none;
                            }

                        </style>

                    </head>

                    <body>

                        <h2>
                            Threat Record Not Found
                        </h2>

                        <p>
                            No analysis was found for:
                        </p>

                        <p>
                            <strong>
                                {}
                            </strong>
                        </p>

                        <br>

                        <a href="/threat/history">
                            ← Back to Threat History
                        </a>

                    </body>

                </html>

            """.format(
                indicator
            ), 404


        # --------------------------------------------------
        # OPEN DETAILS TEMPLATE
        # --------------------------------------------------

        return render_template(
            "threat_details.html",
            result=result
        )


    except Exception as error:

        print(
            "Threat details page error:",
            error
        )


        return """

            <html>

                <head>

                    <title>
                        Threat Details Error
                    </title>

                    <style>

                        body {
                            background: #0f1117;
                            color: white;
                            font-family: Arial;
                            padding: 50px;
                            text-align: center;
                        }

                        a {
                            color: #60a5fa;
                            text-decoration: none;
                        }

                    </style>

                </head>

                <body>

                    <h2>
                        Error Loading Threat Details
                    </h2>

                    <p>
                        {}
                    </p>

                    <br>

                    <a href="/threat/history">
                        ← Back to Threat History
                    </a>

                </body>

            </html>

        """.format(
            error
        ), 500