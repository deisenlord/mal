
# Cribbed, not sure why keywords need a unicode prefix.
UNIKORN = "\u029e"

import copy
import env as lispenv
import printer
import time

class SourceLocation:
    def __init__(self, line, source):
        self.line = line
        self.source = source

def errmsg(loc, msg):
    src = loc.source
    i = loc.source.rfind("/")
    if (i > 0):
        src = loc.source[i+1:]

    return "[" + src + "(" + str(loc.line) + ")] " + msg

class LispException(Exception):
    def __init__(self, object):
        self.malobject = object
    
class LispTypes:
    def __init__(self, val, location = SourceLocation(1, "Unknown")):
        self.val = val
        self.loc = location
        self.meta = None
        
    def value(self):
        return self.val
    def print(self,  tag):
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
    def typestr(self): return "list"
    
    def first(self):
        if (len(self.val) >= 1):
            return self.val[0]
        else:
            raise Exception("first: empty list, no first element")

    def second(self):
        if (len(self.val) >= 2):
            return self.val[1]
        else:
            raise Exception("second: no second element")

    def third(self):
        if (len(self.val) >= 3):
            return self.val[2]
        else:
            raise Exception("third: no third element")

    def rest(self, start):
        if (len(self.val) >= start+1):
            return self.val[start:]
        else:
            return lisp.LispList([])
    
    def count(self):
        return len(self.val)

class LispVector(LispTypes):
    def typestr(self): return "vector"
    
    def first(self):
        if (len(self.val) >= 1):
            return self.val[0]
        else:
            raise Exception("first: empty vector, no first element")

    def second(self):
        if (len(self.val) >= 2):
            return self.val[1]
        else:
            raise Exception("second: no second element")

    def third(self):
        if (len(self.val) >= 3):
            return self.val[2]
        else:
            raise Exception("third: no third element")

    def rest(self, start):
        if (len(self.val) >= start+1):
            return self.val[start:]
        else:
            return lisp.LispList([])

    def count(self):
        return len(self.val)

class LispHashMap(LispTypes):
    def typestr(self): return "hashmap"

class LispNumber(LispTypes):
    def typestr(self) :return "number"

class LispSymbol(LispTypes):
    def typestr(self): return "symbol"
    def setvalue(self, newval):
        self.val = newval

class LispString(LispTypes):
    def typestr(self): return "string"

class LispNil(LispTypes):
    def typestr(self): return "nil"

class LispBoolean(LispTypes):
    def typestr(self): return "boolean"

def trace_call(name, level, args):
    for i in range(level-1):
        print("  ", end="")
    argstr = ",".join([printer.pr_str(x) for x in args])
    print(("{0}: (" + name + " {1} )").format(level-1, argstr))

def trace_return(name, level, ret):
    for i in range(level-1):
        print("  ", end="")
    print(("{0}:" + name + " returned ({1})").format(level-1, printer.pr_str(ret)))
    
class LispFunction(LispTypes):
    def __init__(self, val, outer = None, bindvars = [], intrinsic = True, macro = False, location = SourceLocation(1, "internal-bootstrap")):
        self.val = val
        self.loc = location
        self.dummys = bindvars
        self.outer = outer
        self.intrinsic = intrinsic
        self.isMacro = macro
        self.meta = None
        self.trace = False
        self.tracename = ""
        self.tlevel = 0
        self.name = ""

    def _copy(self):
        cp = LispFunction(copy.deepcopy(self.val))
        cp.loc = self.loc
        cp.dummys = self.dummys[:]
        cp.outer = self.outer
        cp.intrinsic = self.intrinsic
        cp.isMacro = self.isMacro
        cp.meta = copy.deepcopy(self.meta)

        return cp
        
    def typestr(self):
        if (self.intrinsic):
            return "builtin function"
        elif (self.isMacro):
            return "macro"
        else:
            return "user function"
    
    # self.val is either a python function or a user defined function body
    def body(self):
        return self.val
    def pyfunc(self):
        return self.val

    def call(self, evil, *args):
        if (self.trace):
            self.tlevel = self.tlevel + 1
            trace_call(self.tracename, self.tlevel, args) 

        funcenv = lispenv.Environments(self.outer, [d for d in self.dummys], [x for x in args])        
        ret = evil(self.body(), funcenv)
                       
        if (self.trace):
            trace_return(self.tracename, self.tlevel, ret)
            self.tlevel = self.tlevel - 1
                       
        return ret

class LispAtom(LispTypes):
    def typestr(self): return "atom"
    def set(self, val):
        self.val = val

# Python type to MAL type
def Py2Lisp(pyobj):
    if (type(pyobj) == list):
        l = [Py2Lisp(o) for o in pyobj]
        return LispList(l)
    elif (type(pyobj) == tuple):
        return Py2Lisp(list(pyobj))
    elif (type(pyobj) == dict):
        hm = {}
        for k in pyobj.keys():
            hm[k] = Py2Lisp(pyobj[k])
        return LispHashMap(hm)
    elif (type(pyobj) == int or type(pyobj) == float):
        return LispNumber(pyobj)
    elif (type(pyobj) == str):
        return LispString(pyobj)
    elif (type(pyobj) == type(None)):
        return LispNil(None)
    elif (type(pyobj) == bool):
        return LispBoolean(pyobj)
    elif (type(pyobj) == time.struct_time):
        return LispNumber(time.mktime(pyobj))
    else:
        raise Exception("mal: Unsupported python type " + str(type(pyobj)) + " in conversion")

# MAL type to python type
def Lisp2Py(lobj):
    if (isListLike(lobj)):
        return [Lisp2Py(o) for o in lobj.value()]
    elif (isHashMap(lobj)):
        hm = {}
        for k in lobj.value().keys():
            if (isinstance(k, str) and k[0] == UNIKORN):
                ks = k[1:]
            else:
                ks = k
            hm[ks] = Lisp2Py(lobj.value()[k])
        return hm
    elif (isNumber(lobj)):
        return lobj.value()
    elif (isKeyword(lobj)):
        return printer.pr_str(lobj)
    elif (isString(lobj)):
        return lobj.value()
    elif (isNil(lobj)):
        return None
    elif (isBoolean(lobj)):
        return lobj.value()
    else:
        raise Exception("mal: Unsupported MAL type " + lobj.typesstr() + " in conversion")
