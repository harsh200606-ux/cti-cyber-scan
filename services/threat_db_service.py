from datetime import datetime
from config.connection import get_db


COLLECTION_NAME = "threat_analysis"


# --------------------------------------------------
# Get Threat Collection
# --------------------------------------------------

def get_threat_collection():

    db = get_db()

    return db[COLLECTION_NAME]


# --------------------------------------------------
# Merge Two Documents
# --------------------------------------------------

def merge_documents(old_document, new_document):

    merged = old_document.copy()

    # --------------------------------------------------
    # Fields where the newest VirusTotal result
    # should always be used
    # --------------------------------------------------

    latest_fields = [
        "malicious",
        "suspicious",
        "harmless",
        "undetected",
        "reputation",
        "threat_level"
    ]

    # --------------------------------------------------
    # Merge missing information
    # --------------------------------------------------

    for key, new_value in new_document.items():

        # Never copy MongoDB internal ID
        if key == "_id":
            continue

        # If old value is missing, use new value
        if (
            key not in merged
            or merged[key] is None
            or merged[key] == ""
            or merged[key] == "-"
        ):

            if (
                new_value is not None
                and new_value != ""
            ):

                merged[key] = new_value

    # --------------------------------------------------
    # Update latest threat intelligence information
    # --------------------------------------------------

    for key in latest_fields:

        if key in new_document:

            new_value = new_document[key]

            if new_value is not None:

                merged[key] = new_value

    # --------------------------------------------------
    # Update timestamp
    # --------------------------------------------------

    merged["updated_at"] = datetime.utcnow()

    return merged


# --------------------------------------------------
# Save / Merge Threat Result
# --------------------------------------------------

def save_threat_result(result):

    collection = get_threat_collection()

    # --------------------------------------------------
    # Determine indicator
    # --------------------------------------------------

    indicator_type = result.get("type")

    if indicator_type == "IP":

        indicator = result.get("ip")

    else:

        indicator = result.get("url")

    # --------------------------------------------------
    # Validate indicator
    # --------------------------------------------------

    if not indicator:

        return None

    # --------------------------------------------------
    # Build IP document
    # --------------------------------------------------

    if indicator_type == "IP":

        new_document = {

            "indicator": indicator,

            "type": "IP",

            "country": result.get(
                "country"
            ),

            "continent": result.get(
                "continent"
            ),

            "as_owner": result.get(
                "as_owner"
            ),

            "asn": result.get(
                "asn"
            ),

            "reputation": result.get(
                "reputation"
            ),

            "malicious": result.get(
                "malicious",
                0
            ),

            "suspicious": result.get(
                "suspicious",
                0
            ),

            "harmless": result.get(
                "harmless",
                0
            ),

            "undetected": result.get(
                "undetected",
                0
            ),

            "threat_level": result.get(
                "threat_level"
            ),

            "updated_at": datetime.utcnow()
        }

    # --------------------------------------------------
    # Build URL document
    # --------------------------------------------------

    else:

        new_document = {

            "indicator": indicator,

            "type": "URL",

            "title": result.get(
                "title"
            ),

            "last_final_url": result.get(
                "last_final_url"
            ),

            "reputation": result.get(
                "reputation"
            ),

            "malicious": result.get(
                "malicious",
                0
            ),

            "suspicious": result.get(
                "suspicious",
                0
            ),

            "harmless": result.get(
                "harmless",
                0
            ),

            "undetected": result.get(
                "undetected",
                0
            ),

            "threat_level": result.get(
                "threat_level"
            ),

            "updated_at": datetime.utcnow()
        }

    # --------------------------------------------------
    # Check if indicator already exists
    # --------------------------------------------------

    existing = collection.find_one(
        {
            "indicator": indicator
        }
    )

    # --------------------------------------------------
    # If indicator does not exist
    # insert a new document
    # --------------------------------------------------

    if not existing:

        new_document["created_at"] = datetime.utcnow()

        inserted = collection.insert_one(
            new_document
        )

        return str(
            inserted.inserted_id
        )

    # --------------------------------------------------
    # Indicator already exists
    # Merge old and new data
    # --------------------------------------------------

    merged_document = merge_documents(
        existing,
        new_document
    )

    # --------------------------------------------------
    # Preserve original creation time
    # --------------------------------------------------

    if "created_at" in existing:

        merged_document["created_at"] = (
            existing["created_at"]
        )

    else:

        merged_document["created_at"] = (
            datetime.utcnow()
        )

    # --------------------------------------------------
    # Replace old document with merged document
    # --------------------------------------------------

    collection.replace_one(
        {
            "_id": existing["_id"]
        },
        merged_document
    )

    return str(
        existing["_id"]
    )


# --------------------------------------------------
# Find Threat Result
# --------------------------------------------------

def find_threat_result(indicator):

    collection = get_threat_collection()

    return collection.find_one(
        {
            "indicator": indicator
        },
        {
            "_id": 0
        }
    )