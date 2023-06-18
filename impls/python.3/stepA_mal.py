
import sys, traceback
import copy
import re
import reader 
import lisptypes as lisp
import printer
import lisp_input
import env as lispenv
import core

sys.setrecursionlimit(8000)

# Quoting support
def quasiquote(tree):
    if (lisp.isList(tree) and tree.count() == 0):
        return tree
    elif (lisp.isList(tree) and tree.first().value() == "unquote"):
        return tree.second()
    elif (lisp.isList(tree) or lisp.isVector(tree)):
        newtree = lisp.LispList([])
        for i in reversed(range(len(tree.value()))):
            el = tree.value()[i]
            if (lisp.isList(el) and el.count() > 0 and el.first().value() ==  "splice-unquote"):
                newtree = lisp.LispList([lisp.LispSymbol("concat"), el.second(), newtree]) 
            else:
                newtree = lisp.LispList([lisp.LispSymbol("cons"), quasiquote(el), newtree])
        if (lisp.isVector(tree)):
            newtree = lisp.LispList([lisp.LispSymbol("vec"), newtree])
        return newtree
    elif (lisp.isSymbol(tree) or lisp.isHashMap(tree)):
        x = lisp.LispList([lisp.LispSymbol("quote"), tree])
        return x
    else:
        return tree

def is_macro_call(tree, env):
    if (lisp.isList(tree) and lisp.isSymbol(tree.first())):
        if (env.find(tree.first().value()) == None):
            return False
        
        f = env.get(tree.first().value())
        if (lisp.isFunction(f) and f.isMacro):
            return True
        else:
            return False
    else:
        return False

def macroexpand(tree, env):
    while(is_macro_call(tree, env)):
        f = env.get(tree.first().value())    
        tree = f.call(EVAL, *[arg for arg in tree.value()[1:]])
    
    return tree

# REP
# (R)ead (E)val (P)rint

def READ(instr):
    return reader.read_str(instr)

def PRINT(tree):
    return printer.pr_str(tree)

def nsfixup(body, env):
    if (env.nsname == 'user'): 
        return
    
    if (lisp.isSymbol(body)):
        body.setvalue(env.qualify(body.value()))
        return

    for e in body.value():
        if (lisp.isSymbol(e) and env.find(env.qualify(e.value())) != None):
            e.setvalue(env.qualify(e.value()))
        elif (lisp.isListLike(e)):
            nsfixup(e, env)

