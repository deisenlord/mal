
import re
import lisptypes as lisp
import printer

import pdb 

class BlankLine(Exception):
    pass

class Readers:
    def __init__(self, tokens):
        self.tokens = tokens    
        self.length = len(tokens)
        self.index = 0

    def next(self):
        if (self.index < self.length):
            ret = self.tokens[self.index]
            self.index = self.index + 1
            return ret
        else:
            return None

    def peek(self):
        if (self.index < self.length):
            return self.tokens[self.index]
        else:
            return None

def read_str(instr):
    tokens = tokenize(instr)
    if (len(tokens) == 0):
        raise BlankLine("BlankLine")
    return read_form(Readers(tokens))

def read_form(rdr):
    if (rdr.peek() == '('):
        types = read_list(rdr)
    elif (rdr.peek() == ';'):
        rdr.next() 
        types = None
    elif (rdr.peek() == '['):
        types = read_vector(rdr)
    elif (rdr.peek() == '{'):
        types = read_hashmap(rdr)
    elif (rdr.peek() == "'"):
        rdr.next()
        types = lisp.LispList([lisp.LispSymbol("quote"), read_form(rdr)])
    elif (rdr.peek() == "@"):
        rdr.next()
        types = lisp.LispList([lisp.LispSymbol("deref"), read_form(rdr)])
    elif (rdr.peek() == "^"):
        rdr.next()
        one = read_form(rdr)
        two = read_form(rdr)
        types = lisp.LispList([lisp.LispSymbol("with-meta"), two, one])
    elif (rdr.peek() == "`"):
        rdr.next()
        types = lisp.LispList([lisp.LispSymbol("quasiquote"), read_form(rdr)])
    elif (rdr.peek() == "~"):        
        rdr.next()
        types = lisp.LispList([lisp.LispSymbol("unquote"), read_form(rdr)])
    elif (rdr.peek() == "~@"):
        rdr.next()
        types = lisp.LispList([lisp.LispSymbol("splice-unquote"), read_form(rdr)])
    else:
        types = read_atom(rdr)

    return types

def read_list(rdr):
    return read_list_type(rdr, '(', ')')

def read_vector(rdr):
    return read_list_type(rdr, '[', ']')

def read_hashmap(rdr):
    return read_list_type(rdr, '{', '}')

def read_list_type(rdr, start, end):
    types = []
    tok = rdr.next()
    if (tok != start): raise Exception("mal: expected starting '" + start + "'")

    tok = rdr.peek()
    while (tok != end):
        if (not tok):
            raise Exception("mal: expected ending '" + end + "' got EOF")
        form = read_form(rdr)
        types.append(form)
        tok = rdr.peek()

    rdr.next()
    if (start == '('):
        return lisp.LispList(types)
    elif (start == '['):
        return lisp.LispVector(types)
    elif (start == '{'):
        dict = {}
        keys = types[::2]
        values = types[1::2]
        if (len(keys) != len(values)):
            raise Exception("mal: Hashmap unbalanced keys and values")
        for k in keys:
            if (not isinstance(k, lisp.LispString)):
                raise Exception("mal: Hash map keys can only be strings or :keywords")
        for idx, k in enumerate(keys):
            dict[k.value()] = values[idx]
        
        return lisp.LispHashMap(dict)
    else:
        raise Exception("mal: Unkown list starting type: ", start)

def unescape(s):
    return s.replace('\\\\', '\u029e').replace('\\"', '"').replace('\\n', '\n').replace('\u029e', '\\')

def read_atom(rdr):
    val = None
    int_re = re.compile(r"-?[0-9]+$")
    str_re = re.compile(r'"(?:[\\].|[^\\"])*"')
    float_re = re.compile(r"-?[0-9][0-9.]*$")

    tok = rdr.next()
    
    if (tok == None):
        return None
    elif (int_re.match(tok)):
        num = int(tok)
        val = lisp.LispNumber(num)
    elif (float_re.match(tok)):
        num = int(float(tok))
        val = lisp.LispNumber(num)
    elif (tok == "nil"):
        val = lisp.LispNil(None)
    elif (tok == "true"):
        val = lisp.LispBoolean(True)
    elif (tok == "false"):
        val = lisp.LispBoolean(False)
    elif (str_re.match(tok)):
        val = lisp.LispString(unescape(tok[1:-1])) 
    elif (tok[0] == '"'):
        raise Exception("mal: unbalanced quotes")
    elif (tok[0] == ':'):
        val = lisp.LispString(lisp.UNIKORN + tok[1:])
    else:
        val = lisp.LispSymbol(tok)
    return val

def tokenize(str):
    tre = re.compile(r"""[\s,]*(~@|[\[\]{}()'`~^@]|"(?:[\\].|[^\\"])*"?|;.*|[^\s\[\]{}()'"`@,;]+)""");
    toks = [t for t in re.findall(tre, str) if t[0] != ';']
    return toks
