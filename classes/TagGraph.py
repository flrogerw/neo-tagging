import logging  # Import the logging module for error logging
from neo4j import GraphDatabase  # Import the Neo4j Python driver
from neo4j.exceptions import DriverError, Neo4jError  # Import exceptions for error handling


class TagGraph:
    """
    TagGraph class for interacting with a Neo4j graph database.
    """

    def __init__(self, uri, user, password, database=None):
        """
        Constructor for initializing the TagGraph class.
        :param uri: URI of the Neo4j database
        :param user: Username for authentication
        :param password: Password for authentication
        :param database: Optional parameter for specifying the database
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))  # Initialize the Neo4j driver
        self.database = database  # Set the database name

    def close(self):
        """
        Method to close the Neo4j driver.
        """
        self.driver.close()

    def create_content(self, keywords, content_title, air_play):
        """
        Method to create keyword nodes in the graph.
        :param keywords: List of keywords to be created
        """
        # query = "MERGE (c:CONTENT {content_name: $content_title, airplay_time: $air_play, date_created: TIMESTAMP(), date_modified: TIMESTAMP()}) "
        #for keyword, name, weight in keywords:
            #label = f"l_{keyword}"
            #query += f"""MERGE ({label}:KEYWORD {{name: "{name}"}}) ON CREATE SET {label}.name="{name}", {label}.date_created=timestamp(), {label}.date_modified=timestamp() """
            #query += f"MERGE (c)-[:CONTAINS {{offset: 0.0, sort_weight: {weight}, date_created: TIMESTAMP(), date_modified: TIMESTAMP() }}]->({label}) "
        query = f"MERGE (c:CONTENT {{content_name: {content_title}, airplay_time: {air_play}, date_created: TIMESTAMP(), date_modified: TIMESTAMP()}}) "
        print(query)
        for keyword, name, weight in keywords:
            label = f"l_{keyword}"
            print(f"""MERGE ({label}:KEYWORD {{name: "{name}"}}) ON CREATE SET {label}.name="{name}", {label}.date_created=timestamp(), {label}.date_modified=timestamp() """)
            print(f"MERGE (c)-[:CONTAINS {{offset: 0.0, sort_weight: {weight}, date_created: TIMESTAMP(), date_modified: TIMESTAMP() }}]->({label}) ")
        try:
            x=0
            # self.driver.execute_query(
            #  query,
            #  air_play=air_play, content_title=content_title,
            # database_=self.database)
        except (DriverError, Neo4jError) as exception:  # Catch Neo4j driver or database errors
            logging.error("%s raised an error: \n%s", query, exception)  # Log the error
            raise
