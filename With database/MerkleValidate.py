def get_nodes_for_validation(db, block, position):
    """
       :param db: database which store merkle trees data
       :param block: Id of block
       :param position: index leaf for varification
       :return: nodes (level, position) for verification node with id idx in given block
    """
    def parent(idx):
        if idx % 2 == 0: return idx // 2
        return idx // 2 + 1

    def left_child(idx):
        return 2 * idx - 1

    def right_child(idx):
        return 2 * idx

    height = db.get_root_info(block, 'merkle_height')
    nodes = []
    idx = position
    
    for i in range(height - 1):
        prev = idx
        idx = parent(idx)
        left = left_child(idx)
        right = right_child(idx)
        if left == prev:
            nodes += [(i + 1, right, db.get_calculated_hash(block, i + 1, right))]
        else:
            nodes += [(i + 1, left, db.get_calculated_hash(block, i + 1, left))]

    return nodes

