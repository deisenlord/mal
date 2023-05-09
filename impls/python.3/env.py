#!/usr//bin/python3

import sys
import lisptypes as lisp

#Lisp recursive environments

class Environments:
	def __init__(self, outer = None, binds = [], exprs = []):
		self.outer = outer
		self.data = {}
		for idx in range(len(binds)):
			if (binds[idx] == "&"):
				self.set(binds[idx+1], lisp.LispList(exprs[idx:]))
				return
			else:
				self.set(binds[idx], exprs[idx])

	def _get(self, key):
		return self.data[key]

	def set(self, key, value):
		self.data[key] = value

	def find(self, key):
		if (key in self.data):
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
			raise Exception("'{0}' not found".format(key)) 

	def dump(self, tag):
		print(tag + ":")
		for key, val in self.data.items():
			print(key, val)
		if (self.outer):
		    self.outer.dump("outer")
