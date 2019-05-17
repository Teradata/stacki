import requests
import pymysql
import os
import datetime

from pprint import pprint


def connect_db(username="apache", passwd=""):
    passwd = ""
    try:
        file = open("/etc/apache.my.cnf", "r")
        for line in file.readlines():
            if line.startswith("password"):
                passwd = line.split("=")[1].strip()
                break
        file.close()
    except:
        pass

    # Connect to a copy of the database if we are running pytest-xdist
    if "PYTEST_XDIST_WORKER" in os.environ:
        db_name = "cluster" + os.environ["PYTEST_XDIST_WORKER"]
    else:
        db_name = "cluster"

    if os.path.exists("/run/mysql/mysql.sock"):
        db = pymysql.connect(
            db=db_name,
            user=username,
            passwd=passwd,
            host="localhost",
            unix_socket="/run/mysql/mysql.sock",
            autocommit=True,
        )
    else:
        db = pymysql.connect(
            db=db_name,
            host="localhost",
            port=40000,
            user=username,
            passwd=passwd,
            autocommit=True,
        )
    return db.cursor(pymysql.cursors.DictCursor)


db = connect_db()


def get_table_names():
    """Returns a list of the table names in the database"""
    db.execute("SHOW tables")

    table_names = []
    for table in db.fetchall():
        table_names.append(list(table.values())[0])

    return table_names


def select_query(table_name):
    db.execute(f"select * from {table_name}")

    return db.fetchall()


def insert_records(table_name, records):
    query_string = """mutation insert_%s_records($records: [%s_insert_input!]!){
      insert_%s(objects: $records){
        affected_rows
      }
    }
    """ % (
        table_name,
        table_name,
        table_name,
    )
    variables = {"records": records}
    headers = {"x-hasura-admin-secret": "myadminsecretkey"}

    r = requests.post(
        "http://localhost:8081/v1/graphql",
        headers=headers,
        json={"query": query_string, "variables": variables},
    )

    # TODO: deal with foreign keys
    results = r.json()
    #pprint(results)

for table_name in get_table_names():
    if 'yoyo' in table_name:
        continue

    records = select_query(table_name)
    pprint(records)
    insert_records(table_name, records)

