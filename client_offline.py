import pickle
from oprf import client_prf_offline, order_of_generator, G
from time import time

# OPRF parameters
oprf_client_key = 12345678910111213141516171819222222222222
client_point = (oprf_client_key % order_of_generator) * G

with open("client_set", "r") as f:
    lines = f.readlines()
    client_set = list(map(int, lines))

t0 = time()

# OPRF-PREPROCESSING
PRFed_client_set = client_prf_offline(client_set, client_point)

t1 = time()

# SAVING
with open("client_preprocessed", "wb") as f:
    pickle.dump(PRFed_client_set, f)

print('Client OFFLINE time: {:.2f}s'.format(t1-t0))
