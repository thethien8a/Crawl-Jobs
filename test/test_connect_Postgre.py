import os

import psycopg2
from dotenv import load_dotenv
from psycopg2 import Error

load_dotenv()


def connect_to_postgres():
    """Kết nối đến PostgreSQL database"""
    try:
        # Lấy thông số kết nối từ environment variables
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        dbname = os.getenv("POSTGRES_DB", "job_database")
        user = os.getenv("POSTGRES_USER", "scrapy_user")
        password = os.getenv("POSTGRES_PASSWORD", "scrapy_password")

        connection = psycopg2.connect(
            host=host, port=port, database=dbname, user=user, password=password
        )

        cursor = connection.cursor()
        print("Kết nối PostgreSQL thành công!")
        return connection, cursor

    except (Exception, Error) as error:
        print(f"Lỗi kết nối PostgreSQL: {error}")
        return None, None


def close_connection(connection, cursor):
    """Đóng kết nối và cursor"""
    if cursor:
        cursor.close()
    if connection:
        connection.close()
    print("Kết nối PostgreSQL đã đóng.")


if __name__ == "__main__":
    conn, cur = connect_to_postgres()
    if conn:
        cur.execute("SELECT COUNT(*) FROM jobs;")
        count = cur.fetchone()[0]
        print(f"Số lượng bảng jobs: {count}")
        conn.commit()
        close_connection(conn, cur)
    else:
        print("Không thể kết nối đến database.")
