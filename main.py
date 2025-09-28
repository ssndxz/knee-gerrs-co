import psycopg2
import csv
import os

DB_NAME = "dataviz"
DB_USER = "postgres"
DB_PASS = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"

OUTPUT_DIR = "query_results"


def load_queries(file_path="queries.sql"):
    """Load queries from a .sql file, split by semicolon."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    queries = [q.strip() for q in content.split(";") if q.strip()]
    return queries


def save_to_csv(filename, headers, rows):
    """Save query results to CSV file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if headers:
            writer.writerow(headers)
        writer.writerows(rows)
    print(f"Results saved to {path}")


def main():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()

        queries = load_queries("queries.sql")
        for i, q in enumerate(queries, start=1):
            print(f"\n--- Query {i} ---")
            print(q)
            try:
                cur.execute(q)
                rows = cur.fetchall()
                headers = [desc[0] for desc in cur.description]
                for row in rows:
                    print(row)

                save_to_csv(f"query_{i}.csv", headers, rows)

            except Exception as e:
                print("Error executing query:", e)
                conn.rollback()
        cur.close()
        conn.close()
    except Exception as e:
        print("Database connection error:", e)

if __name__ == "__main__":
    main()