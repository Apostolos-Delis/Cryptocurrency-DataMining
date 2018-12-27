#!/usr/bin/env python3
# coding: utf8


import mysql.connector
from hidden import DB_NAME, DB_HOST, DB_USERNAME, DB_PASSWORD


class DatabaseManager:
    """
    Class for a mysql wrapper in python.
    
    Usage:
        >>> dbm = DatabaseManager()
        >>> dbm.show_tables()
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
    

    def create_table(self, table_name: str, schema: dict):
        """
        Creates a table in the database

        :param table_name: str containing the name of the table
        :param schema: dict containing the structure of the table, an example
                       of a table containing student ids and their names would be:
                       {"name": "VARCHAR(255), "id": "INTEGER"}
        """
        if not isinstance(schema, dict):
            raise TypeError("The table schema must be a dictionary")
        
        if table_name in self.show_tables():
            print(table_name, "already exists, ignoring...")
            return
        
        sql_statement = "CREATE TABLE {0} (".format(table_name)
        for k,v in schema.items():
            sql_statement += "{0} {1}, ".format(k, v)
        
        # Remove the last comma and space from the sql command and add a closing )
        sql_statement = sql_statement[:-2] 
        sql_statement += ")"

        self._cursor.execute(sql_statement)


    def show_tables(self):
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
        sql_statement = "INSERT INTO {0} {1} VALUES {2}".format(table,
                str(keys), str(values))
        self._cursor.execute(sql_statement)
        self._cursor.commit()

    
    def delete_table(self, table: str):
        self._cursor.execute("DROP TABLE IF EXISTS {0}".format(table))


    def query(self, query: str):
        self._cursor.execute(query)
        return [q for q in self._cursor]


if __name__ == "__main__":
    pass