def EVAL(tree, env):
    #print("py(EVAL)", printer.pr_str(tree))

    while (True):

        if (not lisp.isList(tree)):
            return eval_ast(tree, env)

        if (tree.count() == 0):
            return tree

        # Macro expansion
        tree = macroexpand(tree, env)
        if (not lisp.isList(tree)):
            return eval_ast(tree, env)

        # Apply phase
        arg1 = tree.first()
        if (lisp.isSymbol(arg1) and arg1.value() == "def!"):
            key = tree.second().value()
            val = EVAL(tree.third(), env)
            env.set(env.qualify(key), val)
            if (lisp.isSymbol(val) or (lisp.isFunction(val) and not val.intrinsic)):
                nsfixup(val.val, env)
            return val
        elif (lisp.isSymbol(arg1) and arg1.value() == "ns"):
            ns = tree.second()
            if (lisp.isSymbol(ns)):
                nsenv = lispenv.Environments(env, ns = ns.value())
                ev = eval_ast(lisp.LispList(tree.rest(2)), nsenv)
                env.nsinstall(nsenv)
                return lisp.LispNil(None)
            else:
                raise Exception("ns: arg0 must be a symbol")       
        elif (lisp.isSymbol(arg1) and arg1.value() == "defmacro!"):
            key = tree.second().value()
            val = EVAL(tree.third(), env)
            newval = val
            if (lisp.isFunction(val)):
                newval = copy.deepcopy(val)
                newval.isMacro = True
            else:
                raise Exception("defmacro!: second argument not a function")
            env.set(env.qualify(key), newval)
            return val
        elif (lisp.isSymbol(arg1) and arg1.value() == "macroexpand"):
            return macroexpand(tree.second(), env)
        elif (lisp.isSymbol(arg1) and arg1.value() == "let*"):
            newenv = lispenv.Environments(env)
            bindlist = tree.second()
            if (not (lisp.isList(bindlist) or lisp.isVector(bindlist))):
                raise Exception("let* bindlist isn't list or vector")
            keys = bindlist.value()[::2]
            rawvals = bindlist.value()[1::2]
            if (len(keys) != len(rawvals)):
                raise Exception("let* unbalanced keys and values")
            for idx, k in enumerate(keys):
                val = EVAL(rawvals[idx], newenv)
                newenv.set(k.value(), val)

            # TCO: return EVAL(tree.third(), newenv)
            env = newenv
            tree = tree.third()
        elif (lisp.isSymbol(arg1) and arg1.value() == "quote"): 
            return tree.second()
        elif (lisp.isSymbol(arg1) and arg1.value() == "quasiquote"):
            return EVAL(quasiquote(tree.second()), env)
            #tree = tree.second()
        elif (lisp.isSymbol(arg1) and arg1.value() == "quasiquoteexpand"):
            return quasiquote(tree.second())
        elif (lisp.isSymbol(arg1) and arg1.value() == "do"):
            ev = eval_ast(lisp.LispList(tree.rest(1)[:-1]), env)
            
            # TCO: return EVAL(tree.value()[-1], env)
            tree = tree.value()[-1]
        elif (lisp.isSymbol(arg1) and arg1.value() == "try*"):
            value_expr = tree.second()
            if(tree.count() <=2):
                tree = EVAL(value_expr, env)
            else:
                catch_list = tree.third()

                if (not (lisp.isList(catch_list) and lisp.isSymbol(catch_list.first()) and catch_list.first().value() == "catch*")):
                    raise Exception("mal: try*/catch*: malformed")

                catch_form = catch_list.third()
                evar = catch_list.second()
                if (not lisp.isSymbol(evar)):
                    raise Exception("mal: try*/catch*: malformed")

                try:
                    return EVAL(value_expr, env)
                except Exception as e:
                    # Exception could be native to python or by i_throw(lispobject)
                    if (isinstance(e.args[0], str)):
                        e = lisp.LispString(e.args[0])
                    elif (isinstance(e.args[0], lisp.LispException)):
                        e = e.args[0].malobject
                    elif (lisp.isLispType(e.args[0])):
                        e = e.args[0]
                    else:
                        e = lisp.LispString("mal: Internal error, unknown exception type")
                    cenv = lispenv.Environments(env, [evar.value()], [e])    
                    return EVAL(catch_form, cenv)
        elif (lisp.isSymbol(arg1) and arg1.value() == "if"):
            cond = EVAL(tree.second(), env)
            if (not (cond.value() == None or (lisp.isBoolean(cond) and cond.value() == False))):
                # TCOL return EVAL(tree.third(), env)
                tree = tree.third()
            elif (len(tree.value()) == 4):
                # TCO: return EVAL(tree.value()[3], env)
                tree = tree.value()[3]
            else:
                return lisp.LispNil(None)
        elif (lisp.isSymbol(arg1) and arg1.value() == "while"):
            condition = tree.second()
            body = tree.third()
            evcond = EVAL(condition, env)
            while (not (evcond.value() == None or (lisp.isBoolean(evcond) and evcond.value() == False))):
                ret = EVAL(body, env)
                evcond = EVAL(condition, env)

            return ret
        elif (lisp.isSymbol(arg1) and arg1.value() == "fn*"):
            dummys = tree.second().value()
            body = tree.third()
            #if (env.nsname != 'user'):
            #    env = env.outer
            ret = lisp.LispFunction(body, env, [b.value() for b in dummys], intrinsic = False)
            return ret
        else:
            v = eval_ast(tree, env)
            f = v.first()
            if (lisp.isFunction(f) and f.intrinsic):
                func = f.pyfunc()
                return func(*[arg for arg in v.value()[1:]])
            elif (lisp.isFunction(f)):
                if (f.trace):   # No TCO if tracing
                    return f.call(EVAL, *[arg for arg in v.value()[1:]])
                else:
                    # TCO
                    env = lispenv.Environments(f.outer, f.dummys, [arg for arg in v.value()[1:]])
                    tree = f.body()
                # No TCO, because how to do tracing ?
                #return f.fn(EVAL, *[arg for arg in v.value()[1:]])
            else:
                raise Exception("mal:: Expected function, got '" + printer.pr_str(f) + "'")

