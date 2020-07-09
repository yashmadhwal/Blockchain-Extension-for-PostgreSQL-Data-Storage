#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 23:08:45 2020

@author: yashmadhwal
"""

from PatriciaDatabase import PatriciaDatabase
from PatriciaTrie import PatriciaTrie
from PatriciaDatabaseTest import test

args = {
    'DB_NAME': "blockchain_postgresql", 
    #'DB_USER': "darkhannurlybay",
    #'DB_PASSWORD': "",
    #'DB_HOST': "localhost",
    'DB_PORT': "5432",
    'verbose': False
}

test(args)

#Creating some Users
user = {
    'Alice': '000010',
    'Bob': '010100',
    'Sally': '111111',
    'Yash': '1111100'
}

db = PatriciaDatabase(**args)
db.delete_tables()
db.create_tables()

t = PatriciaTrie(db, simple_hash=False)

t.create(user['Alice'], 100, '0000')
t.create(user['Bob'], 50, '0001')

db.print_column_name('PatriciaNode');
for row in t.db.show_table('PatriciaNode'):
    print(row)
    
t.draw()    
'''
assert t.get_balance(user['Alice']) == 100
assert t.get_balance(user['Bob']) == 50


t.spend(user['Alice'], user['Bob'], 10, '1000')
assert t.get_balance(user['Alice']) == 90
assert t.get_balance(user['Bob']) == 60
t.draw()

db = PatriciaDatabase(**args)
t = PatriciaTrie(db, simple_hash=False)

t.create(user['Sally'], 0, '1111')
t.spend(user['Alice'], user['Sally'], 40, '1001')
assert t.get_balance(user['Alice']) == 50
assert t.get_balance(user['Sally']) == 40
t.draw()

t.create(user['Yash'], 0, '0111')
assert t.get_balance(user['Yash']) == 0
t.draw()

t.spend(user['Alice'], user['Yash'], 10, '1010')
t.draw()
db.close_session()
'''


