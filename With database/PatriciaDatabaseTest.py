from PatriciaDatabase import PatriciaDatabase

def test(args):
    db = PatriciaDatabase(**args)
    db.delete_tables()
    db.create_tables()

    # Unit test 1
    assert db.get_cell('PatriciaNode', 'type', 'node_id', 0) == 'root'

    # Unit test 2
    db.update_cell('PatriciaNode', 'balance', 100, 'node_id', 0)
    assert db.get_cell('PatriciaNode', 'balance', 'node_id', 0) == 100

    db.update_cell('PatriciaNode', 'hash', '!@#$%', 'node_id', 0)
    assert db.get_cell('PatriciaNode', 'hash', 'node_id', 0) == '!@#$%'

    # Unit test 3
    assert db.create_new_row('PatriciaEdge', 0) == 1
    assert db.get_cell('PatriciaEdge', 'prefix', 'edge_id', 1) == None
    assert db.get_cell('PatriciaEdge', 'child_id', 'edge_id', 1) == None

    # Unit test 4
    db.update_cell('PatriciaEdge', 'child_id', 2, 'edge_id', 1)
    assert db.get_cell('PatriciaEdge', 'child_id', 'edge_id', 1) == 2

    # Unit test 5
    db.update_cell('PatriciaEdge', 'prefix', 'Dark', 'edge_id', 1)
    assert db.get_cell('PatriciaEdge', 'prefix', 'edge_id', 1) == 'Dark'

    # Unit test 6
    assert db.create_new_row('PatriciaNode', 2) == 2
    db.update_cell('PatriciaNode', 'hash', '####', 'node_id', 2)
    assert db.get_cell('PatriciaNode', 'hash', 'node_id', 2) == '####'

    # Unit test 7
    assert db.create_new_row('PatriciaEdge', 0) == 2
    db.update_cell('PatriciaEdge', 'prefix', 'Sally', 'edge_id', 2)
    db.show_table('PatriciaEdge')

    assert db.get_branch(0, 'Darkhan') == (1, 0, 2, 'Dark')
    assert db.get_branch(2, 'Dark') == None
    
    db.delete_tables()
    db.close_session()

    print("\nSeems like good!")
