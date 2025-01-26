from tries import AbstractTrie, VarSizeTrie, FixedSizeTrie, HashTrie
import string

import os
from pathlib import Path
import time
import tracemalloc
import argparse

ALPHABET = '\0' + string.ascii_letters + string.digits

def create_trie(words: list[str], trie_type='fixed_size'):
    """
    This method creates a trie from a list of words and returns the trie and the time [ms] taken to create the trie.
    """
    if trie_type == 'variable_size': # variable size trie
        trie_constructor = lambda w : VarSizeTrie.create_trie(w)
    elif trie_type == 'fixed_size': # fixed size trie
        trie_constructor = lambda w : FixedSizeTrie.create_trie(ALPHABET, w)
    elif trie_type == 'hash': # hash trie
        trie_constructor = lambda w : HashTrie.create_trie(w)
    else:
        raise ValueError("Invalid trie type")
    start = time.time()
    trie = trie_constructor(words)
    end = time.time()
    return trie, (end-start)*1e3

def apply_query(trie: AbstractTrie, query: str):
    """
    This method applies a query to the trie and returns the result.
    """
    # check whether query string ends with i, d, or c
    if query[-1] == 'i': # insert
        return trie.insert(query[:-2])
    elif query[-1] == 'd': # delete
        return trie.delete(query[:-2])
    elif query[-1] == 'c': # contains
        return trie.contains(query[:-2])
    else:
        raise ValueError("Invalid query")

if __name__ == "__main__":
    # read input and query file paths from command line arguments
    parser = argparse.ArgumentParser(
                    prog='test_tries.py',
                    description='Test trie creation, query, and query time. Outputs trie construction time, trie construction memory, and query time.',
                    epilog='')
    parser.add_argument('input_file_path', type=str, help='Path to input file')
    parser.add_argument('query_file_path', type=str, help='Path to query file')
    parser.add_argument('-variante', type=str, default='1', help='Trie variant: variable size trie (1), fixed size trie (2), or hash trie (3)')

    # get paths from command line arguments
    args = parser.parse_args()
    input_file_path = args.input_file_path
    query_file_path = args.query_file_path
    v = args.variante
    variant = 'variable_size' if v == '1' else 'fixed_size' if v == '2' else 'hash' if v == '3' else v
    assert os.path.exists(input_file_path), "Input file does not exist"
    assert os.path.exists(query_file_path), "Query file does not exist"
    assert Path(input_file_path).suffix == '.txt', "Input file is not a text file"
    assert Path(query_file_path).suffix == '.txt', "Query file is not a text file"

    with open(input_file_path, 'r') as text_file:
        words = text_file.read().split('\n')

        # measure memory usage of trie creation with tracemalloc
        tracemalloc.start()
        trie, construction_time = create_trie(words, variant)
        current, peak = tracemalloc.get_traced_memory() # in bytes

    with open(query_file_path, 'r') as text_file:
        query_file = text_file.read().split('\n')

        # measure timing of queries
        q_start = time.time()
        for query in query_file:
            print(apply_query(trie, query))
            #trie.print_trie()
        q_end = time.time() # in s
        query_time = (q_end-q_start)*1e3 # in ms
    
    print(f"name=KevinDanielKuryshev trie_variant={variant} trie_construction_time={construction_time} trie_construction_memory={peak/(1024*1024)} query_time={query_time}")