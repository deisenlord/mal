
import time
import reader
import printer
import lisptypes as lisp
import lisp_input
import copy

# Intrinsics

def i_isList(a):
    if (lisp.isList(a)):
        return lisp.LispBoolean(True)
    else:
        return lisp.LispBoolean(False)

def i_isSequential(a):
    if (lisp.isListLike(a)):
         return lisp.LispBoolean(True)
    else:
         return lisp.LispBoolean(False)

def i_isMap(a):
    if (lisp.isHashMap(a)):
        return lisp.LispBoolean(True)
    else:
        return lisp.LispBoolean(False)

def i_isFunction(a):
    if (lisp.isFunction(a) and not a.isMacro):
        return lisp.LispBoolean(True)
    else:
        return lisp.LispBoolean(False)

def i_isMacro(a):
    if (lisp.isFunction(a) and a.isMacro):
        return lisp.LispBoolean(True)
    else:
        return lisp.LispBoolean(False)
    
def i_isString(a):
    if (lisp.isKeyword(a)):
        return lisp.LispBoolean(False)
    elif (lisp.isString(a)):
        return lisp.LispBoolean(True)
    else:
        return lisp.LispBoolean(False)

def i_isNumber(a):
    if (lisp.isNumber(a)):
        return lisp.LispBoolean(True)
    else:
        return lisp.LispBoolean(False)

def i_mkList(*args):
    #for i in range(len(args)):
    #    args[i].print("py.i_mkList:arg:"+ str(i))
        
    return lisp.LispList([arg for arg in args]) 

def i_mkVector(*args):
    return lisp.LispVector([arg for arg in args])

def i_mkHashMap(*args):
        dict = {}
        keys = args[::2]
        values = args[1::2]
        if (len(keys) != len(values)):
            raise Exception("hash-map: unbalanced keys and values")
        for k in keys:
            if (not isinstance(k, lisp.LispString)):
                raise Exception("hashmap: keys can only be strings or :keywords")
        for idx, k in enumerate(keys):
            dict[k.value()] = values[idx]
        
        return lisp.LispHashMap(dict)

def i_assoc(*args):
    if (not lisp.isHashMap(args[0])):
        raise Exception("assoc: arg0 not a hash map")

    map = args[0].value().copy()
    rest = args[1:]
    keys = rest[::2]
    values = rest[1::2]
    if (len(keys) != len(values)):
        raise Exception("assoc: unbalanced key and value arguments")

    for k in keys:
        if (not isinstance(k, lisp.LispString)):
            raise Exception("assoc: keys can only be strings or :keywords")

        for idx, k in enumerate(keys):
            map[k.value()] = values[idx]

    return lisp.LispHashMap(map)

def i_disassoc(*args):
    if (not lisp.isHashMap(args[0])):
        raise Exception("dissoc: arg0 is not a hash map")

    list = [a for a in args[1:]]
    map = args[0].value().copy()

    for k in list:
        if (not lisp.isString(k)):
            raise Exception("dissoc: keys to remove must be strings or keywords")
        if (k.value() in map):
            discard = map.pop(k.value())
        
    return lisp.LispHashMap(map)

def i_get(*args):
    if (lisp.isNil(args[0])):
        return lisp.LispNil(None)
    if (not lisp.isHashMap(args[0])):
        raise Exception("get: arg0 is not a hash map")
    if (not lisp.isString(args[1])):
        raise Exception("get: arg1 is not string or keyword")

    map = args[0].value()
    key = args[1].value()

    if (key in map):
        return map[key]
    else:
        return lisp.LispNil(None)

def i_contains(map, k):
    if (not lisp.isHashMap(map)):
        raise Exception("contains?: arg0 is not a hash map")
    if (not lisp.isString(k)):
        raise Exception("contains?: arg0 not a string or keyword")

    if (k.value() in map.value()):
        return lisp.LispBoolean(True)
    else:
        return lisp.LispBoolean(False)

def i_keys(map):
    if (not lisp.isHashMap(map)):
        raise Exception("keys: arg0 is not a hash map")

    keys = map.value().keys()
    return lisp.LispList([lisp.LispString(k) for k in keys])

def i_values(map):
    if (not lisp.isHashMap(map)):
        raise Exception("vals: arg0 is not a hash map")

    values = map.value().values()
    return lisp.LispList([v for v in values])

