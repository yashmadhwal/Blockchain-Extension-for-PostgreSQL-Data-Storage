from graphviz import Graph
from MerkleValidate import get_nodes_for_validation

def MerkleTreeDraw(db, block, idx_for_validation=None):
    """
    This function draw Merkle tree
    """
    def parent(idx):
        if idx % 2 == 0: return idx // 2
        return idx // 2 + 1

    def left_child(idx):
        return 2 * idx - 1

    def right_child(idx):
        return 2 * idx

    def dfs(level, idx):
        if level == 1:
            return
        
        node = str(level) + ',' + str(idx)
        
        # left child
        node_left = str(level - 1) + ',' + str(left_child(idx))
        G.edge(node, node_left)
        dfs(level - 1, left_child(idx))

        # right child
        node_right = str(level - 1) + ',' + str(right_child(idx))
        G.edge(node, node_right)
        dfs(level - 1, right_child(idx))

    G = Graph()
    height = db.get_root_info(block, 'merkle_height')
    table = db.get_nodes_by_block(block)
    validation_nodes = None
    if not idx_for_validation is None:
        validation_nodes = get_nodes_for_validation(db, block, idx_for_validation)
        validation_nodes = [(x[0], x[1]) for x in validation_nodes]
    
    # Defining all nodes
    for row in table:  # id, blockid, level, position, hash
        name = str(row[2]) + ',' + str(row[3])
        label = row[4]
        if validation_nodes is None:
            G.node(name=name, label=label)
        elif (row[2], row[3]) in validation_nodes:
            G.node(name=name, label=label, color='lightblue2', style='filled')
        elif (row[2], row[3]) == (1, idx_for_validation):
            G.node(name=name, label=label, color='violet', style='filled')
        else:
            G.node(name=name, label=label)

    # Adding edges
    dfs(height, 1)
    return G
