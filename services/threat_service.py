import ipaddress
import re
from urllib.parse import urlparse


def analyze_ip(ip):
    """
    Basic IP analysis.
    """

    try:
        ip_obj = ipaddress.ip_address(ip)

        result = {
            "type": "IP",
            "value": ip,
            "valid": True,
            "is_private": ip_obj.is_private,
            "is_global": ip_obj.is_global,
            "risk_score": 0,
            "severity": "LOW",
            "reasons": []
        }

        # Private IP
        if ip_obj.is_private:
            result["reasons"].append(
                "Private IP address"
            )

        # Public IP
        if ip_obj.is_global:
            result["reasons"].append(
                "Public IP address"
            )

        return result

    except ValueError:

        return {
            "type": "IP",
            "value": ip,
            "valid": False,
            "risk_score": 100,
            "severity": "INVALID",
            "reasons": [
                "Invalid IP address"
            ]
        }


def analyze_url(url):
    """
    Basic URL analysis.
    """

    parsed = urlparse(url)

    result = {
        "type": "URL",
        "value": url,
        "valid": False,
        "risk_score": 0,
        "severity": "LOW",
        "reasons": []
    }

    # Check protocol
    if parsed.scheme not in ["http", "https"]:
        result["reasons"].append(
            "Invalid URL protocol"
        )
        result["risk_score"] += 30

    # Check domain
    if not parsed.netloc:
        result["reasons"].append(
            "No valid domain found"
        )
        result["risk_score"] += 50

    else:
        result["valid"] = True

    # HTTP instead of HTTPS
    if parsed.scheme == "http":
        result["risk_score"] += 20

        result["reasons"].append(
            "Website does not use HTTPS"
        )

    # Suspicious URL patterns
    suspicious_words = [
        "login",
        "verify",
        "account",
        "password",
        "update",
        "free"
    ]

    for word in suspicious_words:

        if word in url.lower():

            result["risk_score"] += 10

            result["reasons"].append(
                f"Suspicious keyword: {word}"
            )

    # Limit score
    result["risk_score"] = min(
        result["risk_score"],
        100
    )

    # Determine severity
    if result["risk_score"] >= 80:
        result["severity"] = "CRITICAL"

    elif result["risk_score"] >= 60:
        result["severity"] = "HIGH"

    elif result["risk_score"] >= 30:
        result["severity"] = "MEDIUM"

    else:
        result["severity"] = "LOW"

    return result


def analyze_indicator(indicator):

    indicator = indicator.strip()

    # Detect IP
    try:
        ipaddress.ip_address(indicator)

        return analyze_ip(indicator)

    except ValueError:
        pass

    # Detect URL
    if re.match(r"^https?://", indicator, re.IGNORECASE):

        return analyze_url(indicator)

    return {
        "type": "UNKNOWN",
        "value": indicator,
        "valid": False,
        "risk_score": 0,
        "severity": "UNKNOWN",
        "reasons": [
            "Input is not a valid IP address or URL"
        ]
    }