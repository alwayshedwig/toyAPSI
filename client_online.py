import socket
import tenseal as ts
import pickle
import numpy as np
from functools import partial, reduce
from time import time
from math import log2, sqrt, ceil

from cuckoo_hash import Cuckoo_hash
from oprf import order_of_generator, client_prf_online
from stamps import *
from para import hash_seeds, plain_modulus, poly_modulus_degree, minibin_capacity, alpha, circuit_depth, eval_type, bin_capacity, bin_num, beta, batch_num, item_per_batch
from utils import Paterson_Stockmeyer_estimate, multi_int_list

oprf_client_key = 12345678910111213141516171819222222222222


client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect(("localhost", 4472))

# SET FHE SCHEME
private_ctxt = ts.context(ts.SCHEME_TYPE.BFV, poly_modulus_degree=poly_modulus_degree, plain_modulus=plain_modulus)
public_ctxt = ts.context_from(private_ctxt.serialize())
public_ctxt.make_context_public()

# OPRF layer : client send
with open("./data/client_preprocessed", "rb") as f:
    encoded_client_set = pickle.load(f)
    encoded_client_set = pickle.dumps(encoded_client_set, protocol=None)
c2s_oprf_communication = len(encoded_client_set)

print(" * Sending the OPRF client set to the server...", end=" ")
L = str(c2s_oprf_communication).ljust(10)
client_sock.sendall(L.encode())
client_sock.sendall(encoded_client_set)

# print("[DONE]")
print("[DONE]\n * Waiting for the server's answer...", end=" ")

# OPRF layer : client receive & compute
L = client_sock.recv(10).decode().strip()
L = int(L, 10)
PRFed_encoded_client_set = b""
while len(PRFed_encoded_client_set) < L:
    data = client_sock.recv(4096)
    if not data: break
    PRFed_encoded_client_set += data   
s2c_oprf_communication = len(PRFed_encoded_client_set)
PRFed_encoded_client_set = pickle.loads(PRFed_encoded_client_set)

# print("[ACCEPT]")
print("[ACCEPT]\n * Computing client's OPRF...", end=" ")
t0 = time()

key_inverse = pow(oprf_client_key, -1, order_of_generator)
PRFed_client_set = client_prf_online(key_inv=key_inverse, coordinates=PRFed_encoded_client_set)

t1 = time()

print("[DONE]\n * Generating encrypted {} query ...".format(eval_type), end=" ")
t2 = time()

# FHE layer: HASHING
CH_scheme = Cuckoo_hash(hash_seeds=hash_seeds, bin_num=bin_num)
for item in PRFed_client_set:
    CH_scheme.insert(item)
# dummy_client_msg = 2 ** (sigma_max - CH_scheme.output_bits + CH_scheme.idx_bits)
dummy_client_msg = 11100111
CH_scheme.pad(padvalue=dummy_client_msg)

# FHE layer: preparing for BATCHING
multi_int_func = partial(multi_int_list, beta=beta, len_per_int=int(log2(plain_modulus)))
bin_to_batch = [reduce(list.__add__, map(multi_int_func, CH_scheme[item_per_batch*i: item_per_batch*(i+1)])) for i in range(batch_num)]

if eval_type == "Naive":

    # FHE layer: STAMPING
    client_stamps = stamp_get(minibin_capacity, circuit_depth)
    pow_funcs = [partial(pow, exp=stamp, mod=plain_modulus) for stamp in client_stamps]
    client_stamp_querys = [[map(pow_func, batch) for pow_func in pow_funcs] for batch in bin_to_batch]

    # FHE layer: BATCHING
    enc_stamps = [[ts.bfv_vector(private_ctxt, list(query_pow)).serialize() for query_pow in query] for query in client_stamp_querys]

