#!/usr/bin/python3

import json
import unittest

class TreexTest(unittest.TestCase):
    def domirror(self, testdef):
        self.assertTrue(True)

if __name__ == '__main__':
    with open('tests.json') as jtests:
        tests = json.load(jtests)
        for t in tests:
            setattr(TreexTest, "test"+t["name"], lambda s: getattr(TreexTest, "do"+t["type"])(s, t))
    unittest.main(verbosity=2)
