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

# Example usage:

import deriv

x = deriv.varying(5)
y = deriv.varying(-7)

r = (x * x + y * y) ** .5

print "r", deriv.v(r)
print "dr/dx", deriv.v(deriv.d(r, x))
print "dr/dy", deriv.v(deriv.d(r, y))
print "d2r/dx2", deriv.v(deriv.d(r, x, x))
print "d2r/dy2", deriv.v(deriv.d(r, y, y))
print "d2r/dx/dy", deriv.v(deriv.d(r, x, y))
print "d2r/dy/dx", deriv.v(deriv.d(r, y, x))

print

r = deriv.sin(x)
print "r", deriv.v(r)
print "dr/dx", deriv.v(deriv.d(r, x))
print "dr/dy", deriv.v(deriv.d(r, y))
print "d2r/dx2", deriv.v(deriv.d(r, x, x))
print "d2r/dy2", deriv.v(deriv.d(r, y, y))
print "d2r/dx/dy", deriv.v(deriv.d(r, x, y))
print "d2r/dy/dx", deriv.v(deriv.d(r, y, x))

print
print
print

import noise

x = -1 + noise.noise(3)
y = 2 + noise.noise(7)

r = x, y, x + y, x - y, x / y, x * x, x * y, y * y

print ' '.join("%7.03f" % noise.E(x) for x in r), "E"
print ' '.join("%7.03f" % noise.var(x) for x in r), "variance"
print
print "covariance matrix:"

for row in noise.cov_matrix(r):
    for col in row:
        print "%7.03f" % col,
    print
