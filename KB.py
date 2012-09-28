import sys

class Size():
    def __init__(self, expression):
        self.lemma = ""
        if expression == ('over', 0):
            self.lemma = "small"
        if expression == ('over', 1):
            self.lemma = "big"
        if expression == (('ind', 'y'), 0):
            self.lemma = "short"
        if expression == (('ind', 'y'), 1):
            self.lemma = "tall"
        if expression == (('ind', 'x'), 0):
            self.lemma = "thin"
        if expression == (('ind', 'x'), 1):
            self.lemma = "fat"

class Prototypes():
    def __init__(self):
        fid = open("KB-Data/objects", "r")
        in_file = fid.readlines()
        fid.close()
        self.protohash = {}
        self.read(in_file)
        self.implies = {}
        self.interconnections = {}
        self.read_interconnections()

    def read(self, in_file):
        for line in in_file:
            split_line = line.split()
            obj = split_line[0]
            self.protohash[obj] = {}
            self.protohash[obj]['type'] = obj
            for att_val in split_line[1:]:
                av = att_val.split(":")
                att = av[0]
                val = av[1]
                num = av[2]
                try:
                    self.protohash[obj][att][val] = float(num)
                except KeyError:
                    self.protohash[obj][att] = {val:float(num)}

    def find_category(self, object):
        # Ideally, we'd be able to *figure out* the type
        # Here, we're given it, so the input is all correct.
        cat_type = object['type']
        try:
            return self.protohash[cat_type]
        except KeyError:
            return None

    def read_interconnections(self):
        self.interconnections['material'] = ('colour', 'texture', 'sheen', 'opacity')
        self.interconnections['shape'] = ('form', 'height/width')
        self.interconnections['form'] = ()
        self.implies[('material', 'wood')] = {'colour':('tan', 'brown', 'dark-tan', 'light-tan', 'light-brown'), 'texture':('smooth',), 'sheen':1, 'opacity':3}
        self.implies[('material', 'metal')] = {'colour':('silver', 'brass', 'gold'), 'texture':('smooth',), 'sheen':2, 'opacity':3}

