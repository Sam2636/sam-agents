import re

FORBIDDEN = ["DROP", "DELETE", "UPDATE", "TRUNCATE", "ALTER"]

def rewrite_sql(query: str) -> str:
    query = (query or "").strip()
    upper = query.upper()

    for keyword in FORBIDDEN:
        if keyword in upper:
            raise Exception(f"Forbidden SQL operation detected: {keyword}")

    if "LIMIT" not in upper:
        # Add LIMIT safely before a trailing semicolon if present.
        if query.endswith(";"):
            query = query[:-1].rstrip() + "\nLIMIT 100;"
        else:
            query += "\nLIMIT 100;"

    return query
