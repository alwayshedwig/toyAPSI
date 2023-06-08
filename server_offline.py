from simple_hash import Simple_hash
from functools import partial, reduce
from math import log2
from oprf import server_prf_offline, order_of_generator, G
from time import time
from para import hash_seeds, bin_capacity, bin_num, alpha, plain_modulus, sigma_max, minibin_capacity, beta
from utils import multi_int_iter, roots_to_coeffs
import pickle

# OPRF parameters
oprf_server_key = 1234567891011121314151617181920
server_point = (oprf_server_key % order_of_generator) * G


with open("server_set", "r") as f:
    lines = f.readlines()
    server_set = list(map(int, lines))

t0 = time()

# OPRF-PREPROCESSING
PRFed_server_set = set(server_prf_offline(server_set, server_point))

t1 = time()

# HASHING
SH_scheme = Simple_hash(seeds=hash_seeds, bin_capacity=bin_capacity, bin_num=bin_num)
for item in PRFed_server_set:
    SH_scheme.insert_all(item)
if SH_scheme.test_failure():
    raise RuntimeError("SIMPLE-HASHING OCCURS FAILURE!")

dummy_server_msg = 2 ** (sigma_max - SH_scheme.output_bits + SH_scheme.idx_bits) + 1
SH_scheme.pad(padvalue=dummy_server_msg)

t2 = time()

# PARTITIONING
f_coeffs = partial(roots_to_coeffs, modulus=plain_modulus)
multi_int_func = partial(multi_int_iter, beta=beta, len_per_int=int(log2(plain_modulus)))
multi_int_gen = [[multi_int_func(item) for item in each_bin] for each_bin in SH_scheme]

poly_coeffs = []
for i in range(len(SH_scheme)):
    bin_poly = [reduce(list.__add__, (f_coeffs(map(next, multi_int_gen[i][minibin_capacity*k:minibin_capacity*(k+1)])) for k in range(alpha))) for _ in range(beta)]
    poly_coeffs += bin_poly


t3 = time()

# SAVING
with open("server_preprocessed", "wb") as f:
    pickle.dump(poly_coeffs, f)


# TIME EVALUATION
print('OPRF preprocessing time {:.2f}s'.format(t1 - t0))
print('Hashing time {:.2f}s'.format(t2 - t1))
print('Poly coefficients from roots time {:.2f}s'.format(t3 - t2))
print('Server OFFLINE time {:.2f}s'.format(t3 - t0))
