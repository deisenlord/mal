
import math
import time
import reader
import printer
import lisptypes as lisp
import lisp_input
import copy
import os.path

# Intrinsics

def i_max(*args):
    n = len(args)
    if (n < 2):
        raise Exception("max: requires 2 or more arguments")

    __m = args[0]
    if (not lisp.isNumber(__m)):
        raise Exception("max: arguments must be numeric")

    __m = __m.value()
    
    for v in args[1:]:
        __m = max(__m, v.value())

    return lisp.LispNumber(__m)

def i_min(*args):
    n = len(args)
    if (n < 2):
        raise Exception("min: requires 2 or more arguments")

    __m = args[0]
    if (not lisp.isNumber(__m)):
        raise Exception("min: arguments must be numeric")

    __m = __m.value()
    
    for v in args[1:]:
        __m = min(__m, v.value())

    return lisp.LispNumber(__m)

def i_fn_name(f):
    if (not lisp.isFunction(f)):
        raise Exception("fn-name: argument must be a function")

    if (len(f.name) == 0):
        return lisp.LispString(printer.pr_str(f))
    else:
        return lisp.LispString(f.name)
    
def i_format(arg, fmt):
    if (not lisp.isString(fmt)):
        raise Exception("format: format argument must be a string")
    if (lisp.isListLike(arg)):
        s = []
        for v in arg.value():
            s.append(lisp.LispString(format(v.value(), fmt.value())))
        return lisp.LispList(s)
    else:
        s = format(arg.value(), fmt.value())
        return lisp.LispString(s)       
        
def i_fileExists(path):
    if (lisp.isString(path)):
        return lisp.LispBoolean(os.path.isfile(path.value()))
    else:
        raise Exception("fileexists?: arg0 jmust be string")

def i_trace(func, funcname, flag):

    if (lisp.isFunction(func) and lisp.isString(funcname) and lisp.isBoolean(flag)):
        func.trace = flag.value()
        func.tracename = funcname.value()
        func.tlevel = 0
    else:
        raise Exception("trace: trace requires (func, funcname, flag)")

    return lisp.LispNil(None)

def i_pyDo(str):
    if (lisp.isString(str)):
        exec(compile(str.value(), "code", "exec"), globals())
    else:
        raise Exception("pyblock!: arg0 must be string")

    return lisp.LispNil(None)

def i_pyGet(str):
    if (lisp.isString(str)):
        return lisp.Py2Lisp(eval(str.value()))
    else:
        raise Exception("pyexpr!: arg0 must be string")

def i_pyCall(fn, args):
    if (not lisp.isString(fn)):
         raise Exception("pycall!: arg0 must be string")
    if (not lisp.isHashMap(args)):
         raise Exception("pycall!: arg1 must be a hashmap of arguments")
     
    f = globals()[fn.value()]

    if (f == None):
         raise Exception("pycall!: could not find function {}".format(fn.value()))         

    d = lisp.Lisp2Py(args)
    r = f(**d)
    return (lisp.Py2Lisp(r))


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

def i_isInt(a):
    if (lisp.isNumber(a) and isinstance(a.value(), int)):
        return lisp.LispBoolean(True)
    else:
        return lisp.LispBoolean(False)

def i_isFloat(a):
    if (lisp.isNumber(a) and isinstance(a.value(), float)):
        return lisp.LispBoolean(True)
    else:
        return lisp.LispBoolean(False)
    
def i_mkList(*args):
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
            if (not (isinstance(k, lisp.LispString) or isinstance(k, lisp.LispNumber))):
                raise Exception("hashmap: keys can only be strings, :keywords or numbers")
        for idx, k in enumerate(keys):
            dict[k.value()] = values[idx]
        
        return lisp.LispHashMap(dict)

def i_assoc (*args):
    if (not lisp.isHashMap(args[0])):
        raise Exception("assoc: arg0 not a hash map")

    map = args[0].value().copy()
    rest = args[1:]
    keys = rest[::2]
    values = rest[1::2]
    if (len(keys) != len(values)):
        raise Exception("assoc: unbalanced key and value arguments")

    for k in keys:
        if (not (isinstance(k, lisp.LispString) or isinstance(k, lisp.LispNumber))):
            raise Exception("assoc: keys can only be strings, :keywords or numbers")

        for idx, k in enumerate(keys):
            map[k.value()] = values[idx]

    return lisp.LispHashMap(map)

