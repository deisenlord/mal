#!/usr//bin/python3

import sys
import lisptypes as lisp
import printer

#Lisp recursive environments

class Namespaces:
    def __init__(self, init = []):
        self.ns = init

    def push(self, ns):
        self.ns.append(ns)

    def pop(self):
        if (len(self.ns) > 0):
            return self.ns.pop()
        else:
            return ''

    def current(self):
        if (len(self.ns) > 0):
            return self.ns[-1]
        else:
            return ''

# Namespace stack
ns = Namespaces()

class Environments:
	def __init__(self, outer = None, binds = [], exprs = []):
		self.outer = outer
		self.nsname = None      
		self.data = {}
		for idx in range(len(binds)):
			if (binds[idx] == "&"):
				self.set(binds[idx+1], lisp.LispList(exprs[idx:]))
				return
			else:
				self.set(binds[idx], exprs[idx])

	def setns(self, nsname):
		self.nsnme = nsname

	def _nskey(self, key): 
		if (self.nsname != None):
			prefix = self.ns.current()
			if (len(prefix) > 0):
				return prefix + "/" + key
			else:
				return key
		else:
			return key
       
	def _get(self, key):
		return self.data[self._nskey(key)]

	def set(self, key, value):
		self.data[self._nskey(key)] = value

	def find(self, key):
		if (self._nskey(key) in self.data):
			return self
		else:
			if (self.outer == None):
				return None 
			else:
				return self.outer.find(key)

	def get(self, key):
		ev = self.find(key)
		if (ev != None):
			return ev._get(key)
		else:
			raise Exception("mal: '{0}' not found".format(key)) 

	def dump(self):
		print("NS(" + str(self.nsname) + "):")
		for key, val in self.data.items():
			print(key + " : " + printer.pr_str(val))
		if (self.outer):
		    self.outer.dump()
