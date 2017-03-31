#!/usr/bin/env python3

import random
import numpy as np
import itertools
import sys

#s = 13
#s = 10
#s = 7
s = 5
#s = 3
t = s*s  # number of stimuli
stimuli_order = np.arange(t)
#np.random.shuffle(stimuli_order)
max_votes = 1

rand_alpha=0.05

M = np.zeros((t,t), dtype=np.int)

n = t*(np.sqrt(t)-1) # number of comparisons

comparison_matrix = np.arange(t).reshape((s,s))

print('comparison_matrix=\n', comparison_matrix)

#------------------------------------------------------------------------------

def compare(p0, p1):
    global M

    rand = random.random()

    r0 = np.where(stimuli_order==p0)[0][0]
    r1 = np.where(stimuli_order==p1)[0][0]

    dist = r1-r0
    # dist > 0 -> pair0 better
    # dist < 0 -> pair1 better
    # 0.0 < abs(dist) < 1.0
    dd = abs(dist)
    rand_comp = 1 - rand_alpha / dd

    #print('comparing', p0, p1, dist, dd, rand_comp)

    if dist > 0: # pair0 better
        if rand < rand_comp:
            M[p0, p1] += 1
        else:
            M[p1, p0] += 1
    else:
        if rand < rand_comp:
            M[p1, p0] += 1
        else:
            M[p0, p1] += 1
    
#------------------------------------------------------------------------------

print('Iteration=', end=' ')
for it in range(max_votes):
    print(it, end=' ')
    sys.stdout.flush()

    # for each row
    for r in range(s):
        for pair in itertools.combinations(list(comparison_matrix[r,:]), 2):
            compare(pair[0], pair[1])

    for c in range(s):
        for pair in itertools.combinations(list(comparison_matrix[:,c]), 2):
            compare(pair[0], pair[1])

print('\n')
print('M=\n', M)

np.savetxt("m{}.txt".format(s), M, fmt='%2d')
#np.savetxt("a{}.txt".format(s), np.arange(1,t+1), fmt='%d')
        

