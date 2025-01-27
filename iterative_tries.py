from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AbstractNode(ABC):
    """
    Abstract class for nodes in a trie.
    """

    char: str

@dataclass
class AbstractTrie(ABC):
    """
    Abstract class for trie data structures.
    """

    @abstractmethod
    def contains(self, word: str) -> bool:
        pass

    @abstractmethod
    def delete(self, word: str) -> bool:
        pass

    @abstractmethod
    def insert(self, word: str) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def create_trie(words: list[str]) -> AbstractTrie:
        """
        Constructor method for trie data structures. Creates a trie from a list of words.
        """
        pass



@dataclass
class VarSizeNode(AbstractNode):
    """
    Class for nodes in a variable size trie.
    """

    children: list[VarSizeNode]

    def has_max_children(self, max_children):
        if self.children is None: return True
        return len(self.children) <= max_children

@dataclass
class VarSizeTrie(AbstractTrie):
    """
    Class for variable size trie data structures.

    For each node, its character is stored as a string and the children are stored in a list.
    """

    children: list[VarSizeNode]

    def __go_through_trie(self, word: str, if_found, if_not_found, when_completed) -> bool:
        parent = self
        for i, character in enumerate(word):
            found = False
            for child in parent.children:
                if character == child.char:
                    if_found(parent, child)
                    parent = child
                    found = True
                    break
            if not found: return if_not_found(parent, word[i:])
        return when_completed()
    
    def contains(self, word: str) -> bool:
        return self.__go_through_trie(
            word,
            if_found=lambda parent, child: None,
            if_not_found=lambda parent, rest_word: False,
            when_completed=lambda: True
        )

    def delete(self, word: str) -> bool:
        marked_parent = None
        child_to_delete = None

        def mark_parent(parent, child):
            nonlocal marked_parent, child_to_delete
            if not child.has_max_children(1):
                marked_parent = None
                child_to_delete = None
            elif marked_parent == None:
                marked_parent = parent
                child_to_delete = child

        def delete_child_from_marked():
            nonlocal marked_parent, child_to_delete
            marked_parent.children.remove(child_to_delete)
            return True
        
        return self.__go_through_trie(
            word,
            if_found=lambda parent, child: mark_parent(parent, child),
            if_not_found=lambda parent, rest_word: False,
            when_completed=lambda: delete_child_from_marked()
        )

    def insert(self, word: str) -> bool:

        def insert_child(parent, rest_word):
            current_child = parent
            for character in rest_word:
                new_child = VarSizeNode(char=character, children=[])
                current_child.children.append(new_child)
                current_child = new_child
            return True

        return self.__go_through_trie(
            word,
            if_found=lambda parent, child: None,
            if_not_found=lambda parent, rest_word: insert_child(parent, rest_word),
            when_completed=lambda: False
        )

    @staticmethod
    def create_trie(words: list[str]) -> VarSizeTrie:
        trie = VarSizeTrie(children=[])
        for word in words: trie.insert(word)
        return trie


@dataclass
class FixedSizeNode(AbstractNode):
    """
    Class for nodes in a variable size trie.
    """

    children: list[FixedSizeNode]

    def has_max_children(self, max_children):
        if self.children is None: return True
        return sum(1 for _ in filter(None.__ne__, self.children)) <= max_children

