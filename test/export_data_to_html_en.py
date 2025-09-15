import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def test_connection_postgre():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def get_column_names(cursor):
    """Get column names from cursor description"""
    return [desc[0] for desc in cursor.description]

def get_data_from_postgre(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs LIMIT 10")
        rows = cursor.fetchall()
        column_names = get_column_names(cursor)
        
        # Filter out unwanted columns
        columns_to_exclude = ['job_description', 'requirements', 'benefits']
        filtered_column_indices = []
        filtered_column_names = []
        
        for i, col_name in enumerate(column_names):
            if col_name not in columns_to_exclude:
                filtered_column_indices.append(i)
                filtered_column_names.append(col_name)
        
        # Filter rows data by selected columns
        filtered_rows = []
        for row in rows:
            filtered_row = [row[i] for i in filtered_column_indices]
            filtered_rows.append(filtered_row)
        
        return filtered_rows, filtered_column_names
    
    except psycopg2.Error as e:
        print(f"Error getting data from PostgreSQL: {e}")
        return None, None

def generate_html_table(rows, column_names, output_file='job_data.html'):
    """Generate HTML file with styled table"""
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Data Display</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 100%;
            overflow-x: auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 800px;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
            max-width: 200px;
        }
        th {
            background-color: #4CAF50;
            color: white;
            position: sticky;
            top: 0;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .scroll-note {
            text-align: center;
            color: #666;
            font-style: italic;
            margin-top: 10px;
        }
        .no-data {
            text-align: center;
            color: #999;
            font-style: italic;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Job Data from Database</h1>
'''
    
    if not rows or not column_names:
        html_template += '<div class="no-data">No data to display.</div>'
    else:
        html_template += '''<table id="jobTable">
            <thead>
                <tr id="tableHeader">
'''
        # Add headers
        for col_name in column_names:
            html_template += f'                    <th>{col_name}</th>\n'
        
        html_template += '''                </tr>
            </thead>
            <tbody id="tableBody">
'''
        
        # Add rows
        for row in rows:
            html_template += '                <tr>\n'
            for cell in row:
                # Handle None values
                cell_value = str(cell) if cell is not None else ''
                # Escape HTML special characters
                cell_value = cell_value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                html_template += f'                    <td title="{cell_value}">{cell_value}</td>\n'
            html_template += '                </tr>\n'
        
        html_template += '''            </tbody>
        </table>
'''

    html_template += '''        <p class="scroll-note">You can scroll horizontally to see all columns</p>
    </div>
</body>
</html>'''
    
    # Write to file with UTF-8 encoding
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"Created HTML file: {output_file}")
    return output_file

def main():
    conn = test_connection_postgre()
    if conn:
        rows, column_names = get_data_from_postgre(conn)
        if rows is not None and column_names is not None:
            output_file = generate_html_table(rows, column_names, 'display_data_dynamic.html')
            print(f"Data has been exported to {output_file}")
        else:
            print("Failed to get data from PostgreSQL.")
    else:
        print("Failed to connect to PostgreSQL.")

if __name__ == "__main__":
    main()