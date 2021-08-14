#!/usr/bin/python3

import json
from treex import Treex

class TreexTest():
    def __init__(self):
        self.good = 0
        self.fail = 0

    def domirror(self, testdef):
        source = Treex.fromjson(testdef["source"])
        self.assertTrue(Treex.match(source, source))

    def donegmirror(self, testdef):
        source = Treex.fromjson(testdef["source"])
        query = Treex.fromjson(testdef["query"])
        self.assertFalse(Treex.match(source, query))

    def dosimple(self, testdef):
        source = Treex.fromjson(testdef["source"])
        if "srccontext" in testdef:
            source = Treex.apply(Treex.fromjson(testdef["srccontext"]), source)
        query = Treex.fromjson(testdef["query"])
        self.assertTrue(Treex.match(source, query))

    def doselect(self, testdef):
        source = Treex.fromjson(testdef["source"])
        if "srccontext" in testdef:
            source = Treex.apply(Treex.fromjson(testdef["srccontext"]), source)
        query = Treex.fromjson(testdef["query"])
        self.assertResult(Treex.select(source, query), testdef["result"])

    def doconstruct(self, testdef):
        template = Treex.fromjson(testdef["template"])
        self.assertEqual(Treex.construct(template, testdef["argument"]), Treex.fromjson(testdef["result"]))

    def run(self, tests):
        for t in tests:
            if ("active" not in t) or (t["active"]):
                func = getattr(TreexTest, "do"+t["type"])
                self.current = t
                print("Running {0}".format(t["name"] ))
                func(self, t)
        print("Total good: {0}, failed: {1}".format(self.good, self.fail))

    def assertTrue(self, value):
        if value:
            self.good = self.good + 1
            return True
        else:
            self.fail = self.fail + 1
            print("Test {0} failed".format(self.current["name"]))
            return False

    def assertFalse(self, value):
        return self.assertTrue(not value)

    def assertEqual(self, treex, etalon):
        if self.assertTrue(Treex.match(treex, etalon)):
            self.assertTrue(Treex.match(etalon, treex))

    def assertResult(self, select, etalon):
        if select is None:
            self.assertTrue(False)
            return
        final = True
        for group, value in etalon.items():
            if group not in select:
                final = False
            else:
                final = final and (value == select[group])
        for group, _ in select.items():
            final = final and (group in etalon)
        self.assertTrue(final)

if __name__ == '__main__':
    with open('tests.json') as jtests:
        tests = json.load(jtests)
    runner = TreexTest()
    runner.run(tests)
