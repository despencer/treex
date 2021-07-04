#!/usr/bin/python3

import json
from treex import Treex
import unittest

class TreexTest(unittest.TestCase):
    def domirror(self, testdef):
        source = Treex.fromjson(testdef["source"])
        self.assertTrue(Treex.match(source, source))

    def donegmirror(self, testdef):
        source = Treex.fromjson(testdef["source"])
        target = Treex.fromjson(testdef["target"])
        self.assertFalse(Treex.match(source, target))

if __name__ == '__main__':
    with open('tests.json') as jtests:
        tests = json.load(jtests)
        for t in tests:
            setattr(TreexTest, "test"+t["name"], lambda s: getattr(TreexTest, "do"+t["type"])(s, t))
    unittest.main(verbosity=2)
