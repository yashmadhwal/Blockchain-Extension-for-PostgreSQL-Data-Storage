import hashlib
import time
import numpy as np
import matplotlib.pyplot as plt

from PatriciaTrie import PatriciaTrie

samples = 14 # [1, 2, 4, 8, ..., 2 ** (samples - 1)]
time_array = np.zeros((samples,))
amount = 0
for user_number_index in range(samples):
    users_number = 2 ** user_number_index
    transactions = []
    t = PatriciaTrie(simple_hash=True)

    for i in range(users_number): # we can take random user ids
        m = hashlib.sha224(bytes(i)).hexdigest()
        transactions.append([m, 100])

    t.create(transactions, '0000')
    t.draw()

    number_of_request = 10000
    random_indexes = np.random.randint(users_number, size=number_of_request)
    users_for_requests = [hashlib.sha224(bytes(x)).hexdigest() for x in random_indexes]
    start_time = time.time()
    for request_index in range(number_of_request):
        t.info[t.dfs(0, users_for_requests[request_index], amount, update_balance=False, minus=False)]['balance']
    end_time = time.time()
    time_array[user_number_index] = end_time - start_time
    print(users_number, ': ', end_time - start_time)

plt.plot(range(samples), time_array)
plt.show()