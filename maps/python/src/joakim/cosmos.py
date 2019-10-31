# This class performs CRUD operations vs CosmosDB with SQL/DocumentDB API.
# See https://docs.microsoft.com/en-us/azure/cosmos-db/sql-api-sql-query
# Chris Joakim, Microsoft, 2019/03/19

import os
import sys

import pydocumentdb.document_client as document_client


class DocDbUtil(object):

    def __init__(self, enable_cross_partition=True):
        host = os.environ['AZURE_COSMOSDB_SQLDB_URI']
        key  = os.environ['AZURE_COSMOSDB_SQLDB_KEY']
        self.client = document_client.DocumentClient(host, {'masterKey': key})

        if enable_cross_partition:
            self.client.default_headers['x-ms-documentdb-query-enablecrosspartition'] = True

    def collection_link(self, dbname, cname):
        return 'dbs/' + dbname + '/colls/' + cname;

    def document_link(self, dbname, cname, id):
        return self.collection_link(dbname, cname) + '/docs/' + id

    def list_databases(self):
        databases = list(self.client.ReadDatabases())
        if not databases:
            print('no databases')
        else:
            for db in databases:
                id = db['id']
                print('database: {}'.format(id))
        return databases

    def insert_document(self, dbname, cname, doc):
        link = self.collection_link(dbname, cname)
        try:
            return self.client.UpsertDocument(link, doc)
        except:
            print("Unexpected error:{}".format(sys.exc_info()[0]))
            raise

    def delete_document(self, dbname, cname, id, pk=None):
        link = self.document_link(dbname, cname, id)
        opts = dict()
        if pk:
            opts['partitionKey'] = pk
        try:
            return self.client.DeleteDocument(link, opts)
        except:
            print("Unexpected error:{}".format(sys.exc_info()[0]))
            raise

    def execute_query(self, dbname, cname, query_spec, enable_cross_partition=False):
        self.set_cross_partition_header(enable_cross_partition)
        link = self.collection_link(dbname, cname)
        print('execute_query; link: {} query_spec: {}'.format(link, query_spec))
        try:
            return list(self.client.QueryDocuments(link, query_spec))
        except:
            print("Unexpected error:{}".format(sys.exc_info()[0]))
            raise

    def set_cross_partition_header(self, boolean):
        header = self.cross_partition_header()
        self.client.default_headers[header] = boolean

    def cross_partition_header(self):
        return 'x-ms-documentdb-query-enablecrosspartition'
