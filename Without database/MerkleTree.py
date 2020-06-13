from hashlib import sha256
import copy
from graphviz import Graph


class MerkleTree:
    def __init__(self, transactions, block_id=1, simple_hash=True):
        """
        0. transactions - list of transactions
        1. self.simple_hash - boolean. If is True then function self.get_hash()
        return simple hash, otherwise return sha256
        2. db - database where store all calculated hashes
        """
        self.block_id = block_id
        self.simple_hash = simple_hash
        self.node_hash = dict()  # key: (block_id, level, position)

        # Complete transactions for full binary tree
        self.transactions = copy.deepcopy(transactions)
        idx = len(self.transactions)
        for i in range(self.complete_to_full(idx) - idx):
            self.transactions += [self.transactions[-1]]
        self.height = self.get_height(len(self.transactions))

        # Calculating hash of each node in merkle tree
        for i in range(len(self.transactions)):
            self.node_hash[(self.block_id, 1, i + 1)] = self.transactions[i]
        _ = self.calculate_hash(self.transactions)
    
    def get_hash(self, data):
        """
        input: data - string
        output: string, hash of data by sha256 algorithm
        """
        if self.simple_hash:
            return data
        return sha256(data.encode()).hexdigest()

    def calculate_hash(self, hashes, level=1):
        """
        recursive function for calculating hash
        of each node in merkle tree.
        """
        if len(hashes) == 1:
            return hashes[0]

        temp = []
        for i in range(0, len(hashes), 2):
            _hash = self.get_hash(hashes[i] + hashes[i + 1])
            self.node_hash[(self.block_id, level + 1, i // 2 + 1)] = _hash
            temp.append(_hash)

        return self.calculate_hash(temp, level + 1)

    def dfs(self, G, level, idx):
        """
        recursive function for draw merkle tree
        """
        if level == 1:
            return

        node = str(level) + ',' + str(idx)

        # left child
        node_left = str(level - 1) + ',' + str(self.left_child(idx))
        G.edge(node, node_left)
        self.dfs(G, level - 1, self.left_child(idx))

        # right child
        node_right = str(level - 1) + ',' + str(self.right_child(idx))
        G.edge(node, node_right)
        self.dfs(G, level - 1, self.right_child(idx))

    def draw(self, validation_nodes=None, idx_for_validation=None):
        """This function draw Merkle tree"""
        G = Graph()

        # Defining all nodes
        for row in self.node_hash:  # blockid, level, position
            name = str(row[1]) + ',' + str(row[2])
            label = self.node_hash[row]

            if validation_nodes is None:
                G.node(name=name, label=label)
            elif (row[1], row[2]) in validation_nodes:
                G.node(name=name, label=label, color='lightblue2', style='filled')
            elif (row[1], row[2]) == (1, idx_for_validation):
                G.node(name=name, label=label, color='violet', style='filled')
            else:
                G.node(name=name, label=label)

        # Adding edges
        self.dfs(G, self.height, 1)
        return G

    @staticmethod
    def get_height(idx):
        """
        input: idx - right index for complete tree. Example idx = 1, 2, 4, 8,...
        output: level of complete this tree
        """
        level = 0
        while idx > 0:
            level += 1
            idx //= 2
        return level

    @staticmethod
    def complete_to_full(idx):
        """
        input: idx - right index of tree.
        output: right index for complete tree
        """
        # if idx == 1:
        #     return 1
        i = 1
        while i * 2 < idx:
            i *= 2
        return 2 * i

    @staticmethod
    def parent(idx):
        if idx % 2 == 0:
            return idx // 2
        return idx // 2 + 1

    @staticmethod
    def left_child(idx):
        return 2 * idx - 1

    @staticmethod
    def right_child(idx):
        return 2 * idx

    def get_nodes_for_validation(self, idx, get_graph=False):
        """
        idx: index in [1, 2, ...]
        :return list of nodes for validation
        """
        idx_for_validation = idx
        result = []
        for i in range(self.height - 1):
            prev = idx
            idx = self.parent(idx)
            left = self.left_child(idx)
            right = self.right_child(idx)
            if left == prev:
                result += [(i + 1, right)]
            else:
                result += [(i + 1, left)]
        if get_graph:
            return result, self.draw(result, idx_for_validation)
        return result