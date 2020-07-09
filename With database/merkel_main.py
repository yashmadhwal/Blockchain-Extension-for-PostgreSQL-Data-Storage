#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 21:10:47 2020

@author: yashmadhwal
"""
from MerkleDatabase import MerkleDatabase
from MerkleTree import MerkleTree
from MerkleDatabaseTest import test
from MerkleValidate import get_nodes_for_validation
from MerkleTreeDraw import MerkleTreeDraw
import sys

args = {
    'DB_NAME': "blockchain_postgresql", 
    #'DB_USER': "darkhannurlybay",
    #'DB_PASSWORD': "",
    #'DB_HOST': "localhost",
    'DB_PORT': "5432",
    'verbose': False
}

test(args)

db = MerkleDatabase(**args)
db.delete_tables()
db.create_tables()

leaf_items = sys.argv[1:]
range_number = int(leaf_items[0])

#print(type(1))
#print(type(range_number))
#1st Merkle Tree
transactions = [chr(97 + i) for i in range(range_number)]
tree = MerkleTree(db, transactions, simple_hash=True)


for i in db.get_table():
    print(i)

db.close_session()
