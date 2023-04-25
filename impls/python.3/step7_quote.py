
import sys, traceback
import re
import reader 
import lisptypes as lisp
import printer
import lisp_input
import env as lispenv
import core

# Quoting support
def quasiquote(tree):
	if (lisp.isList(tree) and tree.count() == 0):
		#tree.print("empty")
		return tree
	elif (lisp.isList(tree) and tree.first().value() == "unquote"):
		#tree.print("unquote")
		return tree.second()
	elif (lisp.isList(tree) or lisp.isVector(tree)):
		newtree = lisp.LispList([])
		for i in reversed(range(len(tree.value()))):
			el = tree.value()[i]
			#el.print("elem[" + str(i) + "]")
			if (lisp.isList(el) and el.count() > 0 and el.first().value() ==  "splice-unquote"):
				newtree = lisp.LispList([lisp.LispSymbol("concat"), el.second(), newtree]) 
			else:
				newtree = lisp.LispList([lisp.LispSymbol("cons"), quasiquote(el), newtree])
		if (lisp.isVector(tree)):
			newtree = lisp.LispList([lisp.LispSymbol("vec"), newtree])
		#newtree.print("newlist")
		return newtree
	elif (lisp.isSymbol(tree) or lisp.isHashMap(tree)):
		x = lisp.LispList([lisp.LispSymbol("quote"), tree])
		#x.print("sym or hashmap")
		return x
	else:
		#tree.print("default")
		return tree

# REP
# (R)ead (E)val (P)rint

def READ(instr):
	return reader.read_str(instr)

def PRINT(tree):
	return printer.pr_str(tree)

def EVAL(tree, env):
	while (True):
		if (not lisp.isList(tree)):
			return eval_ast(tree, env)
		
		if (tree.count() == 0):
			return tree
				
		# Apply phase
		arg1 = tree.first()
		if (lisp.isSymbol(arg1) and arg1.value() == "def!"):
			key = tree.second().value()
			val = EVAL(tree.third(), env)
			env.set(key, val)
			return val
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

			# Tail call optimization
			env = newenv
			tree = tree.third()
		elif (lisp.isSymbol(arg1) and arg1.value() == "quote"): 
			return tree.second()
		elif (lisp.isSymbol(arg1) and arg1.value() == "quasiquote"):
			#tree.print("before")
			tree = quasiquote(tree.second())
			#tree.print("after")
			# TCO
		elif (lisp.isSymbol(arg1) and arg1.value() == "quasiquoteexpand"):
			return quasiquote(tree.second())
		elif (lisp.isSymbol(arg1) and arg1.value() == "do"):
			ev = eval_ast(lisp.LispList(tree.rest(1)[:-1]), env)

			# TCO: Tail call optimization
			tree = tree.value()[-1]
		elif (lisp.isSymbol(arg1) and arg1.value() == "if"):
			cond = EVAL(tree.second(), env)
			if (not (cond.value() == None or (lisp.isBoolean(cond) and cond.value() == False))):
				tree = tree.third()
			elif (len(tree.value()) == 4):
				# Forth list element: else clause
				tree = tree.value()[3]
			else:
				tree = lisp.LispNil(None)
		elif (lisp.isSymbol(arg1) and arg1.value() == "fn*"):
			dummys = tree.second().value()
			body = tree.third()
			ret = lisp.LispFunction(body, env, [b.value() for b in dummys], intrinsic = False)
			return ret
		else:
			v = eval_ast(tree, env)
			f = v.first()
			if (lisp.isFunction(f) and f.isIntrinsic()):
				func = f.value()
				return func(*[arg for arg in v.value()[1:]])
			else:
				# TCO
				env = lispenv.Environments(f.outer(), f.dummys, [arg for arg in v.value()[1:]])
				tree = f.body()

def eval_ast(ast, env):
	if (lisp.isSymbol(ast)):
		val = env.get(ast.value())
		if (val is None):
			raise Exception("Cannot resolve: " + ast.value())
		else:
		    	return val
	elif (lisp.isList(ast)):
		evald = lisp.LispList([EVAL(e, env) for e in ast.value()])
		return evald
	elif (lisp.isVector(ast)):
		#ast.print("eval vector")
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
repl_env = lispenv.Environments(None)

# Lisp intrinsics requiring EVAL
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
	if (len(args) == 3):
		arglist.append(args[2])
	if (func.isIntrinsic()):
		atom.set(func.value()(*arglist))
		return atom.value()
	else:
		env = lispenv.Environments(func.outer(), func.dummys, arglist)
		atom.set(evil(func.body(), env))
		return atom.value()

def i_quasiquote(tree):
	return quasiquote(tree.second())

# Add evil and swap to envronment
repl_env.set("eval",  lisp.LispFunction(lambda tree: evil(tree, repl_env)))
repl_env.set("swap!", lisp.LispFunction(i_swap))
repl_env.set("quasiquoteexpand", lisp.LispFunction(i_quasiquote))

# Built in intrinsic functions
for funcsym in core.ns:
	repl_env.set(funcsym, core.ns[funcsym])

# *ARGV*
repl_env.set("*ARGV*", lisp.LispList([]))

# Built in user defined functions 
EVAL(READ("(def! not (fn* (a) (if a false true)))"), repl_env)
EVAL(READ('(def! load-file (fn* (f) (eval (read-string (str "(do " (slurp f) "\nnil)")))))'), repl_env)

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
		print("".join(traceback.format_exception(*sys.exc_info())))
else:
	while (True):
		try:
			instr = lisp_input.readline("user> ")
			if (instr == ""):
				continue
			print(rep(instr, repl_env))
		except reader.BlankLine: 
			continue
		except Exception as e:
			print("".join(traceback.format_exception(*sys.exc_info())))



