from config.connection import get_db
from bson import BSON


def get_document_bson_size(document):
    """
    Calculate the BSON size of a MongoDB document.
    """

    encoded_document = BSON.encode(document)

    return len(encoded_document)


def get_all_document_sizes():
    """
    Calculate BSON size for every blog post.
    """

    db = get_db("nosql_labs")
    collection = db["blog_posts"]

    results = []

    for post in collection.find():

        size = get_document_bson_size(post)

        results.append({
            "title": post.get(
                "title",
                "Untitled"
            ),

            "comments": len(
                post.get(
                    "comments",
                    []
                )
            ),

            "bson_size": size
        })

    return results


def calculate_size_statistics():
    """
    Calculate average, minimum and maximum BSON size.
    """

    documents = get_all_document_sizes()

    if not documents:

        return {
            "average": 0,
            "minimum": 0,
            "maximum": 0
        }

    sizes = [
        document["bson_size"]
        for document in documents
    ]

    return {
        "average": sum(sizes) / len(sizes),
        "minimum": min(sizes),
        "maximum": max(sizes)
    }