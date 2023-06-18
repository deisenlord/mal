#!/usr//bin/python3

import sys
import lisptypes as lisp
import printer

#Lisp recursive environments
class Environments:
    def __init__(self, outer = None, binds = [], exprs = [], ns = ''):
        self.outer = outer
        self.data = {}
        self.nsname = ns
        self.nslist = {}
        for idx in range(len(binds)):
            if (binds[idx] == "&"):
                self.set(binds[idx+1], lisp.LispList(exprs[idx:]))
                return
            else:
                self.set(binds[idx], exprs[idx])

    def qualify(self, name):
        if (self.nsname != 'user' and "/" not in name):
            return self.nsname + "/" + name
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
        if (self.nsname != 'user' and "/" not in key):
            ev = self.find(self.qualify(key))
            if (ev):
                return ev._get(self.qualify(key))
            
            ev = self.find(key)
            if (ev):
                return ev._get(key)
            
        elif ("/" in key and len(key) > 1):
            parts = key.split("/")
            ev = self.findroot().nslist[parts[0]]
            if (ev):
                ev = ev.find(key)
                if (ev):
                    return ev._get(key)
            else:
                raise Exception("mal: namespace '{0}' not found".format(parts[0]))

        else:
            ev = self.find(key)
            if (ev != None):
                return ev._get(key)
        
        raise Exception("mal: '{0}' not found".format(key)) 

    def findroot(self):
        root = self
        while (root.outer != None):
            root = root.outer
        
        return root

    def nsinstall(self, env):
        root = self.findroot()
        env.outer = root
        root.nslist[env.nsname] = env

    def nsprint(self):
        keys = self.nslist.keys()
        print("Namespaces:")
        print("user")
        for s in keys:
            if (s): print(s)
        
    def nsdir(self, ns):
        map = None
        if (ns == "user"):
            map = self.data
        else:
            env = self.nslist[ns]
            if (env != None):
                map = env.data

        if (map):
            print("NS(" + ns + "):")
            for (key, val) in map.items():
                if (key): print(key + " : " + val.typestr())


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


            
        
