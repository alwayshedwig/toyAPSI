from random import randint, seed
from math import ceil, log2, floor
import mmh3

# DEBUG (FIXED)
# seed(12345)

class Cuckoo_hash():

    def __init__(self, hash_seeds, *, bin_num):
        self.bin_num = bin_num
        self.output_bits = ceil(log2(bin_num))
        self.seeds = hash_seeds

        assert self.output_bits <= 32, "Output_bits is set as %d against a maximum 32." % self.output_bits

        self.idx_bits = ceil(log2(len(hash_seeds)))
        self.max_depth = floor(8 * log2(self.bin_num))
        self.data = [None for _ in range(self.bin_num)]
        self.__curr_depth = 0
        self.__curr_idx = randint(0, len(self.seeds) - 1)
        self.__FAIL = False
        

    def __location(self, item, i):
        item_left = item >> self.output_bits
        item_right = item & (self.bin_num - 1)
        hashed_left = mmh3.hash(str(item_left), self.seeds[i], signed=False) >> (32 - self.output_bits)
        return hashed_left ^ item_right
    
    def __reconstruct(self, data, curr_loc, i):
        item_left = data >> self.idx_bits
        hashed_left = mmh3.hash(str(item_left), self.seeds[i], signed=False) >> (32 - self.output_bits)
        data_right = hashed_left ^ curr_loc
        return (item_left << self.output_bits) | data_right

    def __left_OR_idx(self, item, i):
        return ((item >> (self.output_bits)) << (self.idx_bits)) | i

    def __extract_idx(self, data):
        return data & (2 ** self.idx_bits - 1)

    def __unique_rand_idx(self, i):
        idx = randint(0, len(self.seeds) - 1)
        while (idx == i):
            idx = randint(0, len(self.seeds) - 1)
        return idx
    
    def __len__(self):
        return self.bin_num

    def __getitem__(self, n):
        return self.data[n]

    def insert(self, item):
        curr_loc = self.__location(item, self.__curr_idx)
        curr_item = self.data[curr_loc]
        self.data[curr_loc] = self.__left_OR_idx(item, self.__curr_idx)

        if curr_item == None:
            self.__curr_idx = randint(0, len(self.seeds) - 1)
            self.__curr_depth = 0
        else:
            aborted_idx = self.__extract_idx(curr_item)
            self.__curr_idx = self.__unique_rand_idx(aborted_idx)
            if self.__curr_depth < self.max_depth:
                self.__curr_depth += 1
                jumping_item = self.__reconstruct(curr_item, curr_loc, aborted_idx)
                self.insert(jumping_item)
            else:
                self.__FAIL = True
    
    def test_failure(self):
        return self.__FAIL
    
    def reconstruct(self, i):
        return self.__reconstruct(self.data[i], i, self.data[i] % (2**self.idx_bits))

    def pad(self, padvalue):
        for i in range(self.bin_num):
            if self.data[i] == None:
                self.data[i] = padvalue
        
    def show(self):
        for i in range(self.bin_num):
            if self.data[i] != None:
                print("{:10} => {:10}".format(i, self.data[i]))

