from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AbstractTrie(ABC):

    children: any

    def is_leaf(self):
        return not bool(self.children)

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
    char: str
    
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
            return VarSizeTrie(char=rest_word, children=[])
        else:
            lower_node = VarSizeTrie.__create_trie_for_rest(rest_word[1:])
            return VarSizeTrie(char=rest_word[0], children=[lower_node])
        
    @staticmethod
    def create_trie(words: list[str]) -> VarSizeTrie:
        trie = VarSizeTrie(char="root", children=[])
        for word in words: trie.insert(word)
        return trie
    
    def print(self, is_root=True, depth=0, is_last=False, was_last=False):
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
            child.print(False, depth+1, id(child) == id(self.children[-1]), is_last)


@dataclass
class FixedSizeTrie(AbstractTrie):

    children: list[FixedSizeTrie]
    char_to_idx: list[int]
    alphabet: str

    def _contains(self, word: str) -> bool:
        child: FixedSizeTrie = self.children[self.char_to_idx[ord(word[0])]]
        if child: return child.contains(word[1:])
        else: False
    
    def _delete(self, word: str) -> bool:
        success = False
        child_idx = self.char_to_idx[ord(word[0])]
        child: FixedSizeTrie = self.children[child_idx]
        if child:
            success = child.delete(word[1:])
        if success:
            if child.is_leaf() or not any(child.children):
                self.children[child_idx] = None
        return success
    
    def _insert(self, word: str) -> bool:
        success = True
        child_idx = self.char_to_idx[ord(word[0])]
        child: FixedSizeTrie = self.children[child_idx]
        if child:
            success = child.insert(word[1:])
        else:
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
        char_to_idx: list[int] = [None] * (highest_index+1)
        children: list[FixedSizeTrie] = [None] * len(alphabet)
        for i, char in enumerate(alphabet):
            char_to_idx[ord(char)] = i
        trie = FixedSizeTrie(char_to_idx=char_to_idx, alphabet=alphabet, children=children)
        for word in words: trie.insert(word)
        return trie
    
    def print(self, name="root", is_root=True, depth=0):
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
                    #print(self.idx_to_char[i])
                    child.print(self.alphabet[i], False, depth+1)





@dataclass
class HashTrie(AbstractTrie):

    children: dict[str, HashTrie]
    
    def _contains(self, word: str) -> bool:
        if word[0] in self.children:
            return self.children[word[0]].contains(word[1:])
        return False
    
    def _delete(self, word: str) -> bool:
        success = False
        if word[0] in self.children:
            child = self.children[word[0]]
            success = child.delete(word[1:])
        #else: print(f"{word[0]} does not appear in {self.children}")
        if success:
            #print(f"For {word[0]} deleting?: {child}")
            if child.is_leaf():
            #    print(f"Deleting...")
                self.children.pop(word[0])
        return success
    
    def _insert(self, word: str) -> bool:
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
    
    def print(self, char="", is_root=True, depth=0, is_last=False, was_last=False):
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
            self.children[child].print(child, False, depth+1, id(child) == id(list(self.children.keys())[-1]), is_last)