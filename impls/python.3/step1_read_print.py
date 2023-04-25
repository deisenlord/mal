
import sys
import re
import reader 
import lisptypes
import printer
import lisp_input

def READ(instr):
	return reader.read_str(instr)

def PRINT(tree):
	printer.pr_str(tree)
	print()
	return tree

def EVAL(tree):
	return tree

def rep(instr):
	return PRINT(EVAL(READ(instr)))


while (True):
	try:
		str = lisp_input.readline("user> ")
		if (str == ''):
			continue
		rep(str)
	except Exception as e:
        	print(e)




