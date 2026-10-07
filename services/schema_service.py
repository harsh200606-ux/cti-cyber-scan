from config.connection import get_db


def get_blog_posts():
    """
    Get all blog/threat-intelligence documents
    from the blog_posts collection.
    """

    db = get_db("nosql_labs")

    collection = db["blog_posts"]

    posts = list(collection.find({}, {"_id": 0}))

    return posts


def get_blog_post_count():
    """
    Return the number of documents in blog_posts.
    """

    db = get_db("nosql_labs")

    collection = db["blog_posts"]

    return collection.count_documents({})


def get_comment_statistics():
    """
    Calculate basic comment statistics
    for the embedded comments.
    """

    posts = get_blog_posts()

    if not posts:
        return {
            "average_comments": 0,
            "minimum_comments": 0,
            "maximum_comments": 0
        }

    comment_counts = [
        len(post.get("comments", []))
        for post in posts
    ]

    return {
        "average_comments": sum(comment_counts) / len(comment_counts),
        "minimum_comments": min(comment_counts),
        "maximum_comments": max(comment_counts)
    }