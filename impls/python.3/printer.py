
import lisptypes as lisp 


# cribed from example
def escape(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def pr_str(tree, readable = True):
    if (lisp.isNumber(tree)):
        return str(tree.value())
    elif (lisp.isSymbol(tree)):
        return str(tree.value()) 
    elif (lisp.isNil(tree)):
        return "nil"
    elif (isinstance(tree, lisp.LispBoolean)):
        return str(tree.value()).lower()
    elif (isinstance(tree, lisp.LispString)):
        if (len(tree.value()) > 0 and tree.value()[0] == lisp.UNIKORN):
            return ":" + tree.value()[1:]
        elif readable:
            s = escape(tree.value())
            return '"' + s + '"'
        else:
            return tree.value()
    elif (isinstance(tree, lisp.LispList)):
        s = "("
        first = True
        for elem in tree.value():
            if (not first):
                s = s + " "
            s = s + pr_str(elem, readable)
            first = False
        return s + ")"
    elif (isinstance(tree, lisp.LispVector)):
        s = "["
        first = True
        for elem in tree.value():
            if (not first):
                s = s + " "
            s = s + pr_str(elem, readable)
            first = False
        return s + "]"
    elif (isinstance(tree, lisp.LispHashMap)):
        s = "{"
        first = True
        for k, v in tree.value().items():
            if (not first):
                s = s + " "
            if (k[0] == lisp.UNIKORN):
                s = s +  ":" + k[1:]
            else:
                s = s + '"' + k + '"'
            s = s + " "
            s = s + pr_str(v, readable)
            first = False
        return s + "}"
    elif (lisp.isFunction(tree)):
        return pr_str(tree.value(), False)
    elif (lisp.isAtom(tree)):
        return "(atom " + pr_str(tree.value()) + ")"
    else:
        return str(tree.value()) # ??? error 

