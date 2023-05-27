#!/usr//bin/python3

import sys
import lisptypes as lisp
import printer

#Lisp recursive environments
class Environments:
    def __init__(self, outer = None, binds = [], exprs = [], ns = ''):
        self.outer = outer
        self.data = {}
        self.ns = ns
        for idx in range(len(binds)):
            if (binds[idx] == "&"):
                self.set(binds[idx+1], lisp.LispList(exprs[idx:]))
                return
            else:
                self.set(binds[idx], exprs[idx])

    def setns(self, ns):
        self.ns = ns

    def getns(self):
        return self.ns

    def qualify(self, name):
        if (self.ns != 'user' and "/" not in name):
            return self.ns + "/" + name
        else:
            return name

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
        key = globalAliases.alias(key)
        if (self.ns != 'user' and "/" not in key):
            ev = self.find(self.qualify(key))
            if (ev != None):
                return ev._get(self.qualify(key))
            else:
                ev = self.find(key)
        else:
            ev = self.find(key)

        if (ev != None):
            return ev._get(key)
        else:
            raise Exception("mal: '{0}' not found".format(key)) 

    def findroot(self):
        if (self.ns == 'user'):
            return self
        else:
            root = self.outer
            while (root.ns != 'user'):
                root = root.outer
            return root

    def findhead(self):
        root = self.findroot()
        while (root.outer != None):
            root = root.outer

        return root

    def nsinstall(self, env):
        head = self.findhead()
        env.outer = None
        head.outer = env
	
    def nspropagate(self):
        root = self.outer
        while (root.outer != None):
            root = root.outer

        for k in self.data.keys():
            root.data[k] = self.data[k]

    def dump(self):
        print("NS(" + self.ns + "):")
        for key, val in self.data.items():
            print(key + " : " + printer.pr_str(val))
        if (self.outer):
            self.outer.dump()


# Global Namespace aliases
class Aliases:
    def __init__(self):
        self.map = {}

    def create(self, orig, alias):
        self.map[alias] = orig

    def alias(self, sym):
        if ("/" in sym):
            symparts = sym.split("/")
            if (symparts[0] in self.map):
                return self.map[symparts[0]] + "/" + symparts[1]
            else:
                return sym
        else:
            return sym

    def dump(self):
        for key, val in self.map.items():
            print(key + " -> " + val)


# Global alias table
globalAliases = Aliases()


            
        