@dataclass
class FixedSizeTrie(AbstractTrie):
    """
    Class for fixed size trie data structures.

    For each node, the children are stored in a fixed size list and the character to index mapping is stored in a list.
    """

    children: list[FixedSizeNode]
    char_to_idx: list[int]
    alphabet: str

    def __go_through_trie(self, word: str, if_found, if_not_found, when_completed) -> bool:
        parent = self
        for i, character in enumerate(word):
            child = parent.children[self.char_to_idx[ord(character)]]
            if child:
                if_found(parent, child)
                parent = child
            else: return if_not_found(parent, word[i:])
        return when_completed()
    
    def contains(self, word: str) -> bool:
        return self.__go_through_trie(
            word,
            if_found=lambda parent, child: None,
            if_not_found=lambda parent, rest_word: False,
            when_completed=lambda: True
        )
    
    def delete(self, word: str) -> bool:
        marked_parent = None
        child_to_delete = None

        def mark_parent(parent, child):
            nonlocal marked_parent, child_to_delete
            if not child.has_max_children(1):
                marked_parent = None
                child_idx = None
            elif marked_parent == None:
                marked_parent = parent
                child_to_delete = child

        def delete_child_from_marked():
            nonlocal marked_parent, child_to_delete
            marked_parent.children[self.char_to_idx[ord(child_to_delete.char)]] = None
            return True
        
        return self.__go_through_trie(
            word,
            if_found=lambda parent, child: mark_parent(parent, child),
            if_not_found=lambda parent, rest_word: False,
            when_completed=lambda: delete_child_from_marked()
        )
    
    def insert(self, word: str) -> bool:
        def insert_child(parent, rest_word):
            current_child = parent
            for character in rest_word:
                new_children = [None] * len(self.alphabet)
                new_child = FixedSizeNode(char=character, children=new_children)
                current_child.children[self.char_to_idx[ord(character)]] = new_child
                current_child = new_child
            return True

        return self.__go_through_trie(
            word,
            if_found=lambda parent, child: None,
            if_not_found=lambda parent, rest_word: insert_child(parent, rest_word),
            when_completed=lambda: False
        )
        
    @staticmethod
    def create_trie(alphabet: str, words: list[str]) -> FixedSizeTrie:
        highest_index = max([ord(char) for char in alphabet.strip('\x00')])
        char_to_idx: list[int] = [None] * (highest_index+1)
        children: list[FixedSizeNode] = [None] * len(alphabet)
        for i, char in enumerate(alphabet):
            char_to_idx[ord(char)] = i
        trie = FixedSizeTrie(char_to_idx=char_to_idx, alphabet=alphabet, children=children)
        for word in words: trie.insert(word)
        return trie


@dataclass
class HashNode(AbstractNode):
    """
    Class for nodes in a variable size trie.
    """

    children: dict[str, HashNode]

    def has_max_children(self, max_children):
        if self.children is None: return True
        return len(self.children.keys()) <= max_children

@dataclass
class HashTrie(AbstractTrie):
    """
    Class for hash trie data structures.

    For each node, the children are stored in a dictionary.
    """

    children: dict[str, HashNode]

    def __go_through_trie(self, word: str, if_found, if_not_found, when_completed) -> bool:
        parent = self
        for i, character in enumerate(word):
            if character in parent.children:
                child = parent.children[character]
                if_found(parent, child)
                parent = child
            else: return if_not_found(parent, word[i:])
        return when_completed()
    
    def contains(self, word: str) -> bool:
        return self.__go_through_trie(
            word,
            if_found=lambda parent, child: None,
            if_not_found=lambda parent, rest_word: False,
            when_completed=lambda: True
        )
    
    def delete(self, word: str) -> bool:
        marked_parent = None
        child_to_delete = None

        def mark_parent(parent, child):
            nonlocal marked_parent, child_to_delete
            if not child.has_max_children(1):
                marked_parent = None
                child_idx = None
            elif marked_parent == None:
                marked_parent = parent
                child_to_delete = child

        def delete_child_from_marked():
            nonlocal marked_parent, child_to_delete
            marked_parent.children.pop(child_to_delete.char)
            return True
        
        return self.__go_through_trie(
            word,
            if_found=lambda parent, child: mark_parent(parent, child),
            if_not_found=lambda parent, rest_word: False,
            when_completed=lambda: delete_child_from_marked()
        )
    
    def insert(self, word: str) -> bool:
        def insert_child(parent, rest_word):
            current_child = parent
            for character in rest_word:
                new_child = HashNode(char=character, children={})
                current_child.children[character] = new_child
                current_child = new_child
            return True

        return self.__go_through_trie(
            word,
            if_found=lambda parent, child: None,
            if_not_found=lambda parent, rest_word: insert_child(parent, rest_word),
            when_completed=lambda: False
        )
        
    @staticmethod
    def create_trie(words: list[str]) -> HashTrie:
        trie = HashTrie({})
        for word in words: trie.insert(word)
        return trie