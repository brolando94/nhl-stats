def insert_list_of_dicts(conn, table_name, data):
    """Inserts a list of dictionaries into a SQLite database table."""

    cursor = conn.cursor()

    # Get the column names from the first dictionary
    columns = data[0].keys()

    # Construct the SQL query
    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in columns])})"

    # Insert the data
    for row in data:
        values = [row[col] for col in columns]
        cursor.execute(query, values)

    conn.commit()