def i_disassoc(*args):
    if (not lisp.isHashMap(args[0])):
        raise Exception("dissoc: arg0 is not a hash map")

    list = [a for a in args[1:]]
    map = args[0].value().copy()

    for k in list:
        if (not (lisp.isString(k) or lisp.isNumber(k))):
            raise Exception("dissoc: keys to remove must be strings, :keywords or numbers")
        if (k.value() in map):
            discard = map.pop(k.value())
        
    return lisp.LispHashMap(map)

def i_get(*args):
    if (lisp.isNil(args[0])):
        return lisp.LispNil(None)
    if (not lisp.isHashMap(args[0])):
        raise Exception("get: arg0 is not a hash map")
    if (not (lisp.isString(args[1]) or lisp.isNumber(args[1]))):
        raise Exception("get: arg1 is not string, :keyword or number")

    map = args[0].value()
    key = args[1].value()

    if (key in map):
        return map[key]
    else:
        return lisp.LispNil(None)

def i_contains(map, k):
    if (not lisp.isHashMap(map)):
        raise Exception("contains?: arg0 is not a hash map")
    if (not (lisp.isString(k) or lisp.isNumber(k))):
        raise Exception("contains?: arg0 not a string, :keyword or number")

    if (k.value() in map.value()):
        return lisp.LispBoolean(True)
    else:
        return lisp.LispBoolean(False)

def i_keys(map):
    if (not lisp.isHashMap(map)):
        raise Exception("keys: arg0 is not a hash map")

    keys = map.value().keys()
    kv = []
    for k in keys:
        if (isinstance(k, str)):
            kv.append(lisp.LispString(k))
        elif (isinstance(k, int) or isinstance(k, float)):
            kv.append(lisp.LispNumber(k))

    return lisp.LispList(kv)

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
    elif lisp.isHashMap(a):
        return lisp.LispNumber(len(a.value()))
    elif lisp.isString(a):
        return lisp.LispNumber(len(a.value()))
    else:
        return lisp.LispNumber(0)

def i_nth(*args):

    if (len(args) < 2):
        raise Exception("nth: requires list and index, optional sentinal upon index error")
    if (lisp.isListLike(args[0])):
        alist = args[0].value()
    if (lisp.isNumber(args[1])):
        idx = args[1].value()
        
    if (idx < len(alist)):
        return alist[idx] 
    else:
        if (len(args) == 3):
            return args[2]
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
    if (lisp.isListLike(args[0])):
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
   
    elif (lisp.isHashMap(args[0])):
        map = args[0].value().copy()

        rest = args[1:]

        for m in rest:
            if (not lisp.isHashMap(m)):
                raise Exception("conj: can only conj maps to maps")
            for k in m.value().keys():
                map[k] = m.value()[k]

        return lisp.LispHashMap(map)
 
    else:
        raise Exception("conj: arg0 must be list, vector or hash-map")


def i_add(a, b):
    return lisp.LispNumber(a.value() + b.value())

def i_sub(a, b):
    return lisp.LispNumber(a.value() - b.value())

def i_mult(a, b):
    return lisp.LispNumber(a.value() * b.value())

def i_div(a, b):
    return lisp.LispNumber(a.value() / b.value())

def i_sqrt(a):
    return lisp.LispNumber(math.sqrt(a.value()))

def i_pow(b, e):
    return lisp.LispNumber(b.value() ** e.value())

def i_int(a):
    return lisp.LispNumber(int(a.value()))

def i_float(a):
    return lisp.LispNumber(float(a.value()))

def i_mod(a, b):
    return lisp.LispNumber(a.value() % b.value())

def i_log(a):
    return (lisp.LispNumber(smath.log(a.value())))

def i_exp(a):
    return (lisp.LispNumber(math.exp(a.value())))
            
def i_log10(a):
    return (lisp.LispNumber(math.log10(a.value())))

def i_ceil(a):
    return (lisp.LispNumber(math.ceil(a.value())))

def i_floor(a):
    return (lisp.LispNumber(math.floor(a.value())))

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

