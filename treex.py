import logging

class Treex:
    @classmethod
    def match(cls, treex, pattern):
        return cls.select(treex, pattern) != None

    @classmethod
    def select(cls, treex, pattern):
        return Selector.select(treex, Selector.prepare(pattern))

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
        ctx = MatchingContext()
        cls.selectnode(treex, pattern, ctx)
        res = ctx.groups if ctx.isgood() else None
        logging.info('select returns with %s', res)
        return res

    @classmethod
    def prepare(cls, rawpat):
        logging.debug('prepare raw pattern')
        pattern = Modifier.copynode(rawpat)
        Modifier.resolverefs(pattern)
        return pattern

    @classmethod
    def selectnode(cls, treex, pattern, ctx):
        logging.debug('select node %s with %s', treex.text, pattern.text)
        if pattern.text[0] == '$':
            if pattern.text == '$any':
                pass
            else:
                ctx.setbad()
        else:
            if treex.text != pattern.text:
                ctx.setbad()
        if ctx.isgood():
            if pattern.has('$group'):
                ctx.appendgroup(pattern.get('$group').text, treex.text)
            if pattern.has('$ref'):
               cls.selectattrs(treex, pattern.get('$ref'), ctx)
        if ctx.isgood():
            cls.selectattrs(treex, pattern, ctx)

    @classmethod
    def selectattrs(cls, treex, pattern, ctx):
        logging.debug('select attrs %s with %s', treex.text, pattern.text)
        for (kind, value) in pattern.attributes.items():
            logging.debug('checking attr %s:%s', kind, Utils.prettyprint(value))
            if kind[0] == '$':
                if kind not in ('$anchor','$optional','$super','$group','$ref'):
                    ctx.setbad()
            else:
                if kind in treex.attributes:
                    cls.selectnode(treex.attributes[kind], value, ctx)
                else:
                    if not value.has('$optional'):
                        ctx.setbad()
        logging.debug('returns with ctx %s of %s found', ctx.isgood(), ctx.groups)

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

    @classmethod
    def resolverefs(cls, treex):
        anchors = {}
        for kind, val, parent in Utils.allvalues('', treex, None):
            logging.debug("Resolving '%s':'%s'", kind, val)
            if kind == '$anchor':
                logging.debug("Anchor %s to %s detected", val, parent.text)
                anchors[val] = parent
            if kind == '$ref':
                logging.debug("Reference %s at %s detected", val, parent.text)
                parent.set(kind, anchors[val])

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
        return "{{ {0}{1} }}".format( treex.text, cls.prettyattrs(treex) )

    @classmethod
    def allvalues(cls, attr, node, parent):
        yield (attr, node.text, parent)
        for kind, value in node.attributes.items():
            yield from cls.allvalues(kind, value, node)

    @classmethod
    def prettyattrs(cls, treex):
        if len(treex.attributes) > 0:
            return " [ {0} ]".format(" , ".join(cls.prettyattrstr(*x) for x in treex.attributes.items()))
        return ''

    @classmethod
    def prettyattrstr(cls, kind, value):
        return "{0}:{1}".format(kind, value.text if kind == '$ref' else Utils.prettyprint(value))

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

class MatchingContext:
    def __init__(self):
        self.good = True
        self.groups = { }

    def isgood(self):
        return self.good

    def setbad(self):
        self.good = False

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
