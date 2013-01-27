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

import math
import itertools

import _deriv

class Variable(object):
    def __init__(self, v):
        self.v = v
    
    def __add__(self, other):
        if not isinstance(other, (Variable, int, long, float)): return NotImplemented
        if isinstance(other, Variable): other = other.v
        return Variable(_deriv._add(self.v, other))
    __radd__ = __add__
    
    def __sub__(self, other):
        if not isinstance(other, (Variable, int, long, float)): return NotImplemented
        if isinstance(other, Variable): other = other.v
        return Variable(_deriv._sub(self.v, other))
    def __rsub__(self, other):
        if not isinstance(other, (Variable, int, long, float)): return NotImplemented
        if isinstance(other, Variable): other = other.v
        return Variable(_deriv._sub(other, self.v))
    
    def __mul__(self, other):
        if not isinstance(other, (Variable, int, long, float)): return NotImplemented
        if isinstance(other, Variable): other = other.v
        return Variable(_deriv._mul(self.v, other))
    __rmul__  = __mul__
    
    def __div__(self, other):
        if not isinstance(other, (Variable, int, long, float)): return NotImplemented
        if isinstance(other, Variable): other = other.v
        return Variable(_deriv._div(self.v, other))
    __truediv__ = __div__
    def __rdiv__(self, other):
        if not isinstance(other, (Variable, int, long, float)): return NotImplemented
        if isinstance(other, Variable): other = other.v
        return Variable(_deriv._div(other, self.v))
    __rtruediv__ = __rdiv__
    
    def __pow__(self, other):
        if not isinstance(other, (Variable, int, long, float)): return NotImplemented
        if isinstance(other, Variable): other = other.v
        return Variable(_deriv._pow(self.v, other))
    def __rpow__(self, other):
        if not isinstance(other, (Variable, int, long, float)): return NotImplemented
        if isinstance(other, Variable): other = other.v
        return Variable(_deriv._pow(other, self.v))
    
    def __repr__(self):
        return "Variable(%r)" % (self.v,)

id_generator = itertools.count()

def varying(value, d_count=1, noise=False):
    assert d_count >= 0
    
    if d_count == 0:
        return value
    
    o = id_generator.next()
    if noise:
        o = ~o
    
    v = (value, {o: 1})
    p = v
    for i in xrange(d_count - 1):
        p[1][o] = (p[1][o], {o: 0})
        p = p[1][o]
    
    return Variable(v)


def sin(self):
    if isinstance(self, Variable):
        return Variable(_deriv._sin(self.v))
    else:
        return math.sin(self)

def cos(self):
    if isinstance(self, Variable):
        return Variable(_deriv._cos(self.v))
    else:
        return math.cos(self)

def log(self):
    if isinstance(self, Variable):
        return Variable(_deriv.log(self.v))
    else:
        return math.log(self)


def v(self):
    if not isinstance(self, Variable):
        return self
    return _deriv._v(self.v)

def d(self, *others):
    if not isinstance(self, Variable):
        return 0
    
    for other in others:
        assert isinstance(other, Variable)
        assert len(other.v[1]) == 1
        
        self = Variable(_deriv._d(self.v).get(other.v[1].keys()[0], 0))
    
    return self


def get_matrix(output, input, n=1):
    return [[v(d(y, *(x,)*n)) for x in input] for y in output]

def matrix_wrapper(n):
    def b(f):
        def a(args, *extra_args, **extra_kwargs):
            args2 = [varying(x) for x in args]
            result2 = f(args2, *extra_args, **extra_kwargs)
            result = result2[0]
            return (([v(x) for x in result], get_matrix(result, args2, n)),) + tuple(result2[1:])
        return a
    return b

jacobian_decorator = matrix_wrapper(1)
hessian_decorator = matrix_wrapper(2)


if __name__ == "__main__":
    w, x, y, z = [varying(n) for n in [3, 4, 5, 6]]
    
    #q = w / x + y * z + 1 / w
    
    q = \
        (w + 4) + (4 + w) + (w + x) + (x + w) + \
        (w - 4) + (4 - w) + (w - x) + (x - w) + \
        (w * 4) + (4 * w) + (w * x) + (x * w) + \
        (w / 4) + (4 / w) + (w / x) + (x / w) + \
        (w **4) + (4 **w) + (w **x) + (x **w) + \
    0
    
    #q = w ** x
    
    print q
    
    print "q", v(q)
    
    print "dq/dw", v(d(q, w))
    print "dq/dx", v(d(q, x))
    print "dq/dy", v(d(q, y))
    print "dq/dz", v(d(q, z))
    
    print "ddq/dw", v(d(q, w, w))
    print "ddq/dx", v(d(q, x, x))
    print "ddq/dy", v(d(q, y, y))
    print "ddq/dz", v(d(q, z, z))
    
    def f((a, b, c)):
        return ((a + b + c, a * b * c, a * b + c, a + b * c, a * a + b * b + c * c), 5)
    
    j = jacobian_decorator(f)
    h = hessian_decorator(f)
    
    print f((1., 2., 3.))
    print j((1., 2., 3.))
    print h((1., 2., 3.))
