from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class AbstractNode(ABC):
    """
    Abstract class for nodes in a trie.
    """

    char: str
    children: Any

    @abstractmethod
    def has_max_children(self, max_children: int) -> bool:
        """
        Check whether the node has at most `max_children` children.
        """
        pass

@dataclass
class AbstractTrie(ABC):
    """
    Abstract class for trie data structures.
    """

    children: Any

    @abstractmethod
    def _go_through_trie(self,
        word: str,
        if_found: Callable[[AbstractNode, AbstractNode], None],
        if_not_found: Callable[[AbstractNode, str], bool],
        when_completed: Callable[[], bool]
    ) -> bool:
        """
        Go through the trie structure with the given word and call the appropriate
        functions when a node for a character is found, not found, or when the traversal
        is completed. Returns a boolean value representing the success of the operation.
        """
        pass

    def contains(self, word: str) -> bool:
        """
        Checks whether the trie contains the given word.

        Returns `True` if the word is found, `False` otherwise.
        """
        return self._go_through_trie(
            word,
            if_found=lambda parent, child: None, # do nothing when a node is found
            if_not_found=lambda parent, rest_word: False, # if a node is not found, the word is not contained in the trie
            when_completed=lambda: True # the word is contained in trie if traversal is completed
        )

    @abstractmethod
    def _delete_child_from_parent(parent_children, child: AbstractNode) -> None:
        """
        Given a list/array/dictionary of children, delete the given child.
        """
        pass

    def delete(self, word: str) -> bool:
        """
        Deletes the given word from the trie.

        Returns `True` if the word was deleted, `False` otherwise.
        """
        marked_parent = None
        child_to_delete = None

        # A node is only (potentially deleted), if it has at most one child.
        # If it has more, this means that multiple words have this same prefix.
        def mark_parent(parent, child):
            nonlocal marked_parent, child_to_delete
            if not child.has_max_children(1): # reset mark, if the child has more than one child
                marked_parent = None
                child_to_delete = None
            elif marked_parent == None: # set mark, if it has at most one child
                marked_parent = parent
                child_to_delete = child

        # Only if the word is contained in the trie, it can be deleted.
        # This is ensured, by checking whether the traversal was completed.
        def delete_child_from_marked():
            nonlocal marked_parent, child_to_delete
            self._delete_child_from_parent(marked_parent.children, child_to_delete)
            return True
        
        return self._go_through_trie(
            word,
            if_found=lambda parent, child: mark_parent(parent, child),
            if_not_found=lambda parent, rest_word: False,
            when_completed=lambda: delete_child_from_marked()
        )
    
    @abstractmethod
    def _add_empty_child(self, parent_children, character: str):
        """
        Create a new child node with the given character and add it to the parent's children.
        """
        pass

    def insert(self, word: str) -> bool:
        """
        Inserts the given word into the trie.

        Returns `True` if the word was inserted, `False` if it already is contained.
        """

        # Construct a new subtrie for the rest of the word and add it to the parent's children.
        def insert_child(parent, rest_word):
            current_child = parent
            for character in rest_word:
                current_child = self._add_empty_child(current_child.children, character)
            return True

        return self._go_through_trie(
            word,
            if_found=lambda parent, child: None, # do nothing when a node is found
            if_not_found=lambda parent, rest_word: insert_child(parent, rest_word),
            when_completed=lambda: False # if the traversal is completed, the word is already contained
        )



@dataclass
class VarSizeNode(AbstractNode):
    """
    Class for nodes in a variable size trie.
    """

    children: list[VarSizeNode]

    def has_max_children(self, max_children):
        if self.children is None: return True
        # The list contains exactly the number of children.
        return len(self.children) <= max_children

@dataclass
class VarSizeTrie(AbstractTrie):
    """
    Class for variable size trie data structures.

    For each node, its character is stored as a string and the children are stored in a list.
    """

    children: list[VarSizeNode]

    def _go_through_trie(self, word: str, if_found, if_not_found, when_completed) -> bool:
        parent = self # parent is initialized with a VarSizeTrie -> later it will be a VarSizeNode
        for i, character in enumerate(word):
            found = False
            # one has to enumerate through all children to find the right one
            for child in parent.children:
                if character == child.char:
                    if_found(parent, child)
                    parent = child # child is a VarSizeNode!
                    found = True
                    break
            if not found: return if_not_found(parent, word[i:])
        return when_completed()

    def _delete_child_from_parent(self, parent_children, child):
        parent_children.remove(child) # default list method does the trick

    def _add_empty_child(self, parent_children, character):
        # new children list can be initialized with an empty list
        new_child = VarSizeNode(char=character, children=[])
        parent_children.append(new_child)
        return new_child

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
        # The list contains more elements than the number of children.
        # Thus one has to filter out the None elements.
        return sum(1 for _ in filter(None.__ne__, self.children)) <= max_children

@dataclass
class FixedSizeTrie(AbstractTrie):
    """
    Class for fixed size trie data structures.

    For each node, the children are stored in a fixed size list and the character to index mapping is stored in a list.
    """

    children: list[FixedSizeNode]
    char_to_idx: list[int] # necessary for O(1) access! Converts a character to an index in the children list.
    alphabet: str

    def _go_through_trie(self, word: str, if_found, if_not_found, when_completed) -> bool:
        parent = self
        for i, character in enumerate(word):
            # get the child by the index: No need to enumerate through all children!
            child = parent.children[self.char_to_idx[ord(character)]]
            if child: # if the child is not None
                if_found(parent, child)
                parent = child
            else: return if_not_found(parent, word[i:])
        return when_completed()

    def _delete_child_from_parent(self, parent_children, child):
        # To delete a child, one simply has to set it to None.
        parent_children[self.char_to_idx[ord(child.char)]] = None

    def _add_empty_child(self, parent_children, character):
        new_children = [None] * len(self.alphabet) # init new children array with many None elements
        new_child = FixedSizeNode(char=character, children=new_children)
        parent_children[self.char_to_idx[ord(character)]] = new_child
        return new_child

    @staticmethod
    def create_trie(alphabet: str, words: list[str]) -> FixedSizeTrie:
        # Find the highest index in the alphabet to determine the size of the children list.
        highest_index = max([ord(char) for char in alphabet.strip('\x00')])
        char_to_idx: list[int] = [None] * (highest_index+1)
        children: list[FixedSizeNode] = [None] * len(alphabet)
        for i, char in enumerate(alphabet):
            char_to_idx[ord(char)] = i # map the character to the index
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
        # The dictionary's keys contain exactly the number of children.
        return len(self.children.keys()) <= max_children

@dataclass
class HashTrie(AbstractTrie):
    """
    Class for hash trie data structures.

    For each node, the children are stored in a dictionary.
    """

    children: dict[str, HashNode]

    def _go_through_trie(self, word: str, if_found, if_not_found, when_completed) -> bool:
        parent = self
        for i, character in enumerate(word):
            # get the child by the character: No need to enumerate through all children!
            if character in parent.children:
                child = parent.children[character]
                if_found(parent, child)
                parent = child
            else: return if_not_found(parent, word[i:])
        return when_completed()
    
    def _delete_child_from_parent(self, parent_children, child):
        parent_children.pop(child.char) # default dictionary method does the trick

    def _add_empty_child(self, parent_children, character):
        # new children dictionary can be initialized with an empty dictionary
        new_child = HashNode(char=character, children={})
        parent_children[character] = new_child
        return new_child

    @staticmethod
    def create_trie(words: list[str]) -> HashTrie:
        trie = HashTrie({})
        for word in words: trie.insert(word)
        return trie