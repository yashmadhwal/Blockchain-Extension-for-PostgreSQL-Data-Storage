#!/usr/bin/env python3



# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 13:00:53 2020

@author: yashmadhwal
"""
import hashlib
import time
import numpy as np
import matplotlib.pyplot as plt
import random
from PatriciaTrie import PatriciaTrie

samples =  4
time_array = np.zeros((samples,),dtype=float)
amount = 0
transactions = 10000
number_of_request = 10000 #number of request from individual users, if users are 2, imagine they are making individual request.
initial_balance = 10**6

for user_number_index in range(1,samples): 
    number_of_users = 2 ** user_number_index 

    
    #creating users as per user_index key[user_no]: value[hash(user_no)]
    #declaring empty dictionary
    user = {}
    
    #appending user:
    for i in range(number_of_users):
        user['user_'+str(i)] = hashlib.sha224(bytes(int(i))).hexdigest()
        
    #object of PatriciaTrie
    t = PatriciaTrie(simple_hash=False)
    
    #creating users with initial transaction
    for i in user:
        tx_hash = hashlib.sha224(i.encode('utf-8')).hexdigest()
        t.create([(user[i], initial_balance)], tx_hash)
    
    #Making Random Transactions
    for i in range(transactions):
        sender = random.choice(list(user))
        receiver = random.choice(list(i for i in user if i not in sender))
        amount = random.randint(0, 100)
        transaction_string = str(sender + receiver + str(amount))
        tx_hash_balance = hashlib.sha224(transaction_string.encode('utf-8')).hexdigest()
        t.spend(user[sender], user[receiver],amount , tx_hash_balance)

    #-----X and Y plot------
    random_indexes = np.random.randint(number_of_users, size=number_of_request)#This array or random index is the request id.
    users_for_requests = [hashlib.sha224(bytes(x)).hexdigest() for x in random_indexes] 
    start_time = time.time()
    for request_index in range(number_of_request):
        t.info[t.dfs(0, users_for_requests[request_index], amount, update_balance=False, minus=False)]['balance']
    end_time = time.time()
    time_array[user_number_index] = end_time - start_time

plt.title('Random Transfers Number', loc='center')
plt.xlabel('Number of users')
plt.ylabel('Time to retrieve request')
#plt.xscale('log')
plt.plot([2 ** x for x in range(1, samples)], time_array[1:],'k.-', linewidth=1, markersize=12)  
plt.show()


visualize_graph = False
if visualize_graph:
    t.draw()