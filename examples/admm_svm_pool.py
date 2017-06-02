"""
Copyright 2013 Steven Diamond

This file is part of CVXPY.

CVXPY is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CVXPY is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CVXPY.  If not, see <http://www.gnu.org/licenses/>.
"""

# A SVM example with CVXPY.
from cvxpy import *
import numpy as np
from multiprocessing import Pool
import time

# Divide the data into NUM_PROCS segments,
# using NUM_PROCS processes.
NUM_PROCS = 4
SPLIT_SIZE = 250

# Problem data.
np.random.seed(1)
N = NUM_PROCS*SPLIT_SIZE
n = 10
offset = np.random.randn(n, 1)
data = []
for i in xrange(N/2):
    data += [(1, offset + np.random.normal(1.0, 2.0, (n, 1)))]
for i in xrange(N/2):
    data += [(-1, offset + np.random.normal(-1.0, 2.0, (n, 1)))]
data_splits = [data[i:i+SPLIT_SIZE] for i in xrange(0, N, SPLIT_SIZE)]

# Count misclassifications.
def get_error(w):
    error = 0
    for label, sample in data:
        if not label*(np.dot(w[:-1].T, sample) - w[-1])[0] > 0:
            error += 1
    return "%d misclassifications out of %d samples" % (error, N)

# Construct problem.
rho = 1.0
w = Variable(n + 1)

def prox(args):
    f, w_avg = args
    f += (rho/2)*sum_squares(w - w_avg)
    Problem(Minimize(f)).solve()
    return w.value

def svm(data):
    slack = [pos(1 - b*(a.T*w[:-1] - w[-1])) for (b, a) in data]
    return norm(w, 2) + sum(slack)

fi = map(svm, data_splits)
# ADMM algorithm.
pool = Pool(NUM_PROCS)
w_avg = np.zeros((n+1, 1))
u_vals = NUM_PROCS*[np.zeros((n+1, 1))]
for i in range(10):
    print get_error(w_avg)
    prox_args = [w_avg - ui for ui in u_vals]
    w_vals = pool.map(prox, zip(fi, prox_args))
    w_avg = sum(w_vals)/len(w_vals)
    u_vals = [ui + wi - w_avg for ui, wi in zip(u_vals, w_vals)]

print w_avg[:-1]
print w_avg[-1]
