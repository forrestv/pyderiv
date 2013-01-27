# This file is part of pyderiv. http://forre.st/pyderiv
#
# pyderiv is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# at your option) any later version.
#
# pyderiv is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyderiv.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division

import itertools
import math

import _deriv
import deriv

def noise2(variance):
    assert variance >= 0
    return math.sqrt(variance) * deriv.varying(0, noise=True)

def noise(sigma):
    return noise2(sigma * sigma)

def Eana(x, c):
    if isinstance(x, tuple):
        t = Eana(x[0], c)
        return t + sum(Eana(x[1][k], c + (k,)) for k in x[1] if k < 0)
    else:
        if len(c) == 0: return x
        if not all(x == c[0] for x in c):  return 0
        if len(c) == 1: return 0
        if len(c) == 2: return x/2
        assert False, "expand E handler!"

# maybe it should just change value and not strip off derivs?
# it should change value and only strip off noise derivs
def E(v):
    if not isinstance(v, deriv.Variable): return v
    a = v.v
    return Eana(a, ())

def ana(x, c):
    if isinstance(x, tuple):
        t = ana(x[0], c)
        return t + sum(ana(x[1][k], c + (k,)) for k in x[1] if k < 0)
    else:
        if len(c) == 0: return 0
        if len(c) == 1: return x*x
        if len(c) == 2: return x*x/2
        assert False, "expand variance handler!"

def var(v):
    if not isinstance(v, deriv.Variable): return 0
    a = v.v
    return ana(a, ())

def cov(a, b):
    return (var(a + b) - var(a) - var(b))/2

def cov_matrix(r):
    result = [[None for a in r] for b in r]
    for i, a in enumerate(r):
        result[i][i] = var(a)
    for i, a in enumerate(r):
        for j, b in enumerate(r[:i]):
            n = cov(a, b)
            result[i][j] = n
            result[j][i] = n
    return result
