from hashfunction import get_hash
from graphviz import Digraph

class PatriciaTrie:
    def __init__(self, db, simple_hash=True):
        self.db = db
        self.simple_hash = simple_hash
        self.cnt = self.db.get_cnt() #count of nodes
    
    def get_balance(self, user:str):
        """
        get user balance
        """
        # Find user in MPT
        idx = self.dfs_simple(0, user)
        
        balance = self.db.get_cell(
            table_name='PatriciaNode', 
            field='balance',
            column='node_id',
            idx=idx,
        )
        return balance
    
    def dfs_simple(self, idx, prefix):
        """
        Helper recursive get_balance
        """
        '''
        Commit: index of given prefix(user), find index of a given prefix.
        here prefix = user_key (eg hash of Alice)
        '''
        if prefix == '': return idx 
        branch = self.db.get_branch(idx, prefix)
        k = self.common_prefix_len(branch[3], prefix)
        return self.dfs_simple(branch[2], prefix[k:])
    
    def create(self, user, amount, txhash):
        """
        :param user, amount:int
        :param txhash: A hash of these transactions which calculated by RPL
        :return: None. Just update MPT
        """
        # Find user in MPT
        idx = self.dfs(0, user, amount, update_balance=False, minus=False)
        self.db.update_cell('PatriciaNode', 'type', 'user', 'node_id', idx)

        # Find transacntion hash for given user
        idx = self.dfs(idx, txhash, amount, update_balance=True, minus=False)

        self.db.update_cell('PatriciaNode', 'balance', amount, 'node_id', idx)
        self.db.update_cell('PatriciaNode', 'type', 'leaf', 'node_id', idx)

        # case 1: hash_leaf = hash(tx_hash|balance_charge)
        node_hash = get_hash(
            '(hash:' + txhash + '|' + 'blc:' + str(amount) + ')',
            self.simple_hash
        )
        self.db.update_cell('PatriciaNode', 'hash', node_hash, 'node_id', idx)
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
            idx = self.dfs_simple(0, user)
            # idx = self.dfs(0, user, amount, update_balance=False, minus=False)
            # self.db.update_cell('InfoPatricia', 'type', 'user', 'node_id', idx)

            # Find transacntion hash for given user
            idx = self.dfs(idx, txhash, amount, update_balance=True, minus=minus)
            self.db.update_cell('PatriciaNode', 'type', 'leaf', 'node_id', idx)

            if minus:
                self.db.update_cell('PatriciaNode', 'balance', -amount, 'node_id', idx)
            else:
                self.db.update_cell('PatriciaNode', 'balance', amount, 'node_id', idx)
            
            # case 1: hash_leaf = hash(tx_hash|balance_charge)
            node_hash = get_hash(
                '(hash:' + txhash + '|' + 'blc:' + str(amount) + ')',
                self.simple_hash
            )
            self.db.update_cell('PatriciaNode', 'hash', node_hash, 'node_id', idx)
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
            balance = self.db.get_cell('PatriciaNode', 'balance', 'node_id', idx)
            if minus:
                balance -= amount
            else:
                balance += amount
            self.db.update_cell('PatriciaNode', 'balance', balance, 'node_id', idx)

        for branch in self.db.get_all_branch(idx): # branch: (ID, node_id, child idx, prefix)
            k = self.common_prefix_len(branch[3], prefix)
            if k > 0:
                found = True
                if k == len(branch[3]):
                    return self.dfs(branch[2], prefix[k:], amount, update_balance, minus)
                else:
                    child_id = branch[2]
                    diff = branch[3][k:]
                    self.cnt += 1

                    self.db.update_cell('PatriciaEdge', 'child_id', self.cnt, 'edge_id', branch[0])
                    self.db.update_cell('PatriciaEdge', 'prefix', prefix[: k], 'edge_id', branch[0])

                    # parent
                    self.db.create_new_row('PatriciaNode', self.cnt)
                    self.db.update_cell('PatriciaNode', 'parent_id', idx, 'node_id', self.cnt)
                    self.db.update_cell('PatriciaNode', 'type', 'before', 'node_id', self.cnt)

                    self.db.update_cell('PatriciaNode', 'parent_id', self.cnt, 'node_id', child_id)

                    ID = self.db.create_new_row('PatriciaEdge', self.cnt)
                    self.db.update_cell('PatriciaEdge', 'child_id', child_id, 'edge_id', ID)
                    self.db.update_cell('PatriciaEdge', 'prefix', diff, 'edge_id', ID)
                    
                    ID = self.db.create_new_row('PatriciaEdge', self.cnt)
                    self.db.update_cell('PatriciaEdge', 'child_id', self.cnt + 1, 'edge_id', ID)
                    self.db.update_cell('PatriciaEdge', 'prefix', prefix[k:], 'edge_id', ID)

                    if update_balance:
                        self.db.update_cell('PatriciaNode', 'type', 'descendant', 'node_id', self.cnt)
                        
                    # parent
                    self.db.create_new_row('PatriciaNode', self.cnt + 1)
                    self.db.update_cell('PatriciaNode', 'parent_id', self.cnt, 'node_id', self.cnt + 1)
                    self.db.update_cell('PatriciaNode', 'type', 'before', 'node_id', self.cnt + 1)

                    # update transaction balance:
                    if update_balance:
                        balance = self.db.get_cell('PatriciaNode', 'balance', 'node_id', child_id)
                        if minus:
                            balance -= amount
                        else:
                            balance += amount
                        self.db.update_cell('PatriciaNode', 'balance', balance, 'node_id', self.cnt)
                    self.cnt += 1
                    return self.cnt
        if not found:
            ID = self.db.create_new_row('PatriciaEdge', idx)
            
            self.db.update_cell('PatriciaEdge', 'child_id', self.cnt + 1, 'edge_id', ID)
            self.db.update_cell('PatriciaEdge', 'prefix', prefix, 'edge_id', ID)

            self.db.create_new_row('PatriciaNode', self.cnt + 1)
            self.db.update_cell('PatriciaNode', 'parent_id', idx, 'node_id', self.cnt + 1)

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
            idx = self.db.get_cell('PatriciaNode', 'parent_id', 'node_id', idx)
            node_type = self.db.get_cell('PatriciaNode', 'type', 'node_id', idx)
            balance = self.db.get_cell('PatriciaNode', 'balance', 'node_id', idx)

            if node_type == 'descendant':
                temp = '(blc:' + str(balance) + ')|'
            elif node_type == 'user':
                temp = '(id:' + str(str(idx) + '|' + 'blc:' + str(balance)) + ')|'
            else:
                temp = ''

            # cancatinating of child hashes
            for branch in self.db.get_all_branch(idx): # branch: (edge_id, node_id, child idx, prefix)
                node_hash = self.db.get_cell('PatriciaNode', 'hash', 'node_id', branch[2])
                temp += '(' + 'prf:' + branch[3] + '|' + 'hash:' + node_hash + ')'

            self.db.update_cell(
                'PatriciaNode', 'hash', get_hash(temp, self.simple_hash), 
                'node_id', idx
            )

    def beautify(self, G, idx: int):
        """
        Helper function for self.draw
        """

        node_type = self.db.get_cell('PatriciaNode', 'type', 'node_id', idx)
        balance = self.db.get_cell('PatriciaNode', 'balance', 'node_id', idx)

        if 'user' == node_type :
            G.node(
                str(idx), 
                str(idx) + "\nUser balance = " + str(balance), 
                shape='square', color='gold1', style='filled'
            )
        elif 'leaf' == node_type:
            G.node(
                str(idx), 
                str(idx) + "\ntx = " + str(balance), 
                color='lightblue2', style='filled'
            )
        elif 'descendant' == node_type:
            G.node(
                str(idx), 
                str(idx) + "\nbalance = " + str(balance)
            )
        else:
            G.node(str(idx))

    def draw(self):
        """
        This function draw Merkle patricia tree
        """
        G = Digraph()

        # Defining all nodes
        for row in self.db.show_table('PatriciaNode'):
            self.beautify(G, row[0])
        
        # Adding edges 
        for row in self.db.show_table('PatriciaEdge'):
            G.edge(str(row[1]), str(row[2]), label=row[3])
        return G