def eval_ast(ast, env):
    #print("py(eval_ast)", printer.pr_str(ast))
    if (lisp.isSymbol(ast)):
        val = env.get(ast.value())
        if (val is None):
            raise Exception("mal: Cannot resolve: " + ast.value())
        else:
            return val
    elif (lisp.isList(ast)):
        evald = lisp.LispList([EVAL(e, env) for e in ast.value()])
        return evald
    elif (lisp.isVector(ast)):
        return lisp.LispVector([EVAL(e, env) for e in ast.value()])
    elif (lisp.isHashMap(ast)):
        newmap = {}
        keys = ast.value().keys()
        for key in keys:
            newmap[key] = EVAL(ast.value().get(key), env)
        return lisp.LispHashMap(newmap)
    else:
        return ast

def rep(instr, env):
    tree = READ(instr)
    return PRINT(EVAL(tree, env))

# Root environment
repl_env = lispenv.Environments(None, ns = "user")

# Alias map for namespace aliases via nsalias
nsalias = lispenv.globalAliases

#
# Lisp intrinsics requiring EVAL, otherwise would be in core.py
def evil(tree, env):
    return EVAL(tree, env)

def i_swap(*args):
    atom = args[0]
    func = args[1]
    if (not lisp.isAtom(atom)):
        raise Exception("swap: arg1 not an atom")
    if (not lisp.isFunction(func)):
        raise Exception("swap: arg2 not a function")

    arglist = [atom.value()]
    for a in args[2:]:
        arglist.append(a)

    if (func.intrinsic):
        atom.set(func.value()(*arglist))
        return atom.value()
    else:
        env = lispenv.Environments(func.outer, func.dummys, arglist)
        atom.set(evil(func.body(), env))
        return atom.value()

def i_apply(*args):
    if (not lisp.isFunction(args[0])):
        raise Exception("apply: arg0 not a function")
        
    # sort out arguments
    f = args[0]
    list0 = []
    if (len(args) == 2):
        if (not lisp.isListLike(args[1])):
           raise Exception("apply: second argument not a list")
        list = args[1]
    else:
        
        if (not lisp.isListLike(args[-1])):
            raise Exception("apply: last argument not a list")
        list = args[-1]
        list0 = [arg for arg in args[1:-1]]

    for e in list.value():
        list0.append(e)

    # apply function to argument list
    if (f.intrinsic):
        func = f.value()        
        return func(*[a for a in list0])
    else:
        newenv = lispenv.Environments(f.outer, f.dummys, [a for a in list0])
        return evil(f.body(), newenv)

def i_map(*args):
    if (not lisp.isFunction(args[0])):
        raise Exception("map: arg0 not a function")
    if (not lisp.isListLike(args[1])):
        raise Exception("map: arg1 not list like")

    f = args[0]
    inputs = args[1]

    outputs = []
    if (f.intrinsic):
        func = f.value()
        for a in inputs.value():
            outputs.append(func(a))
    else:
        for a in inputs.value():
            newenv = lispenv.Environments(f.outer, f.dummys, [a])
            outputs.append(evil(f.body(), newenv))

    return lisp.LispList(outputs)
        
