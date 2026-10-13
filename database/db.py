import mysql.connector
from mysql.connector import Error
import os

class Database:
    def __init__(self):
        self.connection = None
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'bookmyshoot')
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.is_connected():
                print(f"Connected to {self.database} database successfully")
                return True
            self.connection = None
        except Error as e:
            self.connection = None
            print(f"Error while connecting to MySQL: {e}")
        return False

    def is_connected(self):
        """Check whether a usable MySQL connection is available."""
        try:
            return bool(self.connection and self.connection.is_connected())
        except Error as e:
            self.connection = None
            print(f"Error checking MySQL connection: {e}")
            return False

    def _ensure_connection(self):
        if self.is_connected():
            return True
        return self.connect()
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query"""
        try:
            if not self._ensure_connection():
                return []
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"Error executing query: {e}")
            return []
    
    def execute_insert(self, query, params=None):
        """Execute INSERT query"""
        try:
            if not self._ensure_connection():
                return None
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except Error as e:
            if self.is_connected():
                self.connection.rollback()
            print(f"Error inserting data: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """Execute UPDATE query"""
        try:
            if not self._ensure_connection():
                return None
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
        except Error as e:
            if self.is_connected():
                self.connection.rollback()
            print(f"Error updating data: {e}")
            return None
    
    def execute_delete(self, query, params=None):
        """Execute DELETE query"""
        try:
            if not self._ensure_connection():
                return None
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
        except Error as e:
            if self.is_connected():
                self.connection.rollback()
            print(f"Error deleting data: {e}")
            return None

# Create a singleton database instance
db = Database()