elif eval_type == "P.-S.":

    """ 
    if alpha >= (-2*bin_capacity - sqrt(bin_capacity) + sqrt(4*bin_capacity**2 + 12*bin_capacity*sqrt(bin_capacity) - 7*bin_capacity)) / 4 :
        print("<Suggestion> Using \"Naive\" mode may result in a better performance.") 
    """

    # FHE layer: Paterson-Stockmeyer Method -> L, H
    polyL, polyH = Paterson_Stockmeyer_estimate(alpha, minibin_capacity)

    # FHE layer: STAMPING with P.-S.
    PS_stampsL = stamp_get(polyL - 1, circuit_depth - 1)
    PS_stampsH = stamp_get(polyH - 1, circuit_depth - 1)
    pow_funcsL = [partial(pow, exp=stampL, mod=plain_modulus) for stampL in PS_stampsL]
    pow_funcsH = [partial(pow, exp=stampsH*polyL, mod=plain_modulus) for stampsH in PS_stampsH]
    client_stampL = [[map(pow_funcL, batch) for pow_funcL in pow_funcsL] for batch in bin_to_batch]
    client_stampH = [[map(pow_funcH, batch) for pow_funcH in pow_funcsH] for batch in bin_to_batch]
    client_stamp_querys = map(list.__add__, client_stampL, client_stampH)

    # FHE layer: BATCHING
    enc_stamps = [[ts.bfv_vector(private_ctxt, list(query_pow)).serialize() for query_pow in queryLH] for queryLH in client_stamp_querys]

else: NameError("eval_type not found!")

# FHE layer: PACKAGING
fhe_msg = [public_ctxt.serialize(), enc_stamps]
c2s_fhe_msg = pickle.dumps(fhe_msg, protocol=None)
c2s_fhe_communication = len(c2s_fhe_msg)

t3 = time()
print("[DONE]\n * Sending the context and ciphertext to the server...", end=" ")

# FHE layer: client send 
L = str(c2s_fhe_communication).ljust(10)
client_sock.sendall(L.encode())
client_sock.sendall(c2s_fhe_msg)



print("[DONE]\n * Waiting for the server's answer...", end=" ")



# FHE layer: client receive
L = client_sock.recv(10).decode().strip()
L = int(L,10)
enc_answer = b""
while len(enc_answer) < L:
    data = client_sock.recv(4096)
    if not data: break
    enc_answer += data
s2c_fhe_communication = len(enc_answer)
enc_answer = pickle.loads(enc_answer)

# print("[ACCEPT]")
print("[ACCEPT]\n * Decrypting the answer and finding the intersection...", end=" ")
t4 = time()

# FHE layer: DECRYPTION
answer = [[ts.bfv_vector_from(private_ctxt, ct).decrypt() for ct in enc_batch] for enc_batch in enc_answer]

# DEBUG
"""
with open("client_decryption","wb") as f:
    pickle.dump(answer,f)
"""

# reconstruct item from hashed item & find out intersection
with open("./data/client_set","r") as f:
    client_set_raw = f.readlines()

client_intersection = []
for k in range(batch_num):
    for j in range(alpha):
        for i in range(item_per_batch):
            if answer[k][j][beta*i:beta*(i+1)] == [0 for _ in range(beta)]:
                PRFed_common_elem = CH_scheme.reconstruct(k*item_per_batch + i)
                idx = PRFed_client_set.index(PRFed_common_elem)
                client_intersection.append(int(client_set_raw[idx]))
        

t5 = time()
print("[DONE]")

# close socket
client_sock.close()
print(" ! Disconnected.")

print("_" * 40)

# validation
with open("./data/intersection","r") as ft:
    real_intersection = [int(line) for line in ft]
correctness = set(client_intersection) == set(real_intersection)
print('[TEST] Intersection Correctness: {}'.format(correctness))
if correctness == False:
    set_FHE, set_True = set(client_intersection), set(real_intersection)
    print("  | Decrypted intersection num: {}".format(len(set_FHE)))
    print("  | Successfully recovered items num: {}".format(len(set_FHE & set_True)))
    print("  | False positive num: {}".format(len(set_FHE - set_True)))

# TIME EVALUATION
print('Client ONLINE computation time {:.2f}s'.format((t1 - t0) + (t3 - t2) + (t5 - t4)))
print('Communication size:')
print('  | Client --> Server:  {:.2f} MB'.format((c2s_oprf_communication + c2s_fhe_communication) / 2**20))
print('  | Server --> Client:  {:.2f} MB'.format((s2c_oprf_communication + s2c_fhe_communication) / 2**20))

