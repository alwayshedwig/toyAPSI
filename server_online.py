from functools import reduce
from operator import mul, add
import socket
import tenseal as ts
import pickle
import numpy as np
from math import ceil, log2
from time import time

from oprf import server_prf_online
from utils import Paterson_Stockmeyer_estimate
from stamps import *
from para import alpha, plain_modulus, minibin_capacity, circuit_depth, eval_type, poly_modulus_degree

oprf_server_key = 1234567891011121314151617181920

with open("./data/server_preprocessed", "rb") as f:
    poly_coeffs = pickle.load(f)
poly_coeffs_tr = np.transpose(poly_coeffs)

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(("localhost", 4472))
server_sock.listen(1)
print(" ! Server On.\n")

while True:

    print(" * Waiting for the client's OPRF set...", end=" ")

    conn, addr = server_sock.accept()

    # receive client set as curve coordinates
    L = conn.recv(10).decode().strip()
    L = int(L, 10)
    encoded_client_set = b""
    while len(encoded_client_set) < L:
        data = conn.recv(4096)
        if not data: break
        encoded_client_set += data
    encoded_client_set = pickle.loads(encoded_client_set)

    # print("[ACCEPT]")
    print("[ACCEPT]\n * Computing the server's OPRF...", end=" ")
    t0 = time()

    # OPRF layer
    PRFed_encoded_client_set = server_prf_online(oprf_server_key, encoded_client_set)
    PRFed_encoded_client_set = pickle.dumps(PRFed_encoded_client_set, protocol=None)

    t1 = time()
    # print("[DONE]")
    print("[DONE]\n * Sending the server's OPRF...", end=" ")

    # OPRF server reply
    L = str(len(PRFed_encoded_client_set)).ljust(10)
    conn.sendall(L.encode())
    conn.sendall(PRFed_encoded_client_set)
    # print("[DONE]")
    print("[DONE]\n * Waiting for the client's encrypted query...", end=' ')

    # receive client encryped powers
    L = conn.recv(10).decode().strip()
    L = int(L, 10)
    client_data = b""
    while len(client_data) < L:
        data = conn.recv(4096)
        if not data: break
        client_data += data
    client_data = pickle.loads(client_data)

    # print("[ACCEPT]")
    print("[ACCEPT]\n * Evaluating and sending homomorphic polynomials...", end=" ")
    t2 = time()

    fhe_ctxt = ts.context_from(client_data[0])
    query_num = len(client_data[1])
    enc_stamps = [[ts.bfv_vector_from(fhe_ctxt, ct_pow) for ct_pow in ct] for ct in client_data[1]]

    if eval_type == "Naive":
        # recover all of the powers
        stamp_base = stamp_get(minibin_capacity, circuit_depth)
        recover_func = "pows_from_" + "_".join(map(str, stamp_base))

        answer = []
        for q in range(query_num):
            
            all_powers = [None for _ in range(minibin_capacity+1)]
            eval(recover_func)(pows=all_powers, stamps=enc_stamps[q])
            all_powers.reverse()

            batch_poly_coeffs_tr = poly_coeffs_tr[:, poly_modulus_degree*q:poly_modulus_degree*(q+1)].tolist()
            ans = [sum(map(mul, batch_poly_coeffs_tr[(minibin_capacity+1)*j:(minibin_capacity+1)*(j+1)], all_powers)).serialize() for j in range(alpha)]
            answer.append(ans)

    elif eval_type == "P.-S.":

        # recover the lower and higher end of the powers
        polyL, polyH = Paterson_Stockmeyer_estimate(alpha, minibin_capacity) 
        stamp_baseL = stamp_get(polyL - 1, circuit_depth - 1)
        stamp_baseH = stamp_get(polyH - 1, circuit_depth - 1)
        recover_funcL = "pows_from_" + "_".join(map(str, stamp_baseL))
        recover_funcH = "pows_from_" + "_".join(map(str, stamp_baseH))

        answer = []
        for q in range(query_num):
            
            all_powersL = [None for _ in range(polyL)]
            all_powersH = [None for _ in range(polyH)]
            eval(recover_funcL)(pows=all_powersL, stamps=enc_stamps[q][:len(stamp_baseL)])
            eval(recover_funcH)(pows=all_powersH, stamps=enc_stamps[q][len(stamp_baseL):])

            single_ans = []
            for i in range(alpha):
                mini_poly_coeffs_tr = poly_coeffs_tr[(minibin_capacity+1)*i:(minibin_capacity+1)*(i+1), poly_modulus_degree*q:poly_modulus_degree*(q+1)].tolist()
                mini_poly_coeffs_tr.reverse()
                # ansL_gen = (reduce(add, map(mul, mini_poly_coeffs_tr[polyL*j:polyL*(j+1)], all_powersL)) for j in range(polyH))
                mini_polyH = ceil(len(mini_poly_coeffs_tr) / polyL)
                ansL_gen = (reduce(add, map(mul, mini_poly_coeffs_tr[polyL*j:polyL*(j+1)], all_powersL)) for j in range(mini_polyH))
                ans = sum(map(mul, ansL_gen, all_powersH))
                single_ans.append(ans.serialize())
            
            answer.append(single_ans)
    
    else: NameError("eval_type not found!")

    t3 = time()

    # server to client reply
    s2c_msg = pickle.dumps(answer, protocol=None)
    L = str(len(s2c_msg)).ljust(10)
    conn.sendall(L.encode())
    conn.sendall(s2c_msg)

    print("[DONE]")
    print(" # [PORT 4472] Server ONLINE computation time {:.2f}s\n".format(t1 - t0 + t3 - t2))
    # Close the connection
    conn.close()

    # print(" ! Client disconnected")

    # print("_" * 40)
    # print("Server ONLINE computation time {:.2f}s".format(t1 - t0 + t3 - t2))

    # # TO BE CONTINUED
    break
    
    

