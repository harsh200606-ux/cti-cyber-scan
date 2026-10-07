import time

from config.connection import get_db


COLLECTION_NAME = "working_set_docs"


def get_collection():
    """
    Get the working_set_docs collection.
    """

    db = get_db("nosql_labs")

    return db[COLLECTION_NAME]


def insert_working_set(count=100000):
    """
    Insert test documents into MongoDB.

    Each document is approximately 2 KB,
    following the original Lab 7.2 experiment.
    """

    collection = get_collection()

    # Remove old test data before inserting new data
    collection.drop()

    documents = [
        {
            "sensor": f"S-{i:06d}",
            "reading": i * 0.01,
            "metadata": "x" * 1800
        }
        for i in range(count)
    ]

    start = time.perf_counter()

    collection.insert_many(
        documents,
        ordered=False
    )

    elapsed = time.perf_counter() - start

    documents_per_second = (
        count / elapsed
        if elapsed > 0
        else 0
    )

    return {
        "count": count,
        "elapsed_seconds": elapsed,
        "documents_per_second": documents_per_second
    }


def run_range_query(start_value, end_value):
    """
    Run a sensor range query and measure
    how long it takes.
    """

    collection = get_collection()

    start = time.perf_counter()

    results = list(
        collection.find(
            {
                "sensor": {
                    "$gte": f"S-{start_value:06d}",
                    "$lte": f"S-{end_value:06d}"
                }
            }
        )
    )

    elapsed = time.perf_counter() - start

    return {
        "start": start_value,
        "end": end_value,
        "documents_returned": len(results),
        "time_ms": elapsed * 1000
    }


def run_standard_range_queries():
    """
    Run the three range queries from Lab 7.2.
    """

    ranges = [
        (0, 1000),
        (49000, 50000),
        (99000, 100000)
    ]

    results = []

    for start_value, end_value in ranges:

        result = run_range_query(
            start_value,
            end_value
        )

        results.append(result)

    return results