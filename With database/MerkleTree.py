from hashfunction import get_hash
import copy

class MerkleTree:
    def __init__(self, db, transactions, simple_hash=True):
        """
        1. db - database where store all calculated hashes
        2. transactions - list of transactions
        3. block - id of block of transactions
        return simple hash, otherwise return sha256
        """
        self.block = db.get_block_number() + 1
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
            self.node_hash[(self.block, 1, i + 1)] = self.transactions[i]
        _ = self.calculate_hash(self.transactions)

        # Save all calculated data in database
        for item in self.node_hash:
            db.insert_node(item[0], item[1], item[2], self.node_hash[item])
        db.insert_merkle_root(
            self.node_hash[(self.block, self.height, 1)], self.height)

    def calculate_hash(self, hashes, level=1):
        """
        recursive function for calculating hash
        of each node in merkle tree.
        """
        if len(hashes) == 1:
            return hashes[0]

        temp = []
        for i in range(0, len(hashes), 2):
            _hash = get_hash(hashes[i] + hashes[i + 1], self.simple_hash)
            self.node_hash[(self.block, level + 1, i // 2 + 1)] = _hash
            temp.append(_hash)

        return self.calculate_hash(temp, level + 1)

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
