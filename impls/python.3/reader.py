
import re
import lisptypes as lisp
import printer

import pdb 

class BlankLine(Exception):
    pass
        
class Token(str):
    def __new__(cls, t):
        instance = super().__new__(cls, t)
        return instance

    def __init(self):
        self.loc = lisp.SourceLocation(0, "Unknown") 

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

def read_str(instr, source = "Unknown"):
    tokens = tokenize(instr, source)
    if (len(tokens) == 0):
        raise BlankLine("BlankLine")
    return read_form(Readers(tokens))

def read_form(rdr):
    loc = rdr.peek().loc
    if (rdr.peek() == '('):
        types = read_list(rdr)
    elif (rdr.peek() == ';'):
        rdr.next()
        loc = rdr.peek().loc        
        types = None
    elif (rdr.peek() == '['):
        types = read_vector(rdr)
    elif (rdr.peek() == '{'):
        types = read_hashmap(rdr)
    elif (rdr.peek() == "'"):
        rdr.next()
        loc = rdr.peek().loc
        types = lisp.LispList([lisp.LispSymbol("quote", loc), read_form(rdr)], loc)
    elif (rdr.peek() == "@"):
        rdr.next()
        loc = rdr.peek().loc
        types = lisp.LispList([lisp.LispSymbol("deref", loc), read_form(rdr)], loc)
    elif (rdr.peek() == "^"):
        rdr.next()
        loc = rdr.peek().loc
        one = read_form(rdr)
        two = read_form(rdr)
        types = lisp.LispList([lisp.LispSymbol("with-meta", loc), two, one], loc)
    elif (rdr.peek() == "`"):
        rdr.next()
        loc = rdr.peek().loc
        types = lisp.LispList([lisp.LispSymbol("quasiquote", loc), read_form(rdr)], loc)
    elif (rdr.peek() == "~"):
        rdr.next()
        loc = rdr.peek().loc
        types = lisp.LispList([lisp.LispSymbol("unquote", loc), read_form(rdr)], loc)
    elif (rdr.peek() == "~@"):
        rdr.next()
        loc = rdr.peek().loc
        types = lisp.LispList([lisp.LispSymbol("splice-unquote", loc), read_form(rdr)], loc)
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
    loc = tok.loc
    if (tok != start):
        raise Exception(lisp.errmsg(loc, "mal: expected starting '" + start + "'"))
    
    tok = rdr.peek()
    while (tok != end):
        if (not tok): 
            raise Exception(lisp.errmsg(loc, "mal: expected ending '" + end + "' got EOF"))
        else:
            loc = tok.loc
        form = read_form(rdr)
        types.append(form)
        tok = rdr.peek()

    rdr.next()
    if (start == '('):
        return lisp.LispList(types, loc)
    elif (start == '['):
        return lisp.LispVector(types, loc)
    elif (start == '{'):
        dict = {}
        keys = types[::2]
        values = types[1::2]
        if (len(keys) != len(values)):
            raise Exception(lisp.errmsg(loc, "mal: Hashmap unbalanced keys and values"))
        for k in keys:
            if (not (isinstance(k, lisp.LispString) or isinstance(k, lisp.LispNumber))):
                raise Exception(lisp.errmsg(loc, "mal: Hash map keys can only be strings, :keywords or numbers"))
        for idx, k in enumerate(keys):
            dict[k.value()] = values[idx]
        
        return lisp.LispHashMap(dict, loc)
    else:
        raise Exception(lisp.errmsg(loc, "mal: Unkown list starting type: " +  start))

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
        val = lisp.LispNumber(num, tok.loc)
    elif (float_re.match(tok)):
        num = float(tok)
        val = lisp.LispNumber(num, tok.loc)
    elif (tok == "nil"):
        val = lisp.LispNil(None, tok.loc)
    elif (tok == "true"):
        val = lisp.LispBoolean(True, tok.loc)
    elif (tok == "false"):
        val = lisp.LispBoolean(False, tok.loc)
    elif (str_re.match(tok)):
        val = lisp.LispString(unescape(tok[1:-1]), tok.loc) 
    elif (tok[0] == '"'):
        raise Exception(lisp.errmsg(loc, "mal: unbalanced quotes"))
    elif (tok[0] == ':'):
        val = lisp.LispString(lisp.UNIKORN + tok[1:], tok.loc)
    else:
        val = lisp.LispSymbol(tok, tok.loc)
    return val


def match_with_line_numbers(pattern, string, flags=0):

    matches = list(re.finditer(pattern, string, flags))
    if not matches:
        return []

    for m in matches:
        end = string[0:m.end()].count("\n")
        yield (m.group(0),  end)

def tokenize(str, source):
    
    pat = r"""[\s,]*(~@|[\[\]{}()'`~^@]|"(?:[\\].|[^\\"])*"?|;.*|[^\s\[\]{}()'"`@,;]+)"""
    
    pairs = match_with_line_numbers(pat, str, flags=re.MULTILINE)

    toks = []
    for m in pairs:
            t = Token(m[0].strip())
            
            if (t[0] != ';'):
                location = lisp.SourceLocation(m[1]+1, source)
                t.loc = location
                toks.append(t)
                
    return toks