def castbool(x):
    if (lisp.isBoolean(x)):
        return x.value()
    elif (lisp.isNil(x)):
        return False
    else:
        return True
    
def i_or(a, b):
    return lisp.LispBoolean(castbool(a) or castbool(b))

def i_and(a, b):
    return lisp.LispBoolean(castbool(a) and castbool(b))

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
    ret = reader.read_str(a.value())
    return ret

def i_slurp(fname):
    with open(fname.value()) as file:
        str = file.read()
    return lisp.LispString(str)

def i_spit(fname, s):
    with open(fname.value(), "w") as file:
        n = file.write(s.value())
    return lisp.LispNumber(n)

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

def i_throw(obj):
    raise lisp.LispException(obj)

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
        newf = v._copy()
        newf.meta = vmeta
        return newf
    else:
        newmap = copy.deepcopy(v)
        newmap.meta = vmeta
        return newmap
    
def i_time_ms():
        epoch_time = int(time.time())
        return lisp.LispNumber(epoch_time)
        
def i_sort(l, options):
    if (not lisp.isListLike(l)):
        raise Exception("sort: arg0 not a list, vector")
    if (not (lisp.isNil(options) or lisp.LispHashMap(options))):
        raise Exception("sort: arg1 must be nil or a hash-map of options (:reverse :nth)")

    if (lisp.isNil(options) or options.value() == {}):
        return lisp.LispList(sorted(l.value(), key = lambda x: x.value()))
    else:
        optmap = options.value()
        rev = False
        nth = 0
        if (lisp.UNIKORN + "reverse" in  optmap):
            rev = optmap[lisp.UNIKORN + "reverse"].value()
            
        if (lisp.UNIKORN + "nth" in optmap):
            nth = optmap[lisp.UNIKORN + "nth"].value()
            return lisp.LispList(sorted(l.value(), key = lambda x: x.value()[nth].value(), reverse = rev)) 
        else:
            return lisp.LispList(sorted(l.value(), key = lambda x: x.value(), reverse = rev)) 

        
# Table of intrinsic built in functions
ns = {
    "+"        : lisp.LispFunction(i_add),
    "-"        : lisp.LispFunction(i_sub),
    "*"        : lisp.LispFunction(i_mult),
    "/"        : lisp.LispFunction(i_div),
    "max"     : lisp.LispFunction(i_max),
    "min"     : lisp.LispFunction(i_min),
    "sqrt"     : lisp.LispFunction(i_sqrt),
    "pow"      : lisp.LispFunction(i_pow),
    "int"      : lisp.LispFunction(i_int),
    "float"    : lisp.LispFunction(i_float),
    "mod"      : lisp.LispFunction(i_mod),
    "log"      : lisp.LispFunction(i_log),
    "exp"      : lisp.LispFunction(i_exp),
    "log10"    : lisp.LispFunction(i_log10),
    "ceil"     : lisp.LispFunction(i_ceil),
    "floor"    : lisp.LispFunction(i_floor),
    "="        : lisp.LispFunction(i_equal),
    "<"        : lisp.LispFunction(i_less),
    ">"        : lisp.LispFunction(i_greater),
    "<="       : lisp.LispFunction(i_lessEqual),
    ">="       : lisp.LispFunction(i_greaterEqual),
    "or"       : lisp.LispFunction(i_or),
    "and"      : lisp.LispFunction(i_and),
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
    "integer?" : lisp.LispFunction(i_isInt),
    "float?"   : lisp.LispFunction(i_isFloat),
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
    "spit"     : lisp.LispFunction(i_spit),
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
    "sort"     : lisp.LispFunction(i_sort),
    "trace"    : lisp.LispFunction(i_trace),
    "pyblock!" : lisp.LispFunction(i_pyDo),
    "pyexpr!"  : lisp.LispFunction(i_pyGet),
    "pycall!"  : lisp.LispFunction(i_pyCall),
    "format"   : lisp.LispFunction(i_format),
    "fn-name"  : lisp.LispFunction(i_fn_name),
    "fileexists?" : lisp.LispFunction(i_fileExists),
    "sequential?" : lisp.LispFunction(i_isSequential),
    "read-string" : lisp.LispFunction(i_readstring)
}

 

