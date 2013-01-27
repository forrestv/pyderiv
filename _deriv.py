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

# a 'value' (unwrapped Variable) takes the form
# value = float | (float, {var: value, var: value, ...})

# more testing needs to be done for impact of zero padding - is it needed or not?
# _mul fills in extra fields with just a dict
# so is it needed?? o.O

# perhaps we can redefine value to something like
# newvalue = (value, derivative_depth)
# in order to make remove_one_deriv much faster and remove the need for padding

# also, it'd be nice and faster if we could collapse the entire structure to
# pos = {var: int}
# actual = {pos: float}
# value = (actual, pos)
# and have actual not be altered, only the passed around would have pos changed
# this might benefit from the derivative_depth idea

# last, we should really do this after the function
# eg. store all operations and then take only derivatives we need
# derivatives are being taken between noise variables and state variables
# - a huge waste

def _v(x):
    if isinstance(x, tuple):
        return x[0]
    return x

def _d(x):
    if isinstance(x, tuple):
        return x[1]
    return {}

def remove_one_deriv(r):
    assert isinstance(r, tuple), r
    d = r[1]
    assert isinstance(d, dict)
    d = dict((k, remove_one_deriv(d[k])) for k in d if isinstance(d[k], tuple))
    if d:
        return r[0], d
    return r[0]

def check(x):
    if isinstance(x, dict):
        if not x: return 0
        assert all(not isinstance(v, dict) for v in x.itervalues())
        return max(map(check, x.itervalues()))
    if isinstance(x, tuple):
        assert isinstance(x[0], (float, int, long)), x
        assert isinstance(x[1], dict), x
        return check(x[1]) + 1
    assert isinstance(x, (float, int, long)), x
    return 0

def check_decorator(f):
    #return f
    def checker(*args):
        should = max(check(a) for a in args)
        r = f(*args)
        assert check(r) == should, f.func_name + repr(args) + " = " + repr(r)
        return r
    return checker

@check_decorator
def _add(a, b):
    if isinstance(a, dict) or isinstance(b, dict):
        if not isinstance(a, dict): return dict((k, _add(a, b[k])) for k in b)
        if not isinstance(b, dict): return dict((k, _add(a[k], b)) for k in a)
        keys = set(a)
        keys.update(b)
        return dict((k, _add(a.get(k, 0), b.get(k, 0))) for k in keys)
    if isinstance(a, tuple) or isinstance(b, tuple):
        if not isinstance(a, tuple): return a + _v(b), _d(b)
        if not isinstance(b, tuple): return _v(a) + b, _d(a)
        return _add(_v(a), _v(b)), _add(_d(a), _d(b))
    return a + b

@check_decorator
def _sub(a, b):
    if isinstance(a, dict) or isinstance(b, dict):
        if not isinstance(a, dict): return dict((k, _sub(a, b[k])) for k in b)
        if not isinstance(b, dict): return dict((k, _sub(a[k], b)) for k in a)
        keys = set(a)
        keys.update(b)
        return dict((k, _sub(a.get(k, 0), b.get(k, 0))) for k in keys)
    if isinstance(a, tuple) or isinstance(b, tuple):
        if not isinstance(a, tuple): return a - _v(b), _sub(0, _d(b))
        if not isinstance(b, tuple): return _v(a) - b, _d(a)
        return _sub(_v(a), _v(b)), _sub(_d(a), _d(b))
    return a - b

@check_decorator
def _mul(a, b):
    if isinstance(a, dict) or isinstance(b, dict):
        if not isinstance(a, dict): return dict((k, _mul(a, b[k])) for k in b)
        if not isinstance(b, dict): return dict((k, _mul(a[k], b)) for k in a)
        keys = set(a)
        keys.update(b)
        return dict((k, _mul(a.get(k, 0), b.get(k, 0))) for k in keys)
    if isinstance(a, tuple) or isinstance(b, tuple):
        if not isinstance(a, tuple): return a * _v(b), _mul(a, _d(b))
        if not isinstance(b, tuple): return _v(a) * b, _mul(_d(a), b)
        return _mul(_v(a), _v(b)), _add(_mul(remove_one_deriv(a), _d(b)), _mul(remove_one_deriv(b), _d(a)))
    return a * b

