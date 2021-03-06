import sys
import random

###
### Implementation of the Size Algorithm detailed in:
###
### Mitchell, M., van Deemter, K., and Reiter, E. (2011). Two Approaches for Generating Size Modifiers. Proceedings of ENLG 2011.
###
###

class SizeAlgorithm():
    def __init__(self, size_hash=None, observed_hash=None):
        """
        Assumes size_hash is of the format:
        {supertype : {subtype : {'referent': (height, width), 'distractor': (height, width)}}}
        E.g., 
        {'face' : {'3' : {'referent':(13, 5), 'distractor':(blah, blah)}}} 
        {'books' : {'h++w++' : {'referent':(25, 5), 'distractor':(12, 4)}}} 
        Assumes observed_hash is of the format:
        {supertype: {subtype : {expression: [(mod_type, polarity) ... ] }}}
        E.g.,
        {supertype: {subtype : {1: [('over', 0)]}}}
        {supertype: {subtype : {3: [(('ind', 'x'), 1)]}}}
        """
        self.size_hash = size_hash
        self.observed_hash = observed_hash
        self.accuracy = None
        self.prediction_hash = {}
        return None


    def predict(self):
        """
        Makes predictions based on the given referent/distractor heights/widths 
        """
        for supertype in self.observed_hash:
            self.prediction_hash[supertype] = {}
            for subtype in self.observed_hash[supertype]:
                self.prediction_hash[supertype][subtype] = {}
                # Checks to make sure format is correct.
                try:
                    #print supertype, subtype
                    #print self.size_hash[supertype][subtype]
                    # (rx, ry) = (referent width, referent height)
                    (rx, ry) = self.size_hash[supertype][subtype]['referent']
                    # (dx, dy) = (distractor width, distractor height)
                    (dx, dy) = self.size_hash[supertype][subtype]['distractor']
                except KeyError:
                    sys.stderr.write("Size hash formatted incorrectly; exiting...\n")
                    sys.exit()
                # Calls to size_mod to make a prediction based on the given heights/widths.
                (mod, pol) = self.size_mod(rx, ry, dx, dy)
                self.prediction_hash[supertype][subtype] = [(mod, pol)]
        return self.prediction_hash


    def oracle_predict(self):
        """
        Provides the oracle prediction, calculating the majority vote for each referent.
        """
        or_prediction_hash = {}
        for supertype in self.observed_hash:
            or_prediction_hash[supertype] = {}
            for subtype in self.observed_hash[supertype]:
                or_prediction_hash[supertype][subtype] = {}
                # Stores the counts for each abstract size type
                abs_obs_hash = {}
                # list of observed abstract size types for a referent.
                for expression in self.observed_hash[supertype][subtype]:
                    # Oracle predicted by mod *type* across expressions, not *token*.
                    # No expression is weighted more...no, it is, because a person who produces 3 different ones gets 3 votes.
                    for abs_obs in self.get_types(self.observed_hash[supertype][subtype][expression]):
                        #print abs_obs
                        try:
                            abs_obs_hash[abs_obs] += 1
                        except KeyError:
                            abs_obs_hash[abs_obs] = 1
                maj_abs_obs = None
                maj_num = 0
                for abs_obs in abs_obs_hash:
                    num = abs_obs_hash[abs_obs]
                    if num > maj_num:
                        maj_num = abs_obs_hash[abs_obs]
                        maj_abs_obs = abs_obs
                # Makes oracle prediction (observed majority vote).
                or_prediction_hash[supertype][subtype] = [maj_abs_obs]
        return or_prediction_hash


    def maj_predict(self):
        """
        Provides the simple majority prediction, calculating the majority vote for the whole domain excluding the referent."
        """

        maj_prediction_hash = {}
        for supertype in self.observed_hash:
            maj_prediction_hash[supertype] = {}
            for subtype in self.observed_hash[supertype]:
                maj_prediction_hash[supertype][subtype] = {}
                # Corresponds to a single referent and all responses.
                # list of observed abstract size types
                maj_num = 0
                abs_obs_hash = {}
                # For all the *other* referents...
                for supertype_maj in self.observed_hash:
                    for subtype_maj in self.observed_hash[supertype_maj]:
                        if supertype_maj == supertype and subtype_maj == subtype:
                            continue
                        # For each type of modifier...
                        for expression in self.observed_hash[supertype_maj][subtype_maj]:
                            # Majority predicted by *type* across expressions, not *token*.
                            # No expression is weighted more...no, it is, because a person who produces 3 different ones gets 3 votes.
                            for abs_obs_maj in self.get_types(self.observed_hash[supertype_maj][subtype_maj][expression]):
                                # Increment!
                                try:
                                    abs_obs_hash[abs_obs_maj] += 1
                                except KeyError:
                                    abs_obs_hash[abs_obs_maj] = 1
                # Now find which mod was the most common
                maj_abs_obs = None
                maj_num = 0
                for abs_obs in abs_obs_hash:
                    num = abs_obs_hash[abs_obs]
                    if num > maj_num:
                        maj_num = abs_obs_hash[abs_obs]
                        maj_abs_obs = abs_obs
                maj_prediction_hash[supertype][subtype] = [maj_abs_obs]
        return maj_prediction_hash


    def size_mod(self, rx, ry, dx, dy):
        """
        Input:  Referent's height and width (ry, rx)
                Distractor's height and width (dy, dx)
        """
        (mod, pol) = (None, None)
        if ry > dy:
            # H2
            if rx > dx:
                (mod, pol) = ('over', 1)
            # H3
            elif rx < dx:
                (mod, pol) = self.largest_dim_diff(rx, ry, dx, dy)
            # H1 ; rx == dx
            else:
                (mod, pol) = self.calc_ratio(rx, ry, dx, dy, 'y', 1)
        elif ry < dy:
            # H2
            if rx < dx:
                (mod, pol) = ('over', 0)
            # H3
            elif rx > dx:
                (mod, pol) = self.largest_dim_diff(rx, ry, dx, dy)
            # H1 ; rx == dx
            else:
                (mod, pol) = self.calc_ratio(rx, ry, dx, dy, 'y', 0)
        # H1 ; ry == dy
        elif rx > dx:
            (mod, pol) = self.calc_ratio(rx, ry, dx, dy, 'x', 1)
        # H1 ; ry == dy
        elif rx < dx:
            (mod, pol) = self.calc_ratio(rx, ry, dx, dy, 'x', 0)
        else:
            # Changed 31.July.2012.  Removed this line below so it would stop babbling at me. 
            # sys.stderr.write("Don't know what to do!  height and width identical -- " + str(rx) + ", " + str(ry) + "\n")
            pass
        return (mod, pol)


    def largest_dim_diff(self, rx, ry, dx, dy):
        (mod, pol) = (None, None)
        # if difference in height is greater than difference in width
        if abs(ry - dy) > abs(rx - dx):
            if ry > dy:
                (mod, pol) = (('ind', 'y'), 1)
            elif ry < dy:
                (mod, pol) = (('ind', 'y'), 0)
            else:
                sys.stderr.write("Error (this should never happen).\n")
        # if difference in width is greater than difference in height
        elif abs(ry - dy) < abs(rx - dx):
            if rx > dx:
                (mod, pol) = (('ind', 'x'), 1)
            elif rx < dx:
                (mod, pol) = (('ind', 'x'), 0)
            else:
                sys.stderr.write("Error (this should never happen).\n")
        else: # If the differences between both axes are identical...
            # This part hasn't been figgered yet.
            # Difference in h & w is the same between objects, 
            # just choosing height by default.
            # Later versions should reason about location here.
            sys.stderr.write("Warning:  Guessing 'y', should randomize?\n")
            if ry > dy:
                (mod, pol) = (('ind', 'y'), 1)
            elif ry < dy:
                (mod, pol) = (('ind', 'y'), 0)
            else:
                if rx > dx:
                    (mod, pol) = (('ind', 'x'), 1)
                elif rx < dx:
                    (mod, pol) = (('ind', 'x'), 0)
                else:
                    sys.stderr.write("Error -- objects have same height and width.\n")
        return (mod, pol)

    
    def calc_ratio(self, rx, ry, dx, dy, axis, polarity):
        # Takes distractor height/width so a later version
        # may reason about ratio diff.
        if ry > rx:
            greater = ry
            smaller = rx
        else:
            greater = rx
            smaller = ry
        prob_ind = ((greater/float(smaller)) - 1) #* weight
        if prob_ind > 1:
            prob_ind = 1
        val = round(100 * prob_ind)
        rand_num = random.randint(1,100)
        if rand_num > val:
            (mod, pol) = ('over', polarity)
        else:
            (mod, pol) = (('ind', axis), polarity)
        return (mod, pol)


    # Place to add surface forms (not yet called).
    def generate(self, mod_type, polarity):
        return (mod_type, polarity)


    def get_types(self, expression):
        type_hash = {}
        for mod in expression:
            try:
                type_hash[mod] += 1
            except KeyError:
                type_hash[mod] = 1
        return type_hash


    def evaluate(self, predictions=None, observed_hash=None):
        __self_acc__ = False
        if predictions == None:
            __self_acc__ = True
            predictions = self.prediction_hash
        if observed_hash == None:
            observed_hash = self.observed_hash
        total_prec = 0
        total_rec = 0
        total_prec_num = 0
        total_rec_num = 0
        num_expressions = 0.0
        #supertype_prec = 0
        #supertype_rec = 0
        #num_supertypes = 0
        x = 0
        sig_precision_hash = {}
        sig_recall_hash = {}

        #print observed_hash.values()[0].keys()
        for supertype in observed_hash:
            #print supertype
            #subtype_prec = 0
            #subtype_rec = 0
            #num_subtypes = 0
            for subtype in observed_hash[supertype]:
                if observed_hash[supertype][subtype] == {}:
                    sys.stderr.write("Skipping non-size referent...")
                    continue
                #print subtype
                try:
                    prediction = predictions[supertype][subtype]
                except KeyError:
                    # Making no prediction = making wrong prediction (0.0 precision/recall)
                    prediction = ['None']
                #total_prec_num = 0
                #total_rec_num = 0
                #num_expressions = 0
                #print prediction
                num_expressions += len(observed_hash[supertype][subtype])
                __n_exp_tmp__ = len(observed_hash[supertype][subtype])
                __exp_rec_tmp__ = 0
                __exp_prec_tmp__ = 0
                for p in prediction:
                    for n in observed_hash[supertype][subtype]:
                        expression = observed_hash[supertype][subtype][n]
                        #print p, expression
                        # Do not include expressions that don't have size in them anyway.
                        if expression == []:
                            sys.stderr.write("Skipping non-size expression...")
                            continue
                        #print expression
                        #print prediction, expression
                        if p in expression:
                            __tp__ = 1
                            #print "yay!"
                        else:
                            __tp__ = 0
                            #print "boo!"
                        __prec_den__ = float(len(self.get_types(prediction))) #1.0
                        __rec_den__ = float(len(self.get_types(expression)))
                        #print __prec_den__
                        #print __tp__, __prec_den__, __rec_den__
                        __exp_prec__ = __tp__/__prec_den__
                        __exp_rec__ = __tp__/__rec_den__
                        #print __exp_rec__
                        total_prec_num += __exp_prec__
                        total_rec_num += __exp_rec__
                        __exp_rec_tmp__ += __exp_rec__
                        __exp_prec_tmp__ += __exp_prec__
                x += 1
                sig_precision_hash[x] = float(__exp_prec_tmp__)/float(__n_exp_tmp__)
                sig_recall_hash[x] = float(__exp_rec_tmp__)/float(__n_exp_tmp__) #, num_expressions
                #subtype_prec += total_prec_num / num_expressions
                #subtype_rec += total_rec_num / num_expressions
                #if num_expressions > 0:
                #    num_subtypes += 1
            #supertype_prec += subtype_prec / num_subtypes
            #supertype_rec += subtype_rec / num_subtypes 
            #if num_subtypes > 0:
            #    num_supertypes += 1
        #print total_prec_num, total_rec_num
        total_prec = total_prec_num / num_expressions #supertype_prec / num_supertypes
        total_rec = total_rec_num / num_expressions #supertype_rec / num_supertypes
        print "\nPrecision_hash:"
        for key in sorted(sig_precision_hash):
            print str(sig_precision_hash[key]) + ",",
        print "\nRecall_hash:"
        for key in sorted(sig_recall_hash):
            print str(sig_recall_hash[key]) + ",",

        if __self_acc__:
            self.precision = total_prec
            self.recall = total_rec
        return (total_prec, total_rec)


    def stats(self):
        prediction_stats = {}
        for supertype in self.prediction_hash:
            for subtype in self.prediction_hash[supertype]:
                prediction = self.prediction_hash[supertype][subtype]
                for p in prediction:
                    try:
                        prediction_stats[p] += 1
                    except KeyError:
                        prediction_stats[p] = 1
        return prediction_stats


