from fastecdsa.curve import P192
from fastecdsa.point import Point
from math import log2
from multiprocessing.pool import Pool
from functools import partial
from itertools import repeat
from para import sigma_max


# Curve parameters
curve_used = P192
prime_of_curve_equation = curve_used.p
order_of_generator = curve_used.q
log_p = int(log2(prime_of_curve_equation)) + 1
G = Point(curve_used.gx, curve_used.gy, curve=curve_used) #generator of the curve_used

# protocol parameters
mask = 2 ** sigma_max - 1

# machine parameters
number_of_processes = 4

def prf_to_secret(item, point):
    Q = item * point
    return (Q.x >> (log_p - sigma_max - 10)) & mask

def prf_to_curve(item, point):
    Q = item * point
    return [Q.x, Q.y]

'''
def grouper(lst, n):
    div = len(lst) / float(n)
    return [list(lst)[int(round(div*i)):int(round(div*(i+1)))] for i in range(n)]
'''

def server_prf_offline(items, point, num_of_proc=4):
    curr_prf = partial(prf_to_secret, point=point)
    with Pool(processes=num_of_proc) as p:
        outputs = p.map(curr_prf, items)
    return outputs


def server_prf_online(key, coordinates, num_of_proc=4):
    points = map(lambda x:Point(*x, curve=curve_used), coordinates)
    with Pool(processes=num_of_proc) as p:
        outputs = p.starmap(prf_to_curve, zip(repeat(key), points))
    return outputs

def client_prf_offline(items, point, num_of_proc=4):
    curr_prf = partial(prf_to_curve, point=point)
    with Pool(processes=num_of_proc) as p:
        outputs = p.map(curr_prf, items)
    return outputs


def client_prf_online(key_inv, coordinates, num_of_proc=4):
    points = map(lambda x:Point(*x, curve=curve_used), coordinates)
    with Pool(processes=num_of_proc) as p:
        outputs = p.starmap(prf_to_secret, zip(repeat(key_inv), points))
    return outputs

