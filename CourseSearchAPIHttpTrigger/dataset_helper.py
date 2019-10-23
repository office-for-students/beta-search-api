import os
import logging

import azure.cosmos.cosmos_client as cosmos_client


class DataSetHelper:
    def __init__(self, client, collection_link):
        self.client = client
        self.collection_link = collection_link

    def get_highest_successful_version_number(self):
        query = "SELECT VALUE MAX(c.version) from c WHERE c.status = 'succeeded'"
        options = {"enableCrossPartitionQuery": True}
        max_version_number_list = list(
            self.client.QueryItems(self.collection_link, query, options)
        )
        version = max_version_number_list[0]
        logging.info(f"Highest successful dataset version: {version}")
        return version


def get_cosmos_client(cosmosdb_uri, cosmosdb_key):

    master_key = "masterKey"

    return cosmos_client.CosmosClient(
        url_connection=cosmosdb_uri, auth={master_key: cosmosdb_key}
    )


def get_collection_link(db_id, collection_id):
    """Create and return collection link based on values passed in"""

    # Return a link to the relevant CosmosDB Container/Document Collection
    return "dbs/" + db_id + "/colls/" + collection_id
