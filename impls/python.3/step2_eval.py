
import sys
import re
import reader 
import lisptypes as lisp
import printer
import lisp_input

repl_env = {'+': lambda a,b: a+b,
            '-': lambda a,b: a-b,
            '*': lambda a,b: a*b,
            '/': lambda a,b: int(a/b)}

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
			v = eval_ast(tree, env)
			func = v.value()[0].value()
			return lisp.LispNumber(func(*[arg.value() for arg in v.value()[1:]]))

def eval_ast(ast, env):
	if (lisp.isSymbol(ast)):
		val = env[ast.value()]
		if (val is None):
			raise Exception("Cannot resolve: " + ast.value())
		else:
		    	return lisp.LispNumber(val)
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


while (True):
	try:
		str = lisp_input.readline("user> ")
		if (str == ''):
			continue
		rep(str, repl_env)
	except Exception as e:
        	print(e)




