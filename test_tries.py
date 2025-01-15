from tries import AbstractTrie, VarSizeTrie, FixedSizeTrie, HashTrie
import string

import sys
import os
from pathlib import Path
import time
import tracemalloc

ALPHABET = '\0' + string.ascii_letters + string.digits

def create_trie(words: list[str], trie_type='hash'):
    if trie_type == 'var':
        trie_constructor = lambda w : VarSizeTrie.create_trie(w)
    elif trie_type == 'fixed':
        trie_constructor = lambda w : FixedSizeTrie.create_trie(ALPHABET, w)
    elif trie_type == 'hash':
        trie_constructor = lambda w : HashTrie.create_trie(w)
    else:
        raise ValueError("Invalid trie type")
    start = time.time()
    trie = trie_constructor(words)
    end = time.time()
    return trie, (end-start)*1e3

def apply_query(trie: AbstractTrie, query: str):
    # check whether query string ends with i, d, or c
    if query[-1] == 'i':
        return trie.insert(query[:-2])
    elif query[-1] == 'd':
        return trie.delete(query[:-2])
    elif query[-1] == 'c':
        return trie.contains(query[:-2])
    else:
        raise ValueError("Invalid query")

if __name__ == "__main__":
    input_file_path = sys.argv[1]
    query_file_path = sys.argv[2]
    assert os.path.exists(input_file_path), "Input file does not exist"
    assert os.path.exists(query_file_path), "Query file does not exist"
    assert Path(input_file_path).suffix == '.txt', "Input file is not a text file"
    assert Path(query_file_path).suffix == '.txt', "Query file is not a text file"

    with open(input_file_path, 'r') as text_file:
        words = text_file.read().split('\n')
    
    # measure memory usage of trie creation with tracemalloc
    tracemalloc.start()
    trie, construction_time = create_trie(words, 'fixed')
    current, peak = tracemalloc.get_traced_memory()

    with open(query_file_path, 'r') as text_file:
        query_file = text_file.read().split('\n')

    # measure timing of queries
    q_start = time.time()
    for query in query_file:
        print(apply_query(trie, query))
    q_end = time.time()
    query_time = (q_end-q_start)*1e3
    
    print(f"name=KevinDanielKuryshev trie_construction_time={construction_time} trie_construction_memory={peak/(1024*1024)} query_time={query_time}")