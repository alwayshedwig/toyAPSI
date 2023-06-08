from math import ceil, log2
import mmh3


class Simple_hash():

    def __init__(self, seeds, *, bin_num, bin_capacity):
        self.bin_num = bin_num
        self.bin_capacity = bin_capacity
        self.output_bits = ceil(log2(bin_num))
        self.seeds = seeds

        assert self.output_bits <= 32, "Output_bits is set as %d against a maximum 32." % self.output_bits

        self.seeds_num = len(seeds)
        self.idx_bits = ceil(log2(len(seeds)))
        self.data = [[None for _ in range(bin_capacity)] for _ in range(self.bin_num)]
        self.__FAIL = False
        self.__occurences = [0 for _ in range(self.bin_num)]
        

    def __location(self, item, i):
        item_left = item >> self.output_bits
        item_right = item & (self.bin_num - 1)
        hashed_left = mmh3.hash(str(item_left), self.seeds[i], signed=False) >> (32 - self.output_bits)
        return hashed_left ^ item_right

    def __left_OR_idx(self, item, i):
        return ((item >> (self.output_bits)) << (self.idx_bits)) | i

    def __len__(self):
        return self.bin_num

    def __getitem__(self, n):
        return self.data[n]

    #  insert item using hash i on position given by location
    def insert(self, item, i):
        if self.__FAIL: return
        loc = self.__location(item, i)
        if self.__occurences[loc] < self.bin_capacity:
            self.data[loc][self.__occurences[loc]] = self.__left_OR_idx(item, i)
            self.__occurences[loc] += 1
        else:
            self.__FAIL = True
    
    def insert_all(self, item):
        for i in range(self.seeds_num):
            self.insert(item, i)
    
    def test_failure(self):
        return self.__FAIL
    
    def pad(self, padvalue):
        for i in range(self.bin_num):
            for j in range(self.bin_capacity):
                if self.data[i][j] == None:
                    self.data[i][j] = padvalue
