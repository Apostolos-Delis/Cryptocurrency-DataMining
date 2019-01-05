#!/usr/bin/env python3
# coding: utf8


import mysql.connector
from hidden import DB_NAME, DB_HOST, DB_USERNAME, DB_PASSWORD


class DatabaseWrapper:
    """
    Class for a mysql wrapper in python.
    
    Usage:
        >>> dbw = DatabaseWrapper()
        >>> dbw.show_tables()
        ... [table1, table2, ... ]
    """

    def __init__(self):
        self._database = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USERNAME,
                passwd=DB_PASSWORD,
                database=DB_NAME
        )
        self._cursor = self._database.cursor()
    
    
    def create_user(username: str, password: str):
        """Creates a new user for the database with all privileges"""
        sql_statement = f"GRANT ALL PRIVILEGES ON *.* TO {username}'@'localhost IDENTIFIED BY {password}"
        self._cursor.execute(sql_statement)
        self._database.commit()


    def create_table(self, table_name: str, schema: dict, foreign_keys: dict = None):
        """
        Creates a table in the database

        :param table_name: str containing the name of the table
        :param schema: dict containing the structure of the table, an example
                       of a table containing student ids and their names would be:
                       {"name": "VARCHAR(255)", "id": "INTEGER PRIMARY KEY"}
        :param foreign_keys: dict that specifies which columns are foreign keys and 
                             what columns they reference, dict should have the following 
                             structure:
                             {"column": ("table", "col_reference"), "column_2": ... }
        """
        if not isinstance(schema, dict):
            raise TypeError("The table schema must be a dictionary")
        
        if table_name in self.show_tables():
            print(table_name, "table already exists, ignoring...")
            return
        
        sql_statement = "CREATE TABLE {0} (".format(table_name)
        for k,v in schema.items():
            sql_statement += "{0} {1}, ".format(k, v)

        if isinstance(foreign_keys, dict):
            for key in foreign_keys.keys():
                sql_statement += "FOREIGN KEY ({0}) REFERENCES {1} ({2})".format(
                        key, foreign_keys[key][0], foreign_keys[key][1])
                sql_statement += " ON DELETE RESTRICT ON UPDATE CASCADE, "
        
        # Remove the last comma and space from the sql command and add a closing )
        sql_statement = sql_statement[:-2] 
        sql_statement += ")"
        self._cursor.execute(sql_statement)


    def show_tables(self) -> list:
        self._cursor.execute("SHOW TABLES")
        return [table[0] for table in self._cursor]

    
    def insert_into_table(self, entry: dict, table: str):
        """
        Insert a value into a specific table

        :param entry: a dict similar in structure to the schema dict
                      for creating tables, contains the columns as keys and 
                      the values for values. So in the student table example, an 
                      example entry would be:
                      {"id": 123, "name": "Thomas"}
        """
        if not isinstance(entry, dict):
            raise TypeError("The entry to insert into a table must be a dictionary")

        keys = tuple(entry.keys())
        values = tuple(entry.values())
        keys = "(" + ", ".join([str(key) for key in keys]) + ")"
        sql_statement = "INSERT IGNORE INTO {0} {1} VALUES {2}".format(table,
            keys, str(values))
        if len(values) == 1:
            # Remove the last comma and space from the sql command and add a closing )
            sql_statement = sql_statement[:-2] 
            sql_statement += ")"

        self._cursor.execute(sql_statement)
        self._database.commit()

    
    def delete_table(self, table: str):
        self._cursor.execute("DROP TABLE IF EXISTS {0}".format(table))


    def query(self, query: str) -> list:
        self._cursor.execute(query)
        return [q for q in self._cursor]

    
    def execute(self, sql_statement):
        """Will execute the given sql statement"""
        self._cursor.execute(sql_statement, multi=False)
        self._database.commit()


if __name__ == "__main__":
    print("The variable 'd' is an available DatabaseWrapper object")
    d = DatabaseWrapper()
