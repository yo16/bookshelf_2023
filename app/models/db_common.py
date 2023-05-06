import mysql.connector

conn = None

def get_db_connection(app):
    return mysql.connector.connect(
        host=app.config["DBHOST"],
        db=app.config["DBNAME"],
        user=app.config["DBUSER"],
        passwd=app.config["DBPASS"],
        charset=app.config["DBCHARSET"]
    )
