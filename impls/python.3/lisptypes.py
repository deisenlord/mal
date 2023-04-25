
# Cribbed, not sure why keywords need a unicode prefix.
UNIKORN = "\u029e"

import env as lispenv
import printer

class LispTypes:
    def __init__(self, val):
        self.val = val
        self.meta = None
        
    def value(self):
        return self.val
    def print(self, tag):
        print(tag + ": " + printer.pr_str(self))
    def __str__(self):
        return printer.pr_str(self)
    
def isLispType(t):
    return isinstance(t, LispTypes)

def isList(t):
    return isinstance(t, LispList)

def isVector(t):
    return isinstance(t, LispVector)

def isListLike(t):
    return isList(t) or isVector(t)

def isHashMap(t):
    return isinstance(t, LispHashMap)

def isSymbol(t):
    return isinstance(t, LispSymbol)

def isFunction(t):
    return isinstance(t, LispFunction)

def isBoolean(t):
    return isinstance(t, LispBoolean)

def isNumber(t):
    return isinstance(t, LispNumber)

def isNil(t):
    return isinstance(t, LispNil)

def isString(t):
    return isinstance(t, LispString)

def isAtom(t):
    return isinstance(t, LispAtom)

def isKeyword(t):
    return isinstance(t, LispString) and len(t.value()) > 0 and t.value()[0] == UNIKORN

# ----------

class LispList(LispTypes):
    def first(self):
        if (len(self.val) >= 1):
            return self.val[0]
        else:
            raise Exception("empty list, no first element")

    def second(self):
        if (len(self.val) >= 2):
            return self.val[1]
        else:
            raise Exception("no second element")

    def third(self):
        if (len(self.val) >= 3):
            return self.val[2]
        else:
            raise Exception("no third element")

    def rest(self, start):
        if (len(self.val) >= start+1):
            return self.val[start:]
        else:
            return lisp.LispList([])
    
    def count(self):
        return len(self.val)

class LispVector(LispTypes):
    def first(self):
        if (len(self.val) >= 1):
            return self.val[0]
        else:
            raise Exception("empty list, no first element")

    def second(self):
        if (len(self.val) >= 2):
            return self.val[1]
        else:
            raise Exception("no second element")

    def third(self):
        if (len(self.val) >= 3):
            return self.val[2]
        else:
            raise Exception("no third element")

    def rest(self, start):
        if (len(self.val) >= start+1):
            return self.val[start:]
        else:
            return lisp.LispList([])

    def count(self):
        return len(self.val)

class LispHashMap(LispTypes):
    pass

class LispNumber(LispTypes):
    pass

class LispSymbol(LispTypes):
    pass

class LispString(LispTypes):
    pass

class LispNil(LispTypes):
    pass

class LispBoolean(LispTypes):
    pass

class LispFunction(LispTypes):
    def __init__(self, val, outer = None, bindvars = [], intrinsic = True, macro = False):
        self.val = val
        self.dummys = bindvars
        self.out = outer
        self.intrinsic = intrinsic
        self.isMacro = macro
        self.meta = None
        
    def isIntrinsic(self):
        return self.intrinsic

    def body(self):
        return self.val

    def dummys(self):
        return self.dummys

    def outer(self):
        return self.out

    def fn(self, evil, *args):
        funcenv = lispenv.Environments(self.out, [d for d in self.dummys], [x for x in args])        
        ret = evil(self.val, funcenv)
        return ret

    def call(self, *args):
        if (self.intrinsic):
            f = self.val
            return f(*[arg for arg in args])
        else:
            return fn(xxx, args)

class LispAtom(LispTypes):
    def set(self, val):
        self.val = val


