from hashlib import sha256
from graphviz import Digraph

class PatriciaTrie:
    def __init__(self, simple_hash=True):
        self.simple_hash = simple_hash
        self.table = dict()     # key: node_id, value: [child idx, prefix]
        self.cnt = 0            # count of nodes
        self.info = dict()      # Store info about balance, parent_id, hash, type of node.
        self.info[0] = dict({'type': 'root'})

    def get_hash(self, data: str) -> str:
        """input: data - string
        output: string, hash of data by sha256 algorithm
        """
        if self.simple_hash:
            return data
        sha_value = sha256(data.encode()).hexdigest()
        return sha_value

    def create(self, tx: list, txhash: str):
        """
        :param  tx: list of transactions: [(user1, amount1), (user2, amount2), ...]
                txhash: A hash of these transactions which calculated by RPL
        :return: None. Just update MPT
        """
        for (user, amount) in tx:
            # Find user in MPT
            idx = self.dfs(0, user, amount, update_balance=False, minus=False)
            self.info[idx]['type'] = 'user'

            # Find transaction hash for given user
            idx = self.dfs(idx, txhash, amount, update_balance=True, minus=False)
            self.info[idx]['balance'] = amount
            self.info[idx]['type'] = 'leaf'

            # case 1: hash_leaf = hash(tx_hash|balance_charge)
            self.info[idx]['hash'] = self.get_hash('(hash:' + txhash + '|' + 'blc:' + str(amount) + ')')
            self.update_node_hash(idx)

    def spend(self, user1: str, user2: str, amount: int, txhash: str):
        """
        :param tx: list of transactions: [user1, user2, amount, transaction  hash]
        :param txhash: A hash of these transactions which calculated by RPL
        :return: None. Just updated MPT
        """
        minus = True
        for user in [user1, user2]:
            # Find user1 in MPT
            idx = self.dfs(0, user, amount, update_balance=False, minus=False)
            self.info[idx]['type'] = 'user'

            # Find transacntion hash for given user
            idx = self.dfs(idx, txhash, amount, update_balance=True, minus=minus)
            self.info[idx]['type'] = 'leaf'

            if minus:
                self.info[idx]['balance'] = -amount
            else:
                self.info[idx]['balance'] = amount
            
            # case 1: hash_leaf = hash(tx_hash|balance_charge)
            self.info[idx]['hash'] = self.get_hash('(hash:' + txhash + '|' + 'blc:' + str(amount) + ')')
            self.update_node_hash(idx)

            minus = False

    def common_prefix_len(self, prefix1: str, prefix2: str):
        """
        Helper function for self._dfs. Return command prefix for prefix1 and prefix2
        len(prefix1) <= len(prefix2)
        """
        same = 0
        for i in range(len(prefix1)):
            if prefix1[i] == prefix2[i]: 
                same += 1
            else: 
                break
        return same

    def dfs(self, idx: int, prefix: str, amount: int, update_balance=False, minus=False):
        """
        Helper recursive function for self.create
        :param idx: id for starting node
        :param prefix: prefix for searching. prefix user or hash
        :param hash: hash of transaction
        :return: None. Just updated MPT
        """
        if prefix == '':
            return idx
        
        # Initially we don't find any branch of node idx, which have 
        # at least one same character with given prefix
        found = False
        if update_balance:
            if 'balance' not in self.info[idx]:
                self.info[idx]['balance'] = 0
            if minus:
                self.info[idx]['balance'] -= amount
            else:
                self.info[idx]['balance'] += amount

        if idx in self.table:
            for branch in self.table[idx]: # branch: [child idx, prefix]
                k = self.common_prefix_len(branch[1], prefix)
                if k > 0:
                    found = True
                    if k == len(branch[1]):
                        return self.dfs(branch[0], prefix[k:], amount, update_balance, minus)
                    else:
                        child_id = branch[0]
                        diff = branch[1][k:]
                        self.cnt += 1
                        branch[0] = self.cnt
                        branch[1] = prefix[: k]

                        # parent
                        self.info[self.cnt] = dict({'parent': idx, 'type': 'before'})
                        self.info[child_id]['parent'] = self.cnt

                        self.table[self.cnt] = []
                        self.table[self.cnt].append([child_id, diff])
                        self.table[self.cnt].append([self.cnt + 1, prefix[k:]])
                        if update_balance:
                            self.info[self.cnt]['type'] = 'descendant'
                        
                        # parent
                        self.info[self.cnt + 1] = dict({'parent': self.cnt, 'type': 'before'})

                        # update transaction balance:
                        if update_balance:
                            if minus:
                                self.info[self.cnt]['balance'] = self.info[child_id]['balance'] - amount
                            else:
                                self.info[self.cnt]['balance'] = self.info[child_id]['balance'] + amount
                        self.cnt += 1
                        return self.cnt
        if not found:
            if idx not in self.table:
                self.table[idx] = []
            self.table[idx].append([self.cnt + 1, prefix])
            self.info[self.cnt + 1] = dict({'parent': idx})
            self.cnt += 1
            return self.cnt


    def update_node_hash(self, idx: int):
        """
        case 1:  
            If a leaf vertex (corresponds to a transaction):
            hash_leaf = hash(balance_charge|tx_hash)
        case 2:  
            If the vertex is descendant of the user:
            hash(balance|prefix_to_child_node + hash of child| ...)
        case 3: 
            If the vertex is a user: 
            hash_user = hash(id|balance|prefix_to_child_node + hash of child| ...)
        case 4:
            If the vertex is the ancestor (before) of users (for example, root),
            hash(prefix_to_child_node + hash of child| ...)
        """
        # Go up
        while idx != 0:
            idx = self.info[idx]['parent']
            if self.info[idx]['type'] == 'descendant':
                temp = '(blc:' + str(self.info[idx]['balance']) + ')|'
            elif self.info[idx]['type'] == 'user':
                temp = '(id:' + str(str(idx) + '|' + 'blc:' + str(self.info[idx]['balance'])) + ')|'
            else:
                temp = ''

            # cancatinating of child hashes
            for branch in self.table[idx]:  # [child idx, prefix]
                temp += '(' + 'prf:' + branch[1] + '|' + 'hash:' + self.info[branch[0]]['hash'] + ')'
            self.info[idx]['hash'] = self.get_hash(temp)

    def beautify(self, G, idx: int):
        """
        Helper function for self.draw
        """
        node_type = self.info[idx]['type']
        if 'user' == node_type :
            G.node(
                str(idx), 
                str(idx) + "\nUser balance = " + str(self.info[idx]['balance']), 
                shape='square', color='gold1', style='filled'
            )
        elif 'leaf' == node_type:
            G.node(
                str(idx), 
                str(idx) + "\ntx = " + str(self.info[idx]['balance']), 
                color='lightblue2', style='filled'
            )
        elif 'descendant' == node_type:
            G.node(
                str(idx), 
                str(idx) + "\nbalance = " + str(self.info[idx]['balance'])
            )
        else:
            G.node(str(idx))

    def draw(self):
        """
        This function draw Merkle patricia tree
        """
        G = Digraph()

        # Defining all nodes
        for parent_id in self.table:
            self.beautify(G, parent_id)

            for branch in self.table[parent_id]:
                self.beautify(G, branch[0])
        
        # Adding edges 
        for parent_id in self.table:
            for branch in self.table[parent_id]:
                G.edge(str(parent_id), str(branch[0]), label=branch[1])
        return G