def demo():
    predictions = {"class1":{"type1":1, "type2":1, "type3":1, "type4":1}, \
                   "class2":{"type1":1, "type2":1}, \
                   "class3":{"type1":1}}

    observed_hash = {"class1":{"type1":{0:[1, 1, 2], 1:[0, 0, 2], 2:[1, 1, 2], 3:[0, 0, 2], 4:[1, 1, 2], 5:[1, 1, 2], \
                                        6:[1, 1, 2], 7:[0, 0, 2], 8:[1, 1, 2], 9:[0, 0, 0]}, \
                              "type2":{0:[0, 0, 2], 1:[1, 1, 2], 2:[1, 1, 2],\
                                       3:[0, 0, 2], 4:[1, 1, 2], 5:[1, 1, 2],\
                                       6:[0, 0, 2], 7:[1, 1, 2], 8:[1, 1, 2], 9:[1, 1, 2]}, \
                              "type3":{0:[0, 0, 2], 1:[1, 1, 2], 2:[0, 0, 2], 3:[0, 0, 2], 4:[1, 1, 2], 5:[0, 0, 2],\
                                       6:[1, 1, 2]}, \
                              "type4":{0:[0, 0, 2], 1:[0, 0, 2]}}, \
                    "class2":{"type1":{0:[1, 1, 2], 1:[0, 0, 2], 2:[1, 1, 2], 3:[1, 1, 2], 4:[1, 1, 2], 5:[0, 0, 2]},\
                              "type2":{0:[0, 0, 2], 1:[1, 1, 2]}}, \
                    "class3":{"type1":{0:[1, 1, 2], 1:[0, 0, 2], 2:[0, 0, 2],\
                                       3:[1, 1, 2]}}}
    predictions = {"class1":{"type1":'a', "type2": 'a', "type3":'b'}, \
                   "class2":{"type1":'b', "type2": 'b'}}
    observed_hash = {"class1":{"type1":{"expression1": ['a', 'b', 'c'], "expression2":['a', 'b'], \
                                        "expression3":['a'], \
                                        "expression4":['b']}, 
                               "type2":{"expression1": ['a', 'a', 'b', 'c'], "expression2":['a', 'b'], \
                                        "expression3":['a'], \
                                        "expression4":['b']}, \
                                        "type3":{"expression1": ['a', 'b', 'c'], \
                                        "expression2":['a', 'b'], \
                                        "expression3":['a'], \
                                        "expression4":['b']}}, \
                    "class2":{"type1":{'expression1':['a'], \
                                       'expression2':['b', 'c', 'c']}, \
                              "type2":{"expression1":['b'], \
                                        "expression2":['a','c']}}}

    predictions = {"class1":{"type1":'a'}, "class2":{"type2":'b'}}
    observed_hash = {"class1":{"type1":{"expression1":['a','b','c'], "expression2":['a','b'], "expression3":['a'], "expression4":['b']}}, "class2":{"type2":{"expression1":['a'], "expression2":['c', 'b','c']}}}



    predictions = {'supertype': {'11': {'over-0': {}}, '10': {'ind-y-0': {}, 'over-0': {}}, '13': {'over-0': {}}, '14': {'over-0': {}}, '3': {'over-0': {}}, '4': {'over-0': {}}, '6': {'over-0': {}}, '9': {'over-0': {}}}}
    observed_hash = {'supertype': {'11': {23: ['over-0']}, '10': {32: ['ind-y-0'], 33: ['ind-y-0'], 34: ['ind-y-0'], 35: ['ind-y-0'], 36: ['ind-y-0'], 23: ['over-0'], 24: ['ind-y-0'], 25: ['ind-y-1', 'over-0'], 26: ['ind-y-0'], 27: ['over-0'], 28: ['over-0'], 29: ['ind-y-0'], 30: ['ind-y-0'], 31: ['ind-y-0']}, '13': {23: ['over-0'], 24: ['over-0'], 25: ['over-0'], 26: ['over-0'], 27: ['over-0'], 28: ['over-0']}, '12': {32: ['over-1'], 33: ['over-1'], 34: ['over-1'], 35: ['over-1'], 36: ['over-1'], 37: ['over-1'], 38: ['over-1'], 39: ['over-1'], 40: ['over-1'], 41: ['over-1'], 42: ['over-1'], 43: ['over-1'], 23: ['over-1'], 24: ['over-1'], 25: ['over-1'], 26: ['over-1'], 27: ['over-1'], 28: ['over-1'], 29: ['over-1'], 30: ['over-1'], 31: ['over-1']}, '15': {23: ['over-1']}, '14': {32: ['over-0'], 33: ['over-0'], 34: ['over-0'], 35: ['over-0'], 36: ['over-0'], 37: ['over-0'], 38: ['over-0'], 39: ['over-0'], 40: ['over-0'], 41: ['over-0'], 42: ['over-0'], 43: ['over-0'], 23: ['over-0'], 24: ['over-0'], 25: ['over-0'], 26: ['over-0'], 27: ['over-0'], 28: ['over-0'], 29: ['over-0'], 30: ['over-0'], 31: ['over-0']}, '1': {32: ['ind-y-1'], 33: ['ind-y-1'], 34: ['ind-y-1'], 23: ['ind-y-1'], 24: ['ind-y-1'], 25: ['ind-y-1'], 26: ['ind-y-1'], 27: ['ind-y-1'], 28: ['ind-y-1'], 29: ['ind-y-1'], 30: ['ind-y-1'], 31: ['ind-y-1']}, '3': {24: ['over-0'], 25: ['over-0'], 26: ['over-0'], 27: ['over-0'], 23: ['over-0']}, '2': {32: ['over-1'], 23: ['ind-y-1'], 24: ['over-1'], 25: ['ind-y-1'], 26: ['over-1'], 27: ['ind-y-1'], 28: ['ind-y-1'], 29: ['ind-y-1'], 30: ['ind-y-1'], 31: ['ind-y-1']}, '5': {24: ['over-1'], 25: ['ind-y-1'], 26: ['over-1'], 23: ['over-1']}, '4': {32: ['over-1'], 33: ['over-1'], 23: ['over-1'], 24: ['over-0'], 25: ['over-1'], 26: ['over-1'], 27: ['over-0'], 28: ['over-1'], 29: ['over-0'], 30: ['over-0'], 31: ['over-1']}, '7': {24: ['ind-x-1'], 23: ['ind-x-1']}, '6': {24: ['over-0'], 25: ['ind-y-1'], 23: ['ind-x-1']}, '9': {23: ['over-0']}, '8': {32: ['over-1'], 33: ['over-1'], 34: ['over-1'], 35: ['over-1'], 36: ['over-1'], 37: ['over-1'], 38: ['over-1'], 23: ['over-1'], 24: ['over-1'], 25: ['over-1'], 26: ['over-1'], 27: ['over-1'], 28: ['over-1'], 29: ['over-1'], 30: ['over-1'], 31: ['over-1']}}}



    size_alg = SizeAlgorithm()
    accuracy = size_alg.evaluate(predictions, observed_hash)
    print "Precision, recall:", accuracy


if __name__ == "__main__":
    demo()
