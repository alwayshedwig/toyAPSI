# NEVER HERE

class Powers():

    def __init__(self, base_pow, max_length):
        self.power = [None for _ in range(max_length+1)]
        self.h = [None for _ in range(max_length+1)]
        self.maxlen = max_length+1
        self.base = base_pow
        self.code = ""
        self.h[0] = -1
    
    def gen_code(self, name, basename):

        explicit_code = lambda x, y: "{}[{}] = {}[{}]\n".format(name, x, basename, y)
        new_code = lambda x, y, z: "{}[{}] = {}[{}] * {}[{}]\n".format(name, x, name, y, name, z)

        self.power[0] = "{}[0] = 1\n".format(name)
        self.power[1] = explicit_code(1, 0)
        self.h[1] = 0

        for i in range(2, self.maxlen):
            if i not in self.base:
                l = list(map(max, self.h[1:i], reversed(self.h[1:i])))
                min_idx = l.index(min(l))
                self.power[i] = new_code(i, min_idx+1, i-min_idx-1)
                self.h[i] = l[min_idx] + 1
            else:
                self.power[i] = explicit_code(i, self.base.index(i))
                self.h[i] = 0
        
        self.code = ""
        self.code += "try:\n"
        for i in range(self.maxlen):
            self.code += "    " + self.power[i]
        self.code += "except IndexError:\n"
        self.code += "    pass"

        return self.code

    def validate(self):

        if self.code == "":
            s = self.gen_code("pows","stamps")

        print(max(self.h))

        cpt_tree = self.base
        depth = 1
        while len(cpt_tree) < self.maxlen - 1:
            new_tree = [i+j for i in cpt_tree for j in cpt_tree if i <= j and i+j <= self.maxlen-1]
            new_tree = list(set(new_tree)-set(cpt_tree))
            # new_tree.sort()
            # print(new_tree)
            new_depth = [self.h[i] for i in new_tree]
            assert new_depth == [depth] * len(new_tree), "{} error at depth {}.".format(new_depth, depth)
            cpt_tree += new_tree
            cpt_tree.sort()
            # print(cpt_tree)
            depth += 1
        if cpt_tree == list(range(1,self.maxlen)):
            print("OK!")
        else:
            print("ERROR!")



# a1 = Powers(base_pow=[1, 5, 8], max_length=26)
# a1.validate()                

# a2 = Powers(base_pow=[1, 3, 11, 18], max_length=44)        
# a2.validate()

# a3 = Powers(base_pow=[1, 3, 11, 15, 32], max_length=70)
# a3.validate()

# b1 = Powers(base_pow=[1, 7, 12], max_length=52)
# b1.validate()

# b2 = Powers(base_pow=[1, 4, 12, 21], max_length=71)
# b2.validate()

# b3 = Powers(base_pow=[1, 4, 19, 33], max_length=114)
# b3.validate()
# print(b3.code)

# b4 = Powers(base_pow=[1, 7, 12, 43, 52], max_length=216)
# b4.validate()

# c1 = Powers(base_pow=[1, 3, 4], max_length=8)
# c1.validate()

# c2 = Powers(base_pow=[1, 3, 5, 6], max_length=12)
# c2.validate()

# c3 = Powers(base_pow=[1, 3, 5, 7, 8], max_length=16)
# c3.validate()

# c4 = Powers(base_pow=[1, 2, 5, 8, 9, 10], max_length=20)
# c4.validate()

# c5 = Powers(base_pow=[1, 2, 5, 8, 11, 12, 13], max_length=26)
# c5.validate()
