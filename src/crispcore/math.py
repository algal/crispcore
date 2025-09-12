import sympy
from sympy import symbols, Symbol, solve, Matrix, Determinant, Eq, sqrt, Abs, N, Product
from sympy import Integer, Float, Sum, nsimplify, simplify, expand
from sympy import ln, im, E, I, pi, oo, exp, factorial
from sympy import sin, cos, tan, acos, asin, atan, rad
from sympy.stats import Bernoulli, Binomial, Poisson, density
from sympy.abc import a,b,c,d
from sympy.abc import p,q,r,s,t,u,v,w,x,y,z
from sympy import integrate,diff

from fastcore.all import patch
from sympy.core.basic import Basic
from sympy.matrices.matrices import MatrixBase

x1,x2,x3,x4 = symbols("x1 x2 x3 x4")
y1,y2,y3,y4 = symbols("y1 y2 y3 y4")

def deg(a_rad):
    "Converts radians to degrees"
    return a_rad * 180 / pi

# decimal

def decimal(exp,place=1):
    "Evaluates EXP to 1 decimal place"
    return float(exp.n()).__format__(f'.{place}f')

@patch(Basic)
def to_decimal_str(self, place=1):
    "Evaluates expression to specified decimal place"
    return float(self.n()).__format__(f'.{place}f')

@patch(MatrixBase)
def to_decimal_str(self, place=1):
    "Evaluates matrix to specified decimal place"
    return self.evalf().applyfunc(lambda x: float(x).__format__(f'.{place}f'))

