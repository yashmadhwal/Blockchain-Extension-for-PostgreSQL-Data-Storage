import psycopg2

class MerkleDatabase():
    def __init__(self, DB_NAME="blockchain_postgresql", 
                 #DB_USER="yashmadhwal", 
                 #DB_PASSWORD="", 
                 #DB_HOST="localhost",
                 DB_PORT="5432",
                 verbose=False):
        try:
            self.conn = psycopg2.connect(
                dbname=DB_NAME, 
                #user=DB_USER, 
                #password=DB_PASSWORD, 
                #host=DB_HOST, 
                port=DB_PORT
            )
            self.cur = self.conn.cursor()
            self.verbose = verbose
            if self.verbose: print("successfully connected to server!")
        except:
            print("failed while connection to server")

    def delete_tables(self):
        self.cur.execute("DROP TABLE IF EXISTS MerkleNode")
        self.cur.execute("DROP TABLE IF EXISTS Block")
        self.cur.execute("DROP TABLE IF EXISTS Balance")
        self.cur.execute("DROP TABLE IF EXISTS Transaction")
        self.conn.commit()
        if self.verbose: print("...table was deleted")

    def create_tables(self):
        self.cur.execute(
            """CREATE TABLE MerkleNode(
                node_id SERIAL PRIMARY KEY,
                block_id INT,
                level INT,
                position INT,
                hash VARCHAR(255), 
                UNIQUE (block_id, level, position)
            )"""
        )
        self.cur.execute(
            '''CREATE TABLE Block (
                block_id SERIAL PRIMARY KEY,
                merkle_hash VARCHAR(255),
                merkle_height INT,
                patricia_hash VARCHAR(255),
                block_hash VARCHAR(255)
            )'''
        )
        self.cur.execute(
            '''CREATE TABLE balance (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255),
                amount INT,
                UNIQUE (user_id)
            )'''
        )
        self.cur.execute(
            '''CREATE TABLE transaction (
                transaction_id SERIAL PRIMARY KEY,
                tx_hash VARCHAR(255),
                type VARCHAR(255),
                user1 VARCHAR(255),
                user2 VARCHAR(255),
                amount INT,
                block_id INT,
                position INT,
                UNIQUE (tx_hash)
            )'''
        )
        
        if self.verbose: print("table were created...")
        self.conn.commit()
    
    # BALANCE
    def get_balance_of_user(self, user):
        self.cur.execute(
            "SELECT amount FROM Balance WHERE user_id = '{}'".format(user)
        )
        result = self.cur.fetchone()
        if result is None:
            return None
        return result[0]
    
    def create_user(self, user, amount):
        self.cur.execute(
            "INSERT INTO Balance (user_id, amount) VALUES ('{}', {})".format(user, amount)
        )
        self.conn.commit()
    
    def update_user_balance(self, user, newbalance):
        query = "UPDATE Balance SET amount = {} WHERE user_id = '{}'"
        self.cur.execute(query.format(newbalance, user))
    
    # TRANSACTION
    def get_trancsaction(self, transaction_hash):
        self.cur.execute(
            "SELECT * FROM Transaction WHERE tx_hash = '{}'".format(transaction_hash)
        )
        result = self.cur.fetchone()
        if result is None:
            return None
        return result
    
    def insert_trancsaction(self, txhash, _type, user1, amount, blockid, position, user2='NULL'):
        query = '''
        INSERT INTO Transaction  (tx_hash, type, user1, user2, amount, block_id, position) 
        VALUES ('{}', '{}', '{}', '{}', {}, {}, {})'''
        self.cur.execute(query.format(txhash, _type, user1, user2, amount, blockid, position))
        self.conn.commit()
    
    def get_table(self, table_name='MerkleNode'):
        self.cur.execute("SELECT * FROM " + table_name)
        table = []
        for row in self.cur.fetchall():
            table += [row]
        return table

    def insert_node(self, block, level, position, _hash):
        self.cur.execute(
            '''INSERT INTO MerkleNode (block_id, level, position, hash) 
            VALUES ({}, {}, {}, '{}')'''.format(block, level, position, _hash)
        )
        self.conn.commit()
        
    def get_nodes_by_block(self, block):
        self.cur.execute(
            "SELECT * FROM MerkleNode WHERE block_id = {}".format(block)
        )
        table = []
        for row in self.cur.fetchall():
            table += [row]
        return table
    
    def get_calculated_hash(self, block, level, position):
        self.cur.execute(
            '''SELECT hash FROM MerkleNode WHERE 
            block_id = {} AND level = {} AND  position = {}'''.format(block, level, position)
        )
        result = self.cur.fetchone()
        if result is None:
            return None
        return result[0]

    def insert_merkle_root(self, merklehash, merkleheight):
        query = "INSERT INTO Block (merkle_hash, merkle_height) VALUES('{}', {})"
        self.cur.execute(query.format(merklehash, merkleheight))
        self.conn.commit()
    
    def update_info(self, field, new_value, idx):
        query = "UPDATE Block SET {} = '{}' WHERE block_id = {}"
        self.cur.execute(query.format(field, new_value, idx))
        
    def get_root_info(self, block, field='merkle_hash'):
        self.cur.execute('''SELECT {} FROM Block WHERE block_id = {}'''.format(field, block))
        result = self.cur.fetchone()
        if result is None:
            return None
        return result[0]
    
    def get_block_number(self):
        self.cur.execute('''SELECT COUNT(*) FROM Block''')
        result = self.cur.fetchone()
        return result[0]
    
    def close_session(self):
        self.conn.commit()
        self.conn.close()
        if self.verbose: print("connection to server was closed...")
        
    def print_column_name(self, table_name='Block'):
        self.cur.execute("SELECT * FROM {} LIMIT 0".format(table_name))
        print([desc[0] for desc in self.cur.description])

    def get_table_size(self, table_name):
        self.cur.execute("select pg_relation_size('{}')".format(table_name))
        result = self.cur.fetchone()
        return result[0]