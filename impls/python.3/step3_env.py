
import sys
import re
import reader 
import lisptypes as lisp
import printer
import lisp_input
import env as lispenv

def READ(instr):
	return reader.read_str(instr)

def PRINT(tree):
	print(printer.pr_str(tree))
	return tree

def EVAL(tree, env):
	if (not lisp.isList(tree)):
		return eval_ast(tree, env)
	else:
		if (not len(tree.value())):
		    return tree
		else:
			# Apply phase
			if (lisp.isSymbol(tree.value()[0]) and tree.value()[0].value() == "def!"):
				key = tree.value()[1].value()
				val = EVAL(tree.value()[2], env)
				env.set(key, val)
				return val
			elif (lisp.isSymbol(tree.value()[0]) and tree.value()[0].value() == "let*"):
				newenv = lispenv.Environments(env)
				bindlist = tree.value()[1]
				if (not (lisp.isList(bindlist) or lisp.isVector(bindlist))):
					raise Exception("let* bindlist isn't list or vector")
				keys = bindlist.value()[::2]
				rawvals = bindlist.value()[1::2]
				if (len(keys) != len(rawvals)):
                        		raise Exception("let* unbalanced keys and values")
				for idx, k in enumerate(keys):
					val = EVAL(rawvals[idx], newenv)
					newenv.set(k.value(), val)

				# Result
				return EVAL(tree.value()[2], newenv)
			else:
				v = eval_ast(tree, env)
				func = v.value()[0].value()
				return lisp.LispNumber(func(*[arg.value() for arg in v.value()[1:]]))

def eval_ast(ast, env):
	if (lisp.isSymbol(ast)):
		val = env.get(ast.value())
		if (val is None):
			raise Exception("Cannot resolve: " + ast.value())
		else:
		    	return val
	elif (lisp.isList(ast)):
		return lisp.LispList([EVAL(e, env) for e in ast.value()])
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
repl_env.set("+", lisp.LispBuiltIn(lambda a,b: a+b))
repl_env.set("-", lisp.LispBuiltIn(lambda a,b: a-b))
repl_env.set("*", lisp.LispBuiltIn(lambda a,b: a*b))
repl_env.set("/", lisp.LispBuiltIn(lambda a,b: int(a/b)))

# Yahoo...
while (True):
	try:
		str = lisp_input.readline("user> ")
		if (str == ''):
			continue
		rep(str, repl_env)
	except Exception as e:
        	print(e)




