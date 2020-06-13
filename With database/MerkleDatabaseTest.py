from MerkleDatabase import MerkleDatabase

def test(args):
    db = MerkleDatabase(**args)
    db.delete_tables()
    db.create_tables()
    
    # Unittest 0
    assert db.get_block_number() == 0
    
    # Unittest 1
    db.insert_node(1, 1, 2, "a")
    assert db.get_calculated_hash(1, 1, 2) == "a"

    # Unittest 2
    db.insert_node(1, 1, 3, "b")
    assert db.get_calculated_hash(1, 1, 3) == "b"

    # Unittest 3
    db.insert_merkle_root("ab" , 2)
    assert db.get_root_info(1, 'merkle_hash') == "ab"

    # Unittest 4
    db.insert_merkle_root("abcd", 3)
    assert db.get_root_info(2, 'merkle_hash') == "abcd"
    assert db.get_root_info(2, 'merkle_height') == 3
    
    # Unittest 5
    assert db.get_block_number() == 2
    
    # Unittest 6
    db.create_user('Alice', 50)
    db.create_user('Bob', 100)
    db.create_user('Darkhan', 29)
    
    assert db.get_balance_of_user('Alice') == 50
    assert db.get_balance_of_user('Bob') == 100
    assert db.get_balance_of_user('Darkhan') == 29
    
    # Unittest 7
    db.update_user_balance('Darkhan', 20)
    assert db.get_balance_of_user('Darkhan') == 20
    
    # Unittest 8
    db.insert_trancsaction(
        txhash='1', _type='create', user1='Alice',
        amount=12, blockid=1, position=1
    )
    assert db.get_trancsaction('1')[1] == '1'
    assert db.get_trancsaction('1')[3] == 'Alice'
    
    db.delete_tables()
    db.close_session()
    
    print("\nSeems like good!")