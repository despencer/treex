import logging

class Treex:
    @classmethod
    def match(cls, treex, pattern):
        return cls.select(treex, pattern) != None

    @classmethod
    def select(cls, treex, pattern):
        return Selector.select(treex, pattern)

    @classmethod
    def fromjson(cls, jstree):
        return Utils.fromjson(jstree)

    @classmethod
    def apply(cls, context, treex):
        return Modifier.apply(context, treex)

    @classmethod
    def prettyprint(cls, treex):
        return Utils.prettyprint(treex)

class Selector:
    @classmethod
    def select(cls, treex, pattern):
        logging.info('select called for %s with %s', Utils.prettyprint(treex), Utils.prettyprint(pattern) )
        res = cls.selectnode(treex, pattern)
        if res != None:
            res = res.groups
        logging.info('select returns with %s', res)
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
                else:
                    return None
        return found

class Modifier:
    @classmethod
    def apply(cls, context, treex):
        return cls.applyinside(cls.copynode(context), treex)

    @classmethod
    def applyinside(cls, base, treex):
        base.text = treex.text
        for (kind, value) in treex.attributes.items():
            if base.has(kind):
                cls.applyinside(base.get(kind), value)
            else:
                base.set(kind, cls.copynode(value))
        return base

    @classmethod
    def copynode(cls, node):
        result = Node(node.text)
        for (kind, value) in node.attributes.items():
            result.set(kind, cls.copynode(value))
        return result

class Utils:
    @classmethod
    def init(cls):
        logging.basicConfig(filename='treex.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

    @classmethod
    def fromjson(cls, jstree):
        logging.debug('from json {0}'.format(jstree))
        if isinstance(jstree, str):
            return Node(jstree)
        else:
            node = Node(jstree[0])
            for ch in jstree[1:]:
                node.set(ch[0], cls.fromjson(ch[1]))
            return node

    @classmethod
    def prettyprint(cls, treex):
        pp = "{ " + treex.text
        pp = pp + " [ {0} ] "
        return "{{ {0}{1} }}".format( treex.text, cls.prettyattrs(treex) )

    @classmethod
    def prettyattrs(cls, treex):
        if len(treex.attributes) > 0:
            return " [ {0} ]".format(" , ".join(cls.prettyattrstr(*x) for x in treex.attributes.items()))
        return ''

    @classmethod
    def prettyattrstr(cls, kind, value):
        return "{0} : {1}".format(kind, Utils.prettyprint(value))

Utils.init()

class Node:
    def __init__(self, text):
        self.text = text
        self.attributes = { }

    def set(self, kind, value):
        self.attributes[kind] = value

    def get(self, kind):
        return self.attributes[kind]

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
