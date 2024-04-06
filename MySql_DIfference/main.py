import pymysql

def database_difference():

    detail1 = {"host":"hostlink1", "user":"username1", "password":"password1", "database":"databasename1","connect_timeout":5}
    detail2 = {"host":"hostlink2", "user":"username2", "password":"password2", "database":"databasename2","connect_timeout":5} 

    conn1 = pymysql.connect(**detail1)
    cursor1 = conn1.cursor()

    conn2 = pymysql.connect(**detail2)
    cursor2 = conn2.cursor()

    cursor1.execute("SHOW FULL TABLES")
    dbtables1 = set(cursor1.fetchall())

    cursor2.execute("SHOW FULL TABLES")
    dbtables2 = set(cursor2.fetchall())

    alltables = dbtables1.union(dbtables2)
    html = ""
    html += "<table id='example' class='display' style='width:100%'>"
    html += f"<thead><tr><th>Name</th><th>{detail1['database']}</th><th>{detail2['database']}</th></tr></thead><tbody>"

    for table in alltables:
        presence_count = [
            1 if table in dbtables1 else 0,
            1 if table in dbtables2 else 0
        ]
        if sum(presence_count) < 2:
            html += f'<tr><td><b>Table</b>  {table[0]}</td>'
            for count in presence_count:
                html += f'<td>{"present" if count == 1 else "absent"}</td>'
            html += "</tr>"

        elif sum(presence_count) == 2:
            cursor1.execute(f"DESCRIBE {detail1['database']}.{table[0]}")
            column_set1 = set(cursor1.fetchall())

            cursor2.execute(f"DESCRIBE {detail2['database']}.{table[0]}")
            column_set2 = set(cursor2.fetchall())

            column_set1_indexes = {t[0] for t in column_set1}
            column_set2_indexes = {t[0] for t in column_set2}

            all_column_indexes = column_set1_indexes.union(column_set2_indexes)

            maintuple = ("Field", "Type", "Null", "Key", "Default", "Extra")

            # Check for columns present in {detail1['database']} but not in the other
            for index in all_column_indexes - column_set2_indexes:
                tuple1 = next((t for t in column_set1 if t[0] == index), None)
                if tuple1:
                    html += f"<tr><td><b>{table[0]}</b>.{tuple1[0]}</td><td>Present</td><td>Absent</td></tr>"

            # Check for columns present in {detail2['database']} but not in the other
            for index in all_column_indexes - column_set1_indexes:
                tuple2 = next((t for t in column_set2 if t[0] == index), None)
                if tuple2:
                    html += f"<tr><td><b>{table[0]}</b>.{tuple2[0]}</td><td>Absent</td><td>Present</td></tr>"

            # Check for matching columns and mismatches
            for index in all_column_indexes.intersection(column_set1_indexes, column_set2_indexes):
                tuple1 = next((t for t in column_set1 if t[0] == index), None)
                tuple2 = next((t for t in column_set2 if t[0] == index), None)

                if tuple1 and tuple2:
                    if tuple1[1:] != tuple2[1:]:
                        for i in range(1, len(tuple1)):
                            if tuple1[i] != tuple2[i]:
                                html += f"<tr><td><b>{table[0]}</b>.{tuple1[0]}.{maintuple[i]}</td><td>{tuple1[i]}</td><td>{tuple2[i]}</td></tr>"

    html += "</tbody></table>"
    htmlfile = open("db_difference.html","w")
    script = """
        <script src="https://code.jquery.com/jquery-3.7.1.js"></script>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/2.0.0/css/dataTables.dataTables.css">

        <script src="https://cdn.datatables.net/2.0.0/js/dataTables.js"></script>
        <script>
        $(document).ready(function () {
            $('#example').DataTable();
        });
        </script>
        <style>
    </style>
            """

    htmlfile.write(f"""<!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DB Difference</title>
        </head>
                    {script}
        <body>  
    <div style="margin-top: 60px">
        {html}
    </div>
                        
        </body>
        </html>""")
    return html

if __name__ == '__main__':
    database_difference()
