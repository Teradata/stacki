import os
import pymysql


def get_database_pw():
    try:
        file = open("/etc/apache.my.cnf", "r")
        for line in file.readlines():
            if line.startswith("password"):
                passwd = line.split("=")[1].strip()
                return passwd
        file.close()
    except:
        return ""


def connect_db(host="localhost", username="apache", passwd="", port=40000):
    if not passwd:
        passwd = get_database_pw()

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
            host=host,
            unix_socket="/run/mysql/mysql.sock",
            autocommit=True,
        )
    else:
        db = pymysql.connect(
            db=db_name,
            host=host,
            port=port,
            user=username,
            passwd=passwd,
            autocommit=True,
        )
    return db.cursor(pymysql.cursors.DictCursor)


database_url = os.environ.get("DATABASE_URL")

if database_url:
    db = connect_db(host=database_url, username="root", passwd="secret", port=3306)
else:
    db = connect_db()


def run_sql(cmd, args=None, fetchone=False):
    """
  Runs the SQL command

  Returns:
  results - either a list of results or a single result depending
  on the fetchone arg

  affected_rows - Number of rows affected
  """
    if not args:
        args = ()
    affected_rows = db.execute(cmd, args)
    if fetchone:
        return (db.fetchone(), affected_rows)

    return (db.fetchall(), affected_rows)

