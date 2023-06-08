from math import log2, ceil


# PSI-parameters
server_size = 2 ** 20
client_size = 11051


# For validation
intersection_size = 4582


# FHE-parameters
# plain_modulus = 16957441
# [NOTICE] "plain_modulus" works at both offline phase and online phase!!! 
plain_modulus = 8404993
poly_modulus_degree = 8192


# ENCODING-parameters
# [NOTICE] "beta" works at both offline phase and online phase!!! 
beta = 1


# HASHING-parameters
# B = [68, 176, 536, 1832, 6727] for log(server_size) = [16, 18, 20, 22, 24]
hash_seeds = [123456789, 10111213141516, 17181920212223]
bin_capacity = 268 
bin_num = 16384


# OPRF-parameters
sigma_max = beta * int(log2(plain_modulus)) + ceil(log2(bin_num)) - ceil(log2(len(hash_seeds)))


# BATCHING-parameters
batch_num = ceil(beta * bin_num / poly_modulus_degree)
item_per_batch = int(poly_modulus_degree / beta)


# PARTITIONING-parameters
#
# as is proved in [2021],
# as long as alpha satisfies the inequation below, Peterson-Stockmeyer method is more efficient than computing all the powers
# alpha < (-2*B - sqrt(B) + sqrt(4*B**2 + 12*B*sqrt(B) - 7*B)) / 4
#
# [NOTICE] "alpha" works at both offline phase and online phase!!! 
alpha = 2
minibin_capacity = ceil(bin_capacity / alpha)


# STAMP-parameters
circuit_depth = 3


# EVAL-parameters
#
# eval_type = "Naive"
# or 
eval_type = "P.-S."


