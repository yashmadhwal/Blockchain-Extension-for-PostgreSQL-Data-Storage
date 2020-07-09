import psycopg2

class PatriciaDatabase():
    def __init__(self, DB_NAME="blockchain_postgresql",
                 #DB_USER="stxxaqoh",
                 #DB_PASSWORD="T94ybwpTs9z3mbqF0nQ02mFFeFPDlQhj",
                 #DB_HOST="drona.db.elephantsql.com",
                 DB_PORT="5432",
                 verbose=False):
        '''Interface to connecting, manipulating with database for 
        Patricia tree, which contain next tables:
            1. PatriciaEdge: (node_id, child_id, prefix)
            2. PatriciaNode: (node_id, parent_id, balance, hash, type). 
                type - type of node: 
                    a. root - root of patricia tree 
                    b. before (it means that node before user node)
                    c. user - node with start user node
                    d. leaf - leaf of patricia tree
        '''
        try:
            self.conn = psycopg2.connect(dbname=DB_NAME,
                                         #user=DB_USER,
                                         #password=DB_PASSWORD, host=DB_HOST, 
                                         port=DB_PORT)
            self.cur = self.conn.cursor()
            self.verbose = verbose
            if self.verbose: print("successfully connected to server!")
        except:
            print("failed while connection to server")

    def delete_tables(self):
        self.cur.execute("DROP TABLE IF EXISTS PatriciaEdge")
        self.cur.execute("DROP TABLE IF EXISTS PatriciaNode")
        self.conn.commit()
        if self.verbose: print("...table was deleted")

    def create_tables(self):
        self.cur.execute(
            '''CREATE TABLE PatriciaNode (
                node_id SERIAL PRIMARY KEY,
                parent_id INT,
                balance INT DEFAULT 0,
                hash VARCHAR(255),
                type VARCHAR(255)
            )'''
        )
        self.cur.execute(
            """CREATE TABLE PatriciaEdge(
                edge_id SERIAL PRIMARY KEY,
                node_id INT,
                child_id INT,
                prefix VARCHAR(255)
            )"""
        )
        # If table PatriciaNode is empty let's initialize it
        self.cur.execute("SELECT * FROM PatriciaNode")
        if self.cur.fetchone() is None:
            query = "INSERT INTO PatriciaNode (node_id, type) VALUES (0, 'root')"
            self.cur.execute(query)

        self.conn.commit()
        if self.verbose: print("table were created")

    def create_new_row(self, table_name, idx):
        self.cur.execute(
            '''INSERT INTO {} (node_id) 
            VALUES ({})'''.format(table_name, idx)
        )
        self.conn.commit()
        if self.verbose: print("...", idx, "was added to", table_name)

        self.cur.execute('SELECT COUNT(*) FROM {};'.format(table_name))
        result = self.cur.fetchone()
        return result[0]

    def update_cell(self, table_name, field, new_value, column, idx):
        '''
        for PatriciaNode: column is node_id
        for PatriciaEdge: column is edge_id
        '''
        query = "UPDATE {} SET {} = '{}' WHERE {} = {}"
        self.cur.execute(query.format(table_name, field, new_value, column, idx))
        if self.verbose:  print('updated...')
        self.conn.commit()

    def get_cell(self, table_name, field, column, idx):
        '''
        for PatriciaNode: column is node_id
        for PatriciaEdge: column is edge_id
        '''
        self.cur.execute(
            '''SELECT {} FROM {} WHERE {} = {}'''.format(
                field, table_name, column, idx)
        )
        result = self.cur.fetchone()
        if result is None:
            return None
        return result[0]

    def show_table(self, table_name):
        self.cur.execute("SELECT * FROM " + table_name)
        result = []
        for row in self.cur.fetchall():
            result += [row]
        return result

    def get_cnt(self):
        self.cur.execute('SELECT COUNT(*) FROM PatriciaNode;')
        result = self.cur.fetchone()
        return result[0] - 1

    def get_branch(self, idx, prefix):
        self.cur.execute(
            '''SELECT * FROM PatriciaEdge WHERE 
            node_id = {} AND '{}' LIKE CONCAT(prefix, '%')'''.format(idx, prefix)
        )
        result = self.cur.fetchone()
        return result
    
    def get_all_branch(self, idx):
        self.cur.execute(
            "SELECT * FROM PatriciaEdge WHERE node_id = {}".format(idx)
        )
        result = []
        for row in self.cur.fetchall():
            result += [row]
        return result
    
    def print_column_name(self, table_name='PatriciaEdge'):
        self.cur.execute("SELECT * FROM {} LIMIT 0".format(table_name))
        print([desc[0] for desc in self.cur.description])
        
    def close_session(self):
        self.conn.commit()
        self.conn.close()
        if self.verbose: print("connection to server was closed...")
            
    def get_table_size(self, table_name):
        self.cur.execute("select pg_relation_size('{}')".format(table_name))
        result = self.cur.fetchone()
        return result[0]