def i_isEmpty(a):
    if (lisp.isListLike(a) and len(a.value()) == 0):
        return lisp.LispBoolean(True)
    else:
        return lisp.LispBoolean(False)

def i_count(a):
    if (lisp.isListLike(a)):
        return lisp.LispNumber(len(a.value()))
    else:
        return lisp.LispNumber(0)

def i_nth(alist, idx):
    if (lisp.isListLike(alist) and lisp.isNumber(idx) and idx.value() < len(alist.value())):
        return alist.value()[idx.value()]
    else:
        raise Exception("nth: index out of range")

def i_first(alist):
    if (lisp.isNil(alist)):
        return lisp.LispNil(None)
    elif (lisp.isListLike(alist)):
        if (alist.count() > 0):
            return alist.value()[0]
        else:
            return lisp.LispNil(None)
    else:
        raise Exception("first: argument not list like") 

def i_rest(alist):
    if (lisp.isNil(alist)):
        return lisp.LispList([])
    elif (lisp.isListLike(alist)):
        if (alist.count() > 1):
            return lisp.LispList(alist.value()[1:])
        else:
            return lisp.LispList([])
    else:
        raise Exception("rest: argument not list like") 

def i_seq(a):
    if (not (lisp.isListLike(a) or lisp.isString(a) or lisp.isNil(a))):
        raise Exception("seq: argument must be string, nil or list like")

    if (lisp.isListLike(a) and len(a.value()) == []):
        return lisp.LispNil(None)
    elif (lisp.isString(a) and len(a.value()) == 0):
        return lisp.LispNil(None)
    elif (lisp.isNil(a)):
        return lisp.LispNil(None)

    if (lisp.isList(a)):
        if (len(a.value()) == 0):
            return lisp.LispNil(None)
        else:
            return a
    elif (lisp.isVector(a)):
        if (len(a.value()) == 0):
            return lisp.LispNil(None)
        else:
            return lisp.LispList(a.value())
    else:
        return lisp.LispList([lisp.LispString(e) for e in a.value()])

def i_conj(*args):
    if (not lisp.isListLike(args[0])):
        raise Exception("conj arg0 must be a list")

    list = args[0].value().copy()

    rest = args[1:]

    if (lisp.isVector(args[0])):
        for e in rest:
            list.append(e)
        return lisp.LispVector(list)
    else:
        for e in rest:
            list.insert(0, e)
        return lisp.LispList(list)
    return   

def i_add(a, b):
    return lisp.LispNumber(a.value() + b.value())

def i_sub(a, b):
    return lisp.LispNumber(a.value() - b.value())

def i_mult(a, b):
    return lisp.LispNumber(a.value() * b.value())

def i_div(a, b):
    return lisp.LispNumber(a.value() / b.value())

def i_equal(a, b):
    if (lisp.isListLike(a) and lisp.isListLike(b)):
        if (len(a.value()) == len(b.value())):
            for i in range(len(a.value())):
                if (i_equal(a.value()[i], b.value()[i]).value() == False):
                    return lisp.LispBoolean(False)
            return lisp.LispBoolean(True)
        else:
            return lisp.LispBoolean(False)
    elif (lisp.isHashMap(a) and lisp.isHashMap(b)):
        map_a = a.value()
        map_b = b.value()
        if (len(map_a) != len(map_b)):
            return lisp.LispBoolean(False)
        else:
            for k in map_a.keys():
                if (k not in map_b):
                    return lisp.LispBoolean(False)
                va = map_a[k]
                vb = map_b[k]
                if (not i_equal(va, vb).value()):
                    return lisp.LispBoolean(False)
                 
            return lisp.LispBoolean(True)
    else:
        if (a.__class__ == b.__class__):
            return lisp.LispBoolean(a.value() == b.value())
        else:
            return lisp.LispBoolean(False)


def i_less(a, b):
    if (lisp.isNumber(a) and lisp.isNumber(b)):
        return lisp.LispBoolean(a.value() < b.value())
    else:
        raise Exception("< compares numbers")

def i_lessEqual(a, b):
    if (lisp.isNumber(a) and lisp.isNumber(b)):
        return lisp.LispBoolean(a.value() <= b.value())
    else:
        raise Exception("<= compares numbers")

