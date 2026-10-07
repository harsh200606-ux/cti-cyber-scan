"""Lab 7.1 - Analyze a Production Schema

Embed vs reference analysis with BSON document size.
"""

import sys
import os

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from config.connection import get_db, reset_collection, banner
from bson import BSON
from rich.table import Table
from rich.console import Console


console = Console()


BLOG_POSTS = [
    {
        "title": "Getting Started with MongoDB",
        "author": "arjun",
        "slug": "getting-started-mongodb",
        "tags": ["mongodb", "nosql", "beginner"],
        "comments": [
            {
                "author": "reader1",
                "text": "Great intro!",
                "created": "2024-01-16"
            },
            {
                "author": "reader2",
                "text": "More on aggregation please",
                "created": "2024-01-17"
            }
        ]
    },

    {
        "title": "Advanced Aggregation Pipelines",
        "author": "sneha",
        "slug": "advanced-aggregation",
        "tags": ["mongodb", "aggregation", "intermediate"],
        "comments": [
            {
                "author": "reader1",
                "text": "$facet is amazing",
                "created": "2024-02-01"
            },
            {
                "author": "reader3",
                "text": "Very well explained",
                "created": "2024-02-02"
            },
            {
                "author": "reader4",
                "text": "Bookmarking this",
                "created": "2024-02-03"
            }
        ]
    },

    {
        "title": "Vector Search with MongoDB Atlas",
        "author": "kavya",
        "slug": "vector-search-atlas",
        "tags": [
            "mongodb",
            "ai",
            "vector-search",
            "advanced"
        ],
        "comments": [
            {
                "author": "reader5",
                "text": "When is IVF better than HNSW?",
                "created": "2024-03-01"
            }
        ]
    }
]


def get_bson_size(document):
    """
    Calculate the BSON size of a MongoDB document.
    Uses PyMongo BSON encoding instead of the
    unsupported MongoDB bsonsize command.
    """
    return len(BSON.encode(document))


def main():

    banner("Lab 7.1: Analyze a Production Schema")

    # Connect to database
    db = get_db("nosql_labs")

    # Reset and recreate blog_posts collection
    col = reset_collection(
        "nosql_labs",
        "blog_posts"
    )

    # Insert sample CTI/blog documents
    col.insert_many(BLOG_POSTS)

    # ---------------------------------------------------------
    # DOCUMENT SIZE ANALYSIS
    # ---------------------------------------------------------

    print("=== Document Size Analysis (BSON) ===")

    table = Table(
        title="Blog Post Document Sizes"
    )

    table.add_column(
        "Post",
        style="cyan",
        width=35
    )

    table.add_column(
        "Comments",
        justify="right"
    )

    table.add_column(
        "BSON Size (bytes)",
        justify="right"
    )

    table.add_column(
        "Pattern",
        style="green"
    )

    for post in col.find():

        # Calculate BSON size locally
        size = get_bson_size(post)

        comment_count = len(
            post.get("comments", [])
        )

        pattern = (
            "Embedded comments"
            if comment_count <= 5
            else "Consider referencing"
        )

        table.add_row(
            post["title"][:35],
            str(comment_count),
            str(size),
            pattern
        )

    console.print(table)

    # ---------------------------------------------------------
    # EMBED VS REFERENCE ANALYSIS
    # ---------------------------------------------------------

    print("\n=== Embed vs Reference Pattern Analysis ===")

    comment_counts = [
        len(post["comments"])
        for post in BLOG_POSTS
    ]

    average_comments = (
        sum(comment_counts)
        / len(comment_counts)
    )

    print(
        f"  Average comments per post: "
        f"{average_comments:.1f}"
    )

    print(
        f"  Max comments: "
        f"{max(comment_counts)}"
    )

    print(
        f"  Min comments: "
        f"{min(comment_counts)}"
    )

    print()

    print("  Recommendation:")

    print(
        "  - Comments < 100 per post "
        "-> EMBED "
        "(fewer queries, faster reads)"
    )

    print(
        "  - Comments > 100 per post "
        "-> REFERENCE "
        "(avoid 16MB document limit)"
    )

    print(
        "  - Comments > 1000 per post "
        "-> PAGINATED REFERENCE "
        "(bucket pattern)"
    )

    # ---------------------------------------------------------
    # LARGE DOCUMENT GROWTH SIMULATION
    # ---------------------------------------------------------

    print("\n=== Simulating Large Document Growth ===")

    big_post = {
        "title": "Popular Post",
        "author": "celebrity"
    }

    # 100 comments
    big_post["comments"] = [
        {
            "author": f"user{i}",
            "text": f"Comment number {i}"
        }
        for i in range(100)
    ]

    size_100 = get_bson_size(big_post)

    print(
        f"  100 comments      -> "
        f"{size_100:>8} bytes"
    )

    # 1,000 comments
    big_post["comments"] = [
        {
            "author": f"user{i}",
            "text": f"Comment number {i}"
        }
        for i in range(1000)
    ]

    size_1k = get_bson_size(big_post)

    print(
        f"  1,000 comments    -> "
        f"{size_1k:>8} bytes"
    )

    # 10,000 comments
    big_post["comments"] = [
        {
            "author": f"user{i}",
            "text": f"Comment number {i}"
        }
        for i in range(10000)
    ]

    size_10k = get_bson_size(big_post)

    print(
        f"  10,000 comments   -> "
        f"{size_10k:>8,} bytes"
    )

    # MongoDB document size limit
    max_document_size = 16 * 1024 * 1024

    print(
        f"  16 MB limit       -> "
        f"{max_document_size:>8,} bytes"
    )

    if size_10k > max_document_size:

        print(
            "  [WARN] 10K comments "
            "EXCEEDS 16MB limit!"
        )

    else:

        print(
            "  [OK] 10K comments "
            "is still below the 16MB limit."
        )

    # ---------------------------------------------------------
    # COMPLETE
    # ---------------------------------------------------------

    banner("Lab 7.1 Complete")


if __name__ == "__main__":
    main()