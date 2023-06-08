from math import log2, ceil, sqrt
import numpy as np

def roots_to_coeffs(roots, modulus):
    coeffs = np.array(1, dtype=np.int64)
    for r in roots:
        coeffs = np.convolve(coeffs, [1,-r]) % modulus
    return coeffs.tolist()


def multi_int_list(n, beta, len_per_int):
    mask = 2 ** len_per_int - 1
    return [n & (mask << i) for i in range(beta)]


def multi_int_iter(n, beta, len_per_int):
    mask = 2 ** len_per_int - 1
    for i in range(beta):
        yield n & (mask << i)


def Paterson_Stockmeyer_estimate(alpha, degree):
    '''
    param alpha: the partitioning parameter
    param degree: the degree of polynomial, equal with bin/minibin capacity
    return : the (L, H)
    '''
    L = int(sqrt((alpha+1) * (degree+1)))
    H = ceil((degree+1) / L)
    if L*H - 1 < degree: L += 1
    return L, H


