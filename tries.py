from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
# import numpy as np # to create actual arrays for fixed size tries
# import numpy.typing as npt

@dataclass
class AbstractTrie(ABC):
    """
    Abstract class for trie data structures.
    """

    children: Any # all implementations use a form of group of children

    def is_leaf(self):
        """
        Check if the node is a leaf, by checking if it has no children.
        """
        return not bool(self.children) # leafs are nodes without children

    def contains(self, word: str) -> bool:
        """
        Performs contains query on trie. Calls `_contains`.

        Each implementation of `_contains` is based on recursion.

        First it checks if the first character of the word is contained in the children of the current node.
        If it is, the method is called recursively on the child node with the rest of the word.
        If the character is not found in the children, the method returns False.
        """
        if len(word) == 0: return True # Empty word is always contained
        else: return self._contains(word)
        
    @abstractmethod
    def _contains(self, word: str) -> bool:
        pass

    def delete(self, word: str) -> bool:
        """
        Performs delete query on trie. Calls `_delete`.

        Each implementation of `_delete` is based on recursion.

        First it checks if the first character of the word is contained in the children of the current node.
        If it is, the method is called recursively on the child node with the rest of the word.
        If the deletion (of the recursive call) was successful and the child is a leaf, the child node is removed.
        """
        if len(word) == 0: return True # Empty word means nothing to delete
        else: return self._delete(word)

    @abstractmethod
    def _delete(self, word: str) -> bool:
        pass

    def insert(self, word: str) -> bool:
        """
        Performs insert query on trie. Calls `_insert`.

        Each implementation of `_insert` is based on recursion.

        First it checks if the first character of the word is contained in the children of the current node.
        If it is, the method is called recursively on the child node with the rest of the word.
        If the character is not found in the children, a new trie is created for the rest of the word and added to the other children.
        """
        if len(word) == 0: return False # Empty word means nothing to insert
        else: return self._insert(word)

    @abstractmethod
    def _insert(self, word: str) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def create_trie(words: str) -> AbstractTrie:
        """
        Constructor method for trie data structures. Creates a trie from a list of words.
        """
        pass

    @abstractmethod
    def print_trie(self):
        """
        Prints the trie in a human-readable format.
        """
        pass



@dataclass
class VarSizeTrie(AbstractTrie):
    """
    Class for variable size trie data structures.

    For each node, its character is stored as a string and the children are stored in a list.
    """

    children: list[VarSizeTrie]
    char: str
    
    def _contains(self, word: str) -> bool:
        """
        Since the children are stored in a list, the method iterates over `children` to find the correct one.
        """
        for child in self.children:
            if word[0] == child.char: return child.contains(word[1:])
        return False
    
    def _delete(self, word: str) -> bool:
        """
        One has to iterate over the `children` list to find a child.
        Deletion afterward is done with the default `remove` method from lists.
        """
        success = False
        child_to_delete = None
        for child in self.children:
            if word[0] == child.char:
                success = child.delete(word[1:])
                child_to_delete = child
                break # only one child can have the correct character
        if success:
            if child_to_delete.is_leaf():
                self.children.remove(child_to_delete)
        return success
    
    def _insert(self, word: str) -> bool:
        """
        One has to iterate over the `children` list to find the correct child.
        Adding new children is done with the `append` method from lists.
        """
        found = False
        success = True
        for child in self.children:
            if word[0] == child.char:
                found = True
                success = child.insert(word[1:])
                break # only one child can have the correct character
        if not found:
            new_trie = self.__create_trie_for_rest(word)
            self.children.append(new_trie)
        return success
    
    @staticmethod
    def __create_trie_for_rest(rest_word: str) -> VarSizeTrie:
        if len(rest_word) == 1:
            return VarSizeTrie(char=rest_word, children=[])
        else:
            lower_node = VarSizeTrie.__create_trie_for_rest(rest_word[1:])
            return VarSizeTrie(char=rest_word[0], children=[lower_node])
        
    @staticmethod
    def create_trie(words: list[str]) -> VarSizeTrie:
        trie = VarSizeTrie(char="root", children=[])
        for word in words: trie.insert(word)
        return trie
    
    def print_trie(self):
        self.__recursive_print()

    def __recursive_print(self, is_root=True, depth=0, is_last=False, was_last=False):
        prefix = "   "
        for _ in range(depth-2):
            prefix += "│  "
        if depth > 1: prefix += "│  " if not was_last else "   "
        prefix += "├──" if not is_last else "└──"

        if is_root:
            print(self.char)
        else:
            char = self.char if self.char != "\0" else "$"
            print(prefix + char)

        for child in self.children:
            child.__recursive_print(False, depth+1, id(child) == id(self.children[-1]), is_last)



