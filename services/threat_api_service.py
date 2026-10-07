import os
import requests
import base64

from dotenv import load_dotenv

load_dotenv()

VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

BASE_URL = "https://www.virustotal.com/api/v3"


def get_headers():
    return {
        "x-apikey": VIRUSTOTAL_API_KEY
    }


# --------------------------------------------------
# Threat Level Calculation
# --------------------------------------------------

def calculate_threat_level(malicious, suspicious):

    if malicious >= 5:
        return "CRITICAL"

    elif malicious >= 2:
        return "HIGH"

    elif malicious == 1:
        return "MEDIUM"

    elif suspicious >= 3:
        return "HIGH"

    elif suspicious >= 1:
        return "MEDIUM"

    else:
        return "LOW"


# --------------------------------------------------
# IP Address Analysis
# --------------------------------------------------

def analyze_ip_with_virustotal(ip):

    url = f"{BASE_URL}/ip_addresses/{ip}"

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=15
    )

    if response.status_code != 200:

        return {
            "success": False,
            "error": response.text
        }

    data = response.json()

    attributes = data.get(
        "data", {}
    ).get(
        "attributes", {}
    )

    analysis_stats = attributes.get(
        "last_analysis_stats",
        {}
    )

    malicious = analysis_stats.get("malicious", 0)
    suspicious = analysis_stats.get("suspicious", 0)
    harmless = analysis_stats.get("harmless", 0)
    undetected = analysis_stats.get("undetected", 0)

    threat_level = calculate_threat_level(
        malicious,
        suspicious
    )

    return {

        "success": True,

        "type": "IP",

        "ip": ip,

        "country": attributes.get("country"),

        "continent": attributes.get("continent"),

        "as_owner": attributes.get("as_owner"),

        "asn": attributes.get("asn"),

        "reputation": attributes.get("reputation"),

        "malicious": malicious,

        "suspicious": suspicious,

        "harmless": harmless,

        "undetected": undetected,

        "threat_level": threat_level
    }


# --------------------------------------------------
# URL Analysis
# --------------------------------------------------

def analyze_url_with_virustotal(url):

    # VirusTotal uses a URL-safe Base64 encoded URL ID
    url_id = base64.urlsafe_b64encode(
        url.encode()
    ).decode().strip("=")

    api_url = f"{BASE_URL}/urls/{url_id}"

    response = requests.get(
        api_url,
        headers=get_headers(),
        timeout=15
    )

    if response.status_code != 200:

        return {
            "success": False,
            "error": response.text
        }

    data = response.json()

    attributes = data.get(
        "data", {}
    ).get(
        "attributes", {}
    )

    analysis_stats = attributes.get(
        "last_analysis_stats",
        {}
    )

    malicious = analysis_stats.get("malicious", 0)
    suspicious = analysis_stats.get("suspicious", 0)
    harmless = analysis_stats.get("harmless", 0)
    undetected = analysis_stats.get("undetected", 0)

    threat_level = calculate_threat_level(
        malicious,
        suspicious
    )

    return {

        "success": True,

        "type": "URL",

        "url": url,

        "title": attributes.get("title"),

        "last_final_url": attributes.get(
            "last_final_url"
        ),

        "reputation": attributes.get(
            "reputation"
        ),

        "malicious": malicious,

        "suspicious": suspicious,

        "harmless": harmless,

        "undetected": undetected,

        "threat_level": threat_level
    }