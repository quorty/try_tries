# try_tries
I learn how to implement tries. Implemented trie structures:
- Variable size trie: `-variante=1`
- Fixed size trie: `-variante=2`
- Hash trie: `-variante=3`

CLI use:

>`python test_tries.py -variante=<1-3> input_file_path query_file_path`

CLI help:

> `python test_tries.py -h`

Additionally, the boolean outputs for the query file are stored in the directory of
the input file with the name `result_<input file name>.txt`.

Former recursive implementation (`recursive_tries.py`) was way too slow,
so it was replaced with an iterative implementation instead (`iterative_tries.py`).
The recursive version supported a simple print function for the tries, but due
to lacking time, this was not implemented for the iterative version.