@dataclass
class FixedSizeTrie(AbstractTrie):
    """
    Class for fixed size trie data structures.

    For each node, the children are stored in a fixed size list and the character to index mapping is stored in a list.
    """

    # children: npt.NDArray[Any]
    # char_to_idx: npt.NDArray[np.int_]
    children: list[FixedSizeTrie]
    char_to_idx: list[int]
    alphabet: str

    def is_leaf(self):
        if self.children is None or not any(self.children): return True
        return False

    def _contains(self, word: str) -> bool:
        """
        Instead of iterating over `children`, the method uses the character to index mapping to find the correct child.
        In theory this should reduce the time complexity to O(1) for each character.
        """
        child: FixedSizeTrie = self.children[self.char_to_idx[ord(word[0])]]
        if child: return child.contains(word[1:])
        else: return False
    
    def _delete(self, word: str) -> bool:
        """
        The character to index mapping is used to find the correct child. In theory, this is in O(1).
        Deletion is done afterward by setting the corresponding position in the array to `None`.
        """
        success = False
        child_idx = self.char_to_idx[ord(word[0])]
        child: FixedSizeTrie = self.children[child_idx]
        if child:
            success = child.delete(word[1:])
        if success:
            if child.is_leaf():
                self.children[child_idx] = None
        return success
    
    def _insert(self, word: str) -> bool:
        """
        The character to index mapping is used to find the correct child. In theory, this is in O(1).
        A new `children` array (empty and of fixed size) is created if the child is `None`.
        """
        success = True
        child_idx = self.char_to_idx[ord(word[0])]
        child: FixedSizeTrie = self.children[child_idx]
        if child:
            success = child.insert(word[1:])
        else:
            # new_children = np.empty(len(self.alphabet), dtype=FixedSizeTrie)
            new_children = [None] * len(self.children)
            if len(word) == 1:
                new_child = FixedSizeTrie(char_to_idx=None, alphabet=self.alphabet, children=None)
            else:
                new_child = FixedSizeTrie(char_to_idx=self.char_to_idx, alphabet=self.alphabet, children=new_children)
            new_child.insert(word[1:])
            self.children[child_idx] = new_child
        return success
        
    @staticmethod
    def create_trie(alphabet: str, words: list[str]) -> FixedSizeTrie:
        highest_index = max([ord(char) for char in alphabet.strip('\x00')])
        # char_to_idx = np.zeros(highest_index+1, dtype=int)
        # children = np.empty(len(alphabet), dtype=FixedSizeTrie)
        char_to_idx: list[int] = [None] * (highest_index+1)
        children: list[FixedSizeTrie] = [None] * len(alphabet)
        for i, char in enumerate(alphabet):
            char_to_idx[ord(char)] = i
        trie = FixedSizeTrie(char_to_idx=char_to_idx, alphabet=alphabet, children=children)
        for word in words: trie.insert(word)
        return trie
    
    def print_trie(self):
        self.__recursive_print()
    
    def __recursive_print(self, name="root", is_root=True, depth=0):
        prefix = "   "
        for _ in range(depth-2):
            prefix += "│  "
        if depth > 1: prefix += "│  "
        prefix += "└──"

        if is_root:
            print(name)
        else:
            char = name if name != "\0" else "$"
            print(prefix + char)

        if self.children:
            for i, child in enumerate(self.children):
                if child:
                    child.__recursive_print(self.alphabet[i], False, depth+1)



@dataclass
class HashTrie(AbstractTrie):
    """
    Class for hash trie data structures.

    For each node, the children are stored in a dictionary.
    """

    children: dict[str, HashTrie]
    
    def _contains(self, word: str) -> bool:
        """
        `children` being a dictionary allows for quick access to the correct child.
        """
        if word[0] in self.children:
            return self.children[word[0]].contains(word[1:])
        return False
    
    def _delete(self, word: str) -> bool:
        """
        `children` being a dictionary allows for quick access to the correct child.
        To remove a child, the default `pop` method from dictionaries is used.
        """
        success = False
        if word[0] in self.children:
            child = self.children[word[0]]
            success = child.delete(word[1:])
        if success:
            if child.is_leaf():
                self.children.pop(word[0])
        return success
    
    def _insert(self, word: str) -> bool:
        """
        `children` being a dictionary allows for quick access to the correct child.
        Adding new children is done with the default `[]` notation for dictionaries.
        """
        success = True
        if word[0] in self.children:
            success = self.children[word[0]].insert(word[1:])
        else:
            new_trie = self.__create_trie_for_rest(word[1:])
            self.children[word[0]] = new_trie
        return success
    
    @staticmethod
    def __create_trie_for_rest(rest_word: str) -> HashTrie:
        if len(rest_word) == 1:
            return HashTrie({rest_word: HashTrie({})})
        else:
            lower_node = HashTrie.__create_trie_for_rest(rest_word[1:])
            return HashTrie({rest_word[0]: lower_node})
        
    @staticmethod
    def create_trie(words: list[str]) -> HashTrie:
        trie = HashTrie({})
        for word in words: trie.insert(word)
        return trie
    
    def print_trie(self):
        self.__recursive_print()
    
    def __recursive_print(self, char="", is_root=True, depth=0, is_last=False, was_last=False):
        prefix = "   "
        for _ in range(depth-2):
            prefix += "│  "
        if depth > 1: prefix += "│  " if not was_last else "   "
        prefix += "├──" if not is_last else "└──"

        if is_root:
            print("root")
        else:
            char = char if char != "\0" else "$"
            print(prefix + char)

        for child in self.children:
            self.children[child].__recursive_print(child, False, depth+1, id(child) == id(list(self.children.keys())[-1]), is_last)