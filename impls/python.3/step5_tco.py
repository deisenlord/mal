
import sys
import re
import reader 
import lisptypes as lisp
import printer
import lisp_input
import env as lispenv
import core

# REP
# (R)ead (E)val (P)rint

def READ(instr):
	return reader.read_str(instr)

def PRINT(tree):
	print(printer.pr_str(tree))
	return tree

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
		elif (lisp.isSymbol(arg1) and arg1.value() == "do"):
			
			ev = eval_ast(lisp.LispList(tree.rest(1)[:-1]), env)

			# Tail call optimization
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

# Built in intrinsic functions
for funcsym in core.ns:
	repl_env.set(funcsym, core.ns[funcsym])

# Built in user defined functions 
EVAL(READ("(def! not (fn* (a) (if a false true)))"), repl_env)

# Yahoo...
while (True):
	try:
		str = lisp_input.readline("user> ")
		if (str == ''):
			continue
		rep(str, repl_env)
	except Exception as e:
        	print(e)




