from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AbstractTrie(ABC):

    char: str

    def contains(self, word: str) -> bool:
        if len(word) == 0: return True
        else: return self._contains(word)
        
    @abstractmethod
    def _contains(self, word: str) -> bool:
        pass

    def delete(self, word: str) -> bool:
        if len(word) == 0: return True
        else: return self._delete(word)

    @abstractmethod
    def _delete(self, word: str) -> bool:
        pass

    def insert(self, word: str) -> bool:
        if len(word) == 0: return False
        else: return self._insert(word)

    @abstractmethod
    def _insert(self, word: str) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def create_trie(words: str) -> AbstractTrie:
        pass

@dataclass
class VarSizeTrie(AbstractTrie):

    children: list[VarSizeTrie]

    def is_leaf(self):
        return not bool(self.children)
    
    def _contains(self, word: str) -> bool:
        for child in self.children:
            if word[0] == child.char: return child.contains(word[1:])
            #print(f"{word[0]} != {child.char}")
        return False
    
    def _delete(self, word: str) -> bool:
        success = False
        child_to_delete = None
        for child in self.children:
            if word[0] == child.char:
                success = child.delete(word[1:])
                child_to_delete = child
        if success:
            if child_to_delete.is_leaf():
                self.children.remove(child_to_delete)
        return success
    
    def _insert(self, word: str) -> bool:
        found = False
        success = True
        for child in self.children:
            if word[0] == child.char:
                found = True
                success = child.insert(word[1:])
        if not found:
            new_trie = self.__create_trie_for_rest(word)
            self.children.append(new_trie)
        return success
    
    @staticmethod
    def __create_trie_for_rest(rest_word: str) -> VarSizeTrie:
        if len(rest_word) == 1:
            return VarSizeTrie(rest_word, [])
        else:
            lower_node = VarSizeTrie.__create_trie_for_rest(rest_word[1:])
            return VarSizeTrie(rest_word[0], [lower_node])
        
    @staticmethod
    def create_trie(words: str) -> VarSizeTrie:
        trie = VarSizeTrie("root", [])
        trie.has_parent = False
        for word in words: trie.insert(word)
        return trie
    
    def print(self, is_root=True, depth=0):
        prefix = ""
        for _ in range(depth):
            prefix += "   "
        prefix += "└──"

        if is_root:
            print(self.char)
        else:
            char = self.char if self.char != "\0" else "$"
            print(prefix + char)

        for child in self.children:
            child.print(False, depth+1)