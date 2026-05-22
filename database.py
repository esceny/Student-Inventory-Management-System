"""
database.py
-----------
Handles the MySQL database connection.
All other modules import this to get a database connection.
"""

import mysql.connector
from mysql.connector import Error


class Database:
    """
    A simple class to manage the MySQL database connection.
    
    Why a class? So we can reuse the same connection across the app
    without reconnecting every time we need to run a query.
    """

    def __init__(self, host="localhost", user="root", password="", database="inventory_db"):
        """
        Initialize the database connection settings.
        Change the defaults here to match your MySQL setup.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """
        Establish a connection to the MySQL database.
        Returns True if successful, False otherwise.
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"[ERROR] Could not connect to MySQL: {e}")
            print("Make sure MySQL is running and your credentials are correct.")
            return False

    def get_cursor(self):
        """
        Returns a cursor object to run SQL queries.
        dictionary=True means rows come back as dicts like {'id': 1, 'name': 'USB Cable'}
        instead of plain tuples — much easier to work with!
        """
        if self.connection and self.connection.is_connected():
            return self.connection.cursor(dictionary=True)
        else:
            print("[ERROR] No active database connection.")
            return None

    def commit(self):
        """Save (commit) any INSERT/UPDATE/DELETE changes to the database."""
        if self.connection:
            self.connection.commit()

    def close(self):
        """Close the connection when we're done."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
