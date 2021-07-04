class Treex:
    @classmethod
    def match(cls, treex, pattern):
        return cls.select(treex, pattern) != None

    @classmethod
    def select(cls, treex, pattern):
        return Selector.select(treex, pattern)

    @classmethod
    def fromjson(cls, jstree):
        if isinstance(jstree, str):
            return Node(jstree)
        else:
            node = Node(jstree[0])
            for ch in jstree[1:]:
                node.set(ch[0], cls.fromjson(ch[1]))

class Selector:
    @classmethod
    def select(cls, treex, pattern):
        res = cls.selectnode(treex, pattern)
        if res != None:
            res = res.groups
        return res

    @classmethod
    def selectnode(cls, treex, pattern):
        if treex.text != pattern.text:
            return None
        return cls.selectattrs(treex, pattern)

    @classmethod
    def selectattrs(cls, treex, pattern):
        found = MatchingResult()
        for (kind, value) in pattern.attributes.items():
            if kind[0] == '$':
                return None
            else:
                if kind in treex.attributes:
                    res = cls.selectnode(treex.attributes[kind], value)
                    if res == None:
                        return None
                    else:
                        found.append(res)
        return found

class Node:
    def __init__(self, text):
        self.text = text
        self.attributes = { }

    def set(self, kind, value):
        self.attributes[kind] = value

    def has(self, kind):
        return kind in self.attributes

class MatchingResult:
    def __init__(self):
        self.groups = { }

    def appendgroup(self, name, value):
        if name in self.groups:
            self.groups[name].append(value)
        else:
            self.groups[name] = [ value ]

    def append(self, result):
        for (name, value) in result.groups.items():
            if name in self.groups:
                self.groups[name].extend(value)
            else:
                self.groups[name] = value
