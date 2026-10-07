from config.connection import get_db


def get_wiredtiger_cache_metrics():
    """
    Get WiredTiger cache metrics from MongoDB serverStatus().
    """

    db = get_db("nosql_labs")

    status = db.command("serverStatus")

    wired_tiger = status.get(
        "wiredTiger",
        {}
    )

    cache = wired_tiger.get(
        "cache",
        {}
    )

    return {
        "cache_maximum_bytes": cache.get(
            "maximum bytes configured"
        ),

        "cache_bytes_in_use": cache.get(
            "bytes currently in the cache"
        ),

        "dirty_bytes": cache.get(
            "tracked dirty bytes in the cache"
        ),

        "pages_evicted": cache.get(
            "eviction pages evicted by application threads",
            0
        ),

        "pages_read": cache.get(
            "pages read into cache",
            0
        )
    }


def get_cache_metrics_with_approximation():
    """
    Return raw WiredTiger metrics plus the
    approximate calculation used in the original lab.

    IMPORTANT:
    This is NOT a standard MongoDB cache-hit ratio.
    """

    metrics = get_wiredtiger_cache_metrics()

    pages_read = metrics["pages_read"]
    pages_evicted = metrics["pages_evicted"]

    if pages_read and pages_read > 0:

        approximate_ratio = max(
            0,
            1 - (pages_evicted / pages_read)
        )

    else:
        approximate_ratio = None

    metrics["approximate_cache_ratio"] = approximate_ratio

    return metrics