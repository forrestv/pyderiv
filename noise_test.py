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

def f():
    a = noise(3)
    b = 8 + noise(2)
    return a, b, a + b, a /b, a*a, a*b, b*b

def go():
    for x in v: print x
    
    for x in v: print E(x)
    
    print
    
    for i in xrange(len(r)):
        for j in xrange(len(r)):
            print "%6.01f" % cov(r[i], r[j]),
        print

from noise import noise, var, cov, cov_matrix, E

r = f()
v = r

go()

print cov_matrix(r)

print
print

import random
import math

def noise(variance):
    return random.gauss(0, math.sqrt(variance))

def avg(l):
    l = list(l)
    return sum(l)/len(l)

def E(x): return x

def cov(i, j):
    return avg(r[i]*r[j] for r in samples) - avg(r[i] for r in samples)*avg(r[j] for r in samples)

def var(a): return cov(a, a)

samples = [f() for i in xrange(1000000)]
v = map(avg, zip(*samples))

r = xrange(len(samples[0]))

go()
