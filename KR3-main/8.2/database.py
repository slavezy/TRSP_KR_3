import sqlite3

DATABASE = "todos.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT,
            completed   INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("Table 'todos' created successfully.")
