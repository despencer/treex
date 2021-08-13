# treex

Tree expressions (similar to regular expressions)

## Result creation

Let's suppose we have a following list of commands (parent group, group, value) or leaving group:

1. $root, arg, arg
2. arg, name, x
3. arg, kind, type
4. arg, value, int
5. arg, kind, value
6. arg, value, 8
7. leaving arg
8. $root, arg, arg
9. arg, name, y
10. arg, kind, type
11. arg, value, str
12. arg, kind, value
13. arg, value, zz
14. leaving arg

So, during processing we have the following:
1. { arg:[arg] }
2. { arg:[ {$:[arg], name:[x]} ] }
3. { arg:[ {$:[arg], name:[x], kind:[type] } ] }
4. { arg:[ {$:[arg], name:[x], kind:[type], value:[int] } ] }
5. { arg:[ {$:[arg], name:[x], kind:[type, value], value:[int] } ] }
6. { arg:[ {$:[arg], name:[x], kind:[type, value], value:[int, 8] } ] }
7. { arg:[ {$:[arg], name:[x], kind:[type, value], value:[int, 8] } ] }
8. { arg:[ {$:[arg], name:[x], kind:[type, value], value:[int, 8] } , arg] }
9. { arg:[ {$:[arg], name:[x], kind:[type, value], value:[int, 8] } , {$:[arg], name:[y] }] }