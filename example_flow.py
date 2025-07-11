#!/usr/bin/env python3
"""
Example CocoIndex Flow for Standalone Executable Testing
This is a simple flow that processes text files and creates embeddings.
"""

import cocoindex
import os
from pathlib import Path

# Set up some basic environment variables if not already set
if not os.environ.get("COCOINDEX_DATABASE_URL"):
    os.environ["COCOINDEX_DATABASE_URL"] = (
        "postgres://cocoindex:cocoindex@localhost/cocoindex"
    )


@cocoindex.flow_def(name="ExampleTextEmbedding")
def example_text_embedding_flow(
    flow_builder: cocoindex.FlowBuilder, data_scope: cocoindex.DataScope
):
    """
    Example flow that processes text files and creates embeddings.

    This flow:
    1. Watches for text files in the specified directory
    2. Splits them into chunks
    3. Creates embeddings for each chunk
    4. Stores them in PostgreSQL with vector search capability
    """

    # Add a data source to read text files from a directory
    # The standalone executable will watch this directory for changes
    data_scope["documents"] = flow_builder.add_source(
        cocoindex.sources.LocalFile(
            path="./watched_data",  # This will be the directory we watch
            glob_pattern="*.txt",  # Only process .txt files
            recursive=True,  # Include subdirectories
        )
    )

    # Add a collector for data to be exported to the vector index
    doc_embeddings = data_scope.add_collector()

    # Transform data of each document
    with data_scope["documents"].row() as doc:
        # Split the document into chunks
        doc["chunks"] = doc["content"].transform(
            cocoindex.functions.SplitRecursively(),
            language="text",
            chunk_size=1000,
            chunk_overlap=200,
        )

        # Transform data of each chunk
        with doc["chunks"].row() as chunk:
            # Create embeddings for each chunk
            # Using a simple sentence transformer model
            chunk["embedding"] = chunk["text"].transform(
                cocoindex.functions.SentenceTransformerEmbed(
                    model="sentence-transformers/all-MiniLM-L6-v2"
                )
            )

            # Collect the chunk data
            doc_embeddings.collect(
                filename=doc["filename"],
                file_path=doc["file_path"],
                location=chunk["location"],
                text=chunk["text"],
                embedding=chunk["embedding"],
                chunk_size=chunk["size"],
            )

    # Export collected data to PostgreSQL with vector search
    doc_embeddings.export(
        "example_embeddings",
        cocoindex.targets.Postgres(),
        primary_key_fields=["filename", "location"],
        vector_indexes=[
            cocoindex.VectorIndexDef(
                field_name="embedding",
                metric=cocoindex.VectorSimilarityMetric.COSINE_SIMILARITY,
            )
        ],
    )


def create_test_data():
    """Create some test data for demonstration."""
    test_dir = Path("./watched_data")
    test_dir.mkdir(exist_ok=True)

    # Create some sample text files
    sample_files = {
        "document1.txt": """
        This is the first document. It contains information about artificial intelligence
        and machine learning. AI is transforming various industries including healthcare,
        finance, and transportation. Machine learning algorithms can learn from data
        and make predictions or decisions.
        """,
        "document2.txt": """
        The second document discusses natural language processing. NLP is a branch of
        artificial intelligence that focuses on the interaction between computers and
        human language. It includes tasks like text analysis, sentiment analysis,
        and machine translation.
        """,
        "document3.txt": """
        This document is about computer vision. Computer vision is another important
        field in AI that enables machines to interpret and understand visual information.
        It has applications in autonomous vehicles, medical imaging, and robotics.
        """,
    }

    for filename, content in sample_files.items():
        file_path = test_dir / filename
        if not file_path.exists():
            file_path.write_text(content.strip())
            print(f"Created test file: {file_path}")


def query_example():
    """Example of how to query the indexed data."""
    import psycopg2
    from pgvector.psycopg2 import register_vector

    try:
        # Connect to the database
        conn = psycopg2.connect(
            host="localhost",
            database="cocoindex",
            user="cocoindex",
            password="cocoindex",
        )
        register_vector(conn)

        cur = conn.cursor()

        # Query for documents similar to a search term
        search_query = "machine learning algorithms"

        # This is a simplified query - in practice you'd want to embed the search query
        # and use vector similarity search
        cur.execute(
            """
            SELECT filename, text, chunk_size
            FROM example_embeddings
            WHERE text ILIKE %s
            ORDER BY filename, location
            LIMIT 5
        """,
            (f"%{search_query}%",),
        )

        results = cur.fetchall()

        print(f"\nSearch results for '{search_query}':")
        print("-" * 50)

        for filename, text, chunk_size in results:
            print(f"File: {filename}")
            print(f"Text: {text[:100]}...")
            print(f"Chunk size: {chunk_size}")
            print("-" * 30)

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Query failed: {e}")
        print("Make sure PostgreSQL is running and the data has been indexed.")


def main():
    """Main function for testing the flow."""
    print("CocoIndex Example Flow")
    print("=" * 30)

    # Create test data
    create_test_data()

    print("\nTest data created in ./watched_data/")
    print("You can now use the standalone executable to watch this directory:")
    print("  ./cocoindex-watcher ./watched_data ./example_flow.py")
    print("\nOr run the indexing manually:")
    print("  cocoindex update ./example_flow.py")

    # Ask if user wants to run a query example
    try:
        response = input("\nWould you like to run a query example? (y/n): ").lower()
        if response == "y":
            query_example()
    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
