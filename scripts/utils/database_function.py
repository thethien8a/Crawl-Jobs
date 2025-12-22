
def sql_command(cursor, sql, params=None):
    cursor.execute(sql)
    cursor.connection.commit()
    return cursor.fetchall() if cursor.description else None