@check_decorator
def _div(a, b):
    if isinstance(a, dict) or isinstance(b, dict):
        if not isinstance(a, dict): return dict((k, _div(a, b[k])) for k in b)
        if not isinstance(b, dict): return dict((k, _div(a[k], b)) for k in a)
        keys = set(a)
        keys.update(b)
        return dict((k, _mul(a.div(k, 0), b.get(k, 0))) for k in keys)
    if isinstance(a, tuple) or isinstance(b, tuple):
        if not isinstance(a, tuple): return a / _v(b), _mul(_d(b), _div(-a, _mul(remove_one_deriv(b), remove_one_deriv(b))))
        if not isinstance(b, tuple): return _v(a) / b, _div(_d(a), b)
        return _div(_v(a), _v(b)), _div(_sub(_mul(remove_one_deriv(b), _d(a)), _mul(remove_one_deriv(a), _d(b))), _mul(remove_one_deriv(b), remove_one_deriv(b)))
    return a / b

@check_decorator
def _pow(a, b):
    if isinstance(a, dict) or isinstance(b, dict):
        if not isinstance(a, dict): return dict((k, _pow(a, b[k])) for k in b)
        if not isinstance(b, dict): return dict((k, _pow(a[k], b)) for k in a)
        keys = set(a)
        keys.update(b)
        return dict((k, _pow(a.div(k, 0), b.get(k, 0))) for k in keys)
    if isinstance(a, tuple) or isinstance(b, tuple):
        if not isinstance(a, tuple): return _pow(a, _v(b)), _mul(_d(b), _mul(_log(a), _pow(a, remove_one_deriv(b))))
        if not isinstance(b, tuple): return _pow(_v(a), b), _mul(_d(a), _mul(_pow(remove_one_deriv(a), b - 1), b))
        return _pow(_v(a), _v(b)), _add(
            _mul(_d(a), _mul(_pow(remove_one_deriv(a), _sub(remove_one_deriv(b), 1)), remove_one_deriv(b))),
            _mul(_d(b), _mul(_log(remove_one_deriv(a)), _pow(remove_one_deriv(a), remove_one_deriv(b)))),
        )
    return a ** b

@check_decorator
def _log(a):
    if not isinstance(a, tuple):
        return math.log(a)
    return _log(_v(a)), _div(_d(a), remove_one_deriv(a))

@check_decorator
def _sin(a):
    if not isinstance(a, tuple):
        return math.sin(a)
    return _sin(_v(a)), _mul(_d(a), _cos(remove_one_deriv(a)))

@check_decorator
def _cos(a):
    if not isinstance(a, tuple):
        return math.cos(a)
    return _cos(_v(a)), _mul(_d(a), _mul(-1, _sin(remove_one_deriv(a))))

if __name__ == "__main__":
    def ana(x, c, d):
        if isinstance(x, tuple):
            d.setdefault(c, []).append(x[0])
            for k in x[1]:
                ana(x[1][k], c + (k,), d)
        else:
            d.setdefault(c, []).append(x)
    
    def print_var(x):
        r = {}
        ana(x, (), r)
        print r
    
    r1 = "x"
    r2 = "y"
    
    n = (5, {r1: (1, {r1: 0})})
    o = (3, {r2: (1, {r2: 0})})
    p = 2
    
    assert check(n) == 2
    assert check(o) == 2
    assert check(p) == 0
    assert check((1, {})) == 1
    
    assert remove_one_deriv(n) == (5, {r1: 1})
    assert remove_one_deriv(remove_one_deriv(n)) == 5
    
    assert check(remove_one_deriv(n)) == check(n) - 1
    
    print 'n+n', _add(n, n)
    print 'n+o', _add(n, o)
    print 'n+p', _add(n, p)
    
    print 'n-o', _sub(n, o)
    
    print 'n*n', _mul(n, n)
    print 'n*o', _mul(n, o)
    print 'n*p', _mul(n, p)
    
    print_var(_mul(n, o))
    
    print_var(_mul(_mul(_mul(n, n), n), n))
    
    print_var(_div(o, n))
    
    print_var(_sin(o))
    
    assert _mul(n, o) == _mul(o, n)
    assert _mul(_mul(o, n), o) == _mul(_mul(o, o), n)
