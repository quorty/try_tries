# try_tries
I learn how to implement tries. Implemented trie structures:
- Variable size trie: `-variante=1`
- Fixed size trie: `-variante=2`
- Hash trie: `-variante=3`

CLI use:

>`python test_tries.py -variante=<1-3> input_file_path query_file_path`

CLI help:

> `python test_tries.py -h`

Note: Current implementation for fixed size trie uses lists, that are initialized with `None`. This is technically speaking not a literal fixed-size array, but an implementation with numpy arrays (that are closer to actual fixed-size arrays) did not show improvement in terms of performance.

The lines of code, that can be used to replace the current for the numpy implementation, are commented out right above the corresponding lines (in `tries.py`).