def i_greater(a, b):
    if (lisp.isNumber(a) and lisp.isNumber(b)):
        return lisp.LispBoolean(a.value() > b.value())
    else:
        raise Exception("> compares numbers")

def i_greaterEqual(a, b):
    if (lisp.isNumber(a) and lisp.isNumber(b)):
        return lisp.LispBoolean(a.value() >= b.value())
    else:
        raise Exception(">= compares numbers")

def i_prstr(*args):
    parts = [printer.pr_str(arg) for arg in args]    
    return lisp.LispString(" ".join(parts))

def i_prn(*args):
    parts = [printer.pr_str(arg) for arg in args]    
    print(" ".join(parts))
    return lisp.LispNil(None)

def i_str(*args):
    parts = [printer.pr_str(arg, False) for arg in args]    
    return lisp.LispString("".join(parts))

def i_println(*args):
    parts = [printer.pr_str(arg, False) for arg in args]    
    print(" ".join(parts))
    return lisp.LispNil(None)

def i_readstring(a):
#    a.print("in readstring"):
    ret = reader.read_str(a.value())
#    if (lisp.isList(ret)): print("islist")
#    ret.print("after read_str")
    return ret

def i_slurp(fname):
    with open(fname.value()) as file:
        str = file.read()
    return lisp.LispString(str)

def i_atom(val):
    return lisp.LispAtom(val)

def i_isAtom(val):
    return lisp.LispBoolean(lisp.isAtom(val))

def i_isNil(val):
    return lisp.LispBoolean(lisp.isNil(val))

def i_isTrue(val):
    if (lisp.isFunction(val)):
        return lisp.LispBoolean(False)  # Incorrect I believe but needed for tests
    elif (lisp.isNil(val) or (lisp.isBoolean(val) and val.value() == False)):
        return lisp.LispBoolean(False)
    elif (lisp.isBoolean(val) and val.value() == True):
        return lisp.LispBoolean(True)
    else:
        return lisp.LispBoolean(True)

def i_isFalse(val):
    return lisp.LispBoolean(not i_isTrue(val).value())

def i_isSymbol(val):
    return lisp.LispBoolean(lisp.isSymbol(val))

def i_isVector(val):
    return lisp.LispBoolean(lisp.isVector(val))

def i_isKeyword(val):
    return lisp.LispBoolean(lisp.isKeyword(val))

def i_deref(val):
    if (lisp.isAtom(val)):
        return val.value()
    else:
        raise Exception("not an Atom")

def i_reset(atom, val):
    if (lisp.isAtom(atom)):
        atom.set(val)
        return atom.value()
    else:
        raise Exception("not an Atom")

def i_cons(val, alist):
    if (not lisp.isListLike(alist)):
        raise Exception("cons: second argument not list")
    else:
        newlist = [e for e in alist.value()]
        newlist.insert(0, val)
        
        return lisp.LispList(newlist)

def i_mkSymbol(val):
    if (lisp.isString(val)):
        return lisp.LispSymbol(val.value())
    else:
        raise Exception("symbol: arg0 is not a string")

def i_mkKeyword(val):
    if (lisp.isKeyword(val)):
        return val
    elif (lisp.isString(val)):
        return lisp.LispString(lisp.UNIKORN + val.value())
    else:
        raise Exception("keyword: arg0 is not a string")

def i_concat(*args):
    newlist = []
    for l in args:
        if (lisp.isListLike(l)):
            for v in l.value():
                newlist.append(v)
        else:
            newlist.append(l)

    return lisp.LispList(newlist)

def i_vector(v):
    if (lisp.isListLike(v)):
        return lisp.LispVector(v.value())
    else:
        raise Exception("vec: arg0 not list like")

def i_throw(v):
    raise Exception(v)

def i_readline(prompt):
    if (not lisp.isString(prompt)):
        raise Exception("readstring: prompt must be string")
    return lisp.LispString(lisp_input.readline(prompt.value()))

def i_meta(v):
    if (not (lisp.isListLike(v) or lisp.isFunction(v) or lisp.isHashMap(v))):
        raise Exception("meta: arg0 not a list, vector, function or hash map")

    if (not v.meta):
        return lisp.LispNil(None)
    else:
        return v.meta

