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
        target = Treex.fromjson(testdef["target"])
        self.assertFalse(Treex.match(source, target))

    def run(self, tests):
        for t in tests:
            if ("active" not in t) or (t["active"]):
                func = getattr(TreexTest, "do"+t["type"])
                self.current = t
                print("Running {0}".format(t["name"] ))
                func(self, t)
        print("Total good: {0}, failed: {1}".format(self.good, self.failed))

    def assertTrue(self, value):
        if value:
            self.fail = self.fail + 1
            print("Test {0} failed".format(self.current["name"]))
        else:
            self.good = self.good + 1

    def assertFalse(self, value):
        assertTrue(not value)

if __name__ == '__main__':
    with open('tests.json') as jtests:
        tests = json.load(jtests)
    runner = TreexTest()
    runner.run(tests)
