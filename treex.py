import logging

class Treex:
    @classmethod
    def match(cls, treex, pattern):
        return cls.select(treex, pattern) != None

    @classmethod
    def select(cls, treex, pattern):
        return Selector.select(treex, Selector.prepare(pattern))

    @classmethod
    def construct(cls, template, argument):
        return Constructor.construct(template, argument)

    @classmethod
    def fromjson(cls, jstree):
        return Utils.fromjson(jstree)

    @classmethod
    def apply(cls, context, treex):
        return Modifier.apply(context, treex)

    @classmethod
    def prettyprint(cls, treex):
        return Utils.prettyprint(treex)

    @classmethod
    def setlogconfig(cls, level=logging.WARNING, location=""):
        Utils.logger.setLevel(level)
        Utils.setloglocation(location)

class Selector:
    @classmethod
    def select(cls, treex, pattern):
        Utils.logger.info('select called for %s with %s', Utils.prettyprint(treex), Utils.prettyprint(pattern) )
        ctx = MatchingContext()
        cls.selectnode(treex, pattern, ctx)
        res = ctx.root()
        Utils.logger.info('select returns with %s', res)
        return res

    @classmethod
    def prepare(cls, rawpat):
        Utils.logger.debug('prepare raw pattern')
        pattern = Modifier.copynode(rawpat)
        Modifier.resolverefs(pattern)
        return pattern

    @classmethod
    def selectnode(cls, treex, pattern, ctx):
        Utils.logger.debug('select node %s with %s', treex.text, pattern.text)
        if pattern.text[0] == '$':
            if pattern.text == '$any':
                pass
            elif pattern.text == '$option':
                Utils.logger.debug('Trying list %s for %s', pattern.get('$list').attributes.values(), treex.text)
                if not treex.text in map(lambda x: x.text, pattern.get('$list').attributes.values()):
                    ctx.setbad()
            else:
                ctx.setbad()
        else:
            if treex.text != pattern.text:
                ctx.setbad()
        Utils.logger.debug('select node %s with %s, sofar %s', treex.text, pattern.text, ctx.isgood())
        group = None
        if ctx.isgood():
            if pattern.has('$group'):
                spr = pattern.get('$super').text if pattern.has('$super') else '$root'
                group = pattern.get('$group').text
                ctx.appendgroup(group, treex.text, spr)
            if pattern.has('$ref'):
               cls.selectnode(treex, pattern.get('$ref'), ctx)
        if ctx.isgood():
            cls.selectattrs(treex, pattern, ctx)
        ctx.leavegroup(group)

    @classmethod
    def selectattrs(cls, treex, pattern, ctx):
        Utils.logger.debug('select attrs %s with %s', treex.text, pattern.text)
        for (kind, value) in pattern.attributes.items():
            Utils.logger.debug('checking attr %s:%s', kind, Utils.prettyprint(value))
            if kind[0] == '$':
                if kind not in ('$anchor','$optional','$super','$group','$ref','$option','$list'):
                    ctx.setbad()
            else:
                if kind in treex.attributes:
                    cls.selectnode(treex.attributes[kind], value, ctx)
                else:
                    if not value.has('$optional'):
                        ctx.setbad()
        Utils.logger.debug('returns with ctx %s of %s found', ctx.isgood(), ctx.groups)

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
            Utils.logger.debug("Resolving '%s':'%s'", kind, val)
            if kind == '$anchor':
                Utils.logger.debug("Anchor %s to %s detected", val, parent.text)
                anchors[val] = parent
            if kind == '$ref':
                Utils.logger.debug("Reference %s at %s detected", val, parent.text)
                parent.set(kind, anchors[val])