def i_quasiquote(tree):
    return quasiquote(tree.second())

def i_nsalias(orig, alias):
    if (not lisp.isSymbol(orig)):
        raise Exception("ns-alias: arg0 (orig) not a symbol")
    if (not lisp.isSymbol(alias)):
        raise Exception("ns-alias: arg1 (alias) not a symbol")
    
    nsalias.create(orig.value(), alias.value())
    return lisp.LispNil(None)

def i_nsall():
    repl_env.nsprint()
    return lisp.LispNil(None)

def i_nsdir(*args):
    ns = "user"
    if (len(args) == 1 and lisp.isSymbol(args[0])):
        ns = args[0].value()
    elif (len(args) != 0):
        raise Exception("ns-dir: takes zero or one namespace symbol")
    
    repl_env.nsdir(ns)
    return lisp.LispNil(None)

def i_printaliases():
    nsalias.dump()
    return lisp.LispNil(None)

# Add evil and swap to envronment
repl_env.set("eval",      lisp.LispFunction(lambda tree: evil(tree, repl_env)))
repl_env.set("swap!",     lisp.LispFunction(i_swap))
repl_env.set("quasiquoteexpand", lisp.LispFunction(i_quasiquote))
repl_env.set("apply",     lisp.LispFunction(i_apply))
repl_env.set("map",       lisp.LispFunction(i_map))

# Namespace, env
repl_env.set("ns-alias",   lisp.LispFunction(i_nsalias))
repl_env.set("ns-dir",     lisp.LispFunction(i_nsdir))
repl_env.set("ns-all",     lisp.LispFunction(i_nsall))
repl_env.set("ns-aliases", lisp.LispFunction(i_printaliases))


# Built in intrinsic functions
for funcsym in core.ns:
    repl_env.set(funcsym, core.ns[funcsym])

# Built-in variables*
repl_env.set("*ARGV*", lisp.LispList([]))
repl_env.set("*host-language*", lisp.LispString("python3 DJE 2023"))
repl_env.set("*ns*", lisp.LispHashMap({}))

# Built in user defined functions 
EVAL(READ("(def! not (fn* (a) (if a false true)))"), repl_env)
EVAL(READ('(def! load-file (fn* (f) (eval (read-string (str "(do " (slurp f) "\nnil)")))))'), repl_env)
EVAL(READ("(defmacro! cond (fn* (& xs) (if (> (count xs) 0) (list 'if (first xs) (if (> (count xs) 1) (nth xs 1) (throw \"odd number of forms to cond\")) (cons 'cond (rest (rest xs)))))))"), repl_env)

# Additional bootstrap lisp code
EVAL(READ('(if (fileexists? "./bootstrap.mal") (load-file "./bootstrap.mal") (load-file "/usr/local/lib/mal/bootstrap.mal"))'), repl_env)

# Yahoo...

if (len(sys.argv) > 1):
    fname = sys.argv[1]
    try:
        argv = []
        for a in sys.argv[2:]:
            argv.append(lisp.LispString(a))

        if (len(argv) > 0):
            repl_env.set("*ARGV*", lisp.LispList(argv))
            
        rep("(load-file \"{0}\")".format(fname), repl_env)
        sys.exit(0)
    except Exception as e:
        if (isinstance(e, lisp.LispException)):
            print(printer.pr_str(e.malobject))
        else:
            print(e.args[0])
else:
    rep('(println (str "Mal [" *host-language* "]"))', repl_env)
    while (True):
        try:
            instr = lisp_input.readline(repl_env.nsname + "> ")
            if (instr == ""):
                continue
            if (instr == None):
                print("EOF bye")
                sys.exit(0)
            print(rep(instr, repl_env))
        except reader.BlankLine: 
            continue
        except Exception as e:
            if (isinstance(e, lisp.LispException)):
                print(printer.pr_str(e.malobject))
            else:
                print(e.args[0])