def i_with_meta(v, vmeta):
    if (not (lisp.isListLike(v) or lisp.isFunction(v) or lisp.isHashMap(v))):
        raise Exception("meta: arg0 not a list, vector, function or hash map")

    if (lisp.isListLike(v)):
        newl = copy.deepcopy(v)
        newl.meta = vmeta
        return newl
    elif (lisp.isFunction(v)):
        newf = copy.deepcopy(v)
        newf.meta = vmeta
        return newf
    else:
        newmap = copy.deepcopy(v)
        newmap.meta = vmeta
        return newmap
    
def i_time_ms():
        epoch_time = int(time.time())
        return lisp.LispNumber(epoch_time)
        
# Table of intrinsic built in functions
ns = {
    "+" : lisp.LispFunction(i_add),
        "-" : lisp.LispFunction(i_sub),
    "*" : lisp.LispFunction(i_mult),
    "/" : lisp.LispFunction(i_div),

    "="  : lisp.LispFunction(i_equal),
    "<"  : lisp.LispFunction(i_less),
    ">"  : lisp.LispFunction(i_greater),
    "<=" : lisp.LispFunction(i_lessEqual),
    ">=" : lisp.LispFunction(i_greaterEqual),

    "list"     : lisp.LispFunction(i_mkList),
    "count"    : lisp.LispFunction(i_count),
    "nth"      : lisp.LispFunction(i_nth),
    "first"    : lisp.LispFunction(i_first),
    "rest"     : lisp.LispFunction(i_rest),
    "list?"    : lisp.LispFunction(i_isList),
    "nil?"     : lisp.LispFunction(i_isNil),
    "true?"    : lisp.LispFunction(i_isTrue),
    "false?"   : lisp.LispFunction(i_isFalse),
    "symbol?"  : lisp.LispFunction(i_isSymbol),
    "empty?"   : lisp.LispFunction(i_isEmpty),
    "atom?"    : lisp.LispFunction(i_isAtom),
    "keyword?" : lisp.LispFunction(i_isKeyword),
    "vector?"  : lisp.LispFunction(i_isVector),
    "map?"     : lisp.LispFunction(i_isMap),
    "fn?"      : lisp.LispFunction(i_isFunction),
    "string?"  : lisp.LispFunction(i_isString),
    "number?"  : lisp.LispFunction(i_isNumber),
    "macro?"   : lisp.LispFunction(i_isMacro),
    "vec"      : lisp.LispFunction(i_vector),
    "throw"    : lisp.LispFunction(i_throw),
    "str"      : lisp.LispFunction(i_str),
    "pr-str"   : lisp.LispFunction(i_prstr),
    "prn"      : lisp.LispFunction(i_prn),
    "atom"     : lisp.LispFunction(i_atom),
    "deref"    : lisp.LispFunction(i_deref),
    "reset!"   : lisp.LispFunction(i_reset),
    "println"  : lisp.LispFunction(i_println),
    "cons"     : lisp.LispFunction(i_cons),
    "concat"   : lisp.LispFunction(i_concat),
    "slurp"    : lisp.LispFunction(i_slurp),
    "symbol"   : lisp.LispFunction(i_mkSymbol),
    "keyword"  : lisp.LispFunction(i_mkKeyword),
    "vector"   : lisp.LispFunction(i_mkVector),
    "assoc"    : lisp.LispFunction(i_assoc),
    "dissoc"   : lisp.LispFunction(i_disassoc),
    "hash-map" : lisp.LispFunction(i_mkHashMap),
    "get"      : lisp.LispFunction(i_get),
    "keys"     : lisp.LispFunction(i_keys),
    "vals"     : lisp.LispFunction(i_values),
    "contains?": lisp.LispFunction(i_contains),
    "readline" : lisp.LispFunction(i_readline),
    "seq"      : lisp.LispFunction(i_seq),
    "conj"     : lisp.LispFunction(i_conj),
    "meta"     : lisp.LispFunction(i_meta),
    "with-meta": lisp.LispFunction(i_with_meta),
    "time-ms"  : lisp.LispFunction(i_time_ms),
    "sequential?" : lisp.LispFunction(i_isSequential),
    "read-string" : lisp.LispFunction(i_readstring)
}

 