class Constructor:
    @classmethod
    def construct(cls, template, argument):
        Utils.logger.info('Constructing for %s with %s', Utils.prettyprint(template), argument)
        result = cls.constructnode(template, argument)
        Utils.logger.info('Constructing result %s', Utils.prettyprint(result))
        return result

    @classmethod
    def constructnode(cls, template, argument):
        Utils.logger.debug('Constructing node for %s with %s', Utils.prettyprint(template), argument)
        result = Node(template.text)
        if template.text[0] == '$':
            if template.text == '$serial':
                return cls.serial(template, argument)
        if template.text == '$set':
            if isinstance(argument, Node):
                result = argument
            else:
                if template.has('$group'):
                    result.text = argument[template.get('$group').text][0]
                else:
                    result.text = argument
        for kind, value in template.attributes.items():
            if kind not in ('$group'):
                if value == '$set':
                      value = argument
                else:
                      value = cls.constructnode(value, argument)
                result.set( kind, value)
        return result

    @classmethod
    def serial(cls, template, argument):
        Utils.logger.debug('Constructing serial for %s with %s', Utils.prettyprint(template), argument)
        group = argument[template.get('$group').text]
        if len(group) == 0:
            return None
        result = cls.constructnode( template.get('$item'), group[0] )
        node = result
        for i in range(1, len(group)):
            child = cls.constructnode( template.get('$item'), group[i] )
            join = cls.constructnode( template.get('$join'), child )
            for kind, value in join.attributes.items():
                node.set( kind, value)
            node = child
        return result

class Utils:
    @classmethod
    def init(cls):
        if not hasattr(cls, "logger"):
            name = "treex"
            cls.logger = logging.getLogger(name)
            cls.logger.setLevel(logging.WARNING)
            cls.logger.addHandler( cls.getfilehandler(name, "") )

    @classmethod
    def setloglocation(cls, location):
        cls.init()
        for handler in cls.logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                cls.logger.removeHandler(handler)
        cls.logger.addHandler( cls.getfilehandler("treex", location) )

    @classmethod
    def getfilehandler(cls, name, location):
        fh = logging.FileHandler( location + name + '.log', mode='w', delay=True)
        fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(message)s'))
        return fh

    @classmethod
    def fromjson(cls, jstree):
        Utils.logger.debug('from json {0}'.format(jstree))
        if isinstance(jstree, str):
            return Node(jstree)
        else:
            node = Node(jstree[0])
            for ch in jstree[1:]:
                node.set(ch[0], cls.fromjson(ch[1]))
            return node

    @classmethod
    def tojson(cls, treex):
        Utils.logger.debug('to json %s', Utils.prettyprint(treex) )
        if len(treex.attributes) > 0:
            jtree = [ treex.text ]
            for kind, value in treex.attributes.items():
                jvalue = value.text if kind == '$ref' else cls.tojson(value)
                jtree.append( [ kind, jvalue ] )
            return jtree
        return treex.text

    @classmethod
    def load(cls, jstree):
        return cls.fromjson(jstree)

    @classmethod
    def save(cls, treex):
        return cls.tojson(treex)

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

    def __repr__(self):
        return Utils.prettyprint(self)

class MatchingContext:
    def __init__(self):
        self.good = True
        self.groups = { '$root' : MatchingGroup() }
        self.groups['$root'].makeroot()

    def isgood(self):
        return self.good

    def setbad(self):
        self.good = False

    def appendgroup(self, name, value, spr):
        Utils.logger.debug('append group %s with %s, super %s all groups %s', name, value, spr, self.groups)
        if spr not in self.groups:
            self.groups[spr] = self.groups['$root'].addgroup(spr)
        group = self.groups[spr].addgroup(name)
        group.append(value)
        self.groups[name] = group
        Utils.logger.debug('group appended, groups %s', self.groups)

    def leavegroup(self, name):
        Utils.logger.debug('leaving group %s', name)
        if not self.good or name == None:
            return
#        self.groups.pop(name)

    def root(self):
        return self.groups['$root'].toresult()[0] if self.good else None

class MatchingGroup:
    def __init__(self):
        self.values = [ ]
        self.simple = True

    def append(self, value):
        if self.simple:
            self.values.append( value )
        else:
            self.values.append( { '$' : [value] } )

    def addgroup(self, name):
        if self.simple:
            self.convert()
        members = self.values[-1]
        if name not in members:
            members[name] = MatchingGroup()
        return members[name]

    def convert(self):
        for i in range(0, len(self.values)):
            self.values[i] = { '$' : [ self.values[i] ] }
        self.simple = False

    def makeroot(self):
        self.values = [ { } ]
        self.simple = False

    def toresult(self):
        if self.simple:
            return self.values
        result = []
        for x in self.values:
            item = {}
            for name, value in x.items():
                item[name] = value if name == '$' else value.toresult()
            result.append(item)
        return result

    def __repr__(self):
        return str(self.values)