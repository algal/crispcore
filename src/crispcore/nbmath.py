import sympy
from sympy import symbols, Symbol, solve, Matrix, Determinant, Eq, sqrt, Abs, N, Product, Rational
from sympy import Integer, Float, Sum, nsimplify, simplify, expand
from sympy import ln, im, E, I, pi, oo, exp, factorial
from sympy import sin, cos, tan, acos, asin, atan, rad
from sympy.stats import Bernoulli, Binomial, Poisson, density
from sympy.abc import a,b,c,d
from sympy.abc import p,q,r,s,t,u,v,w,x,y,z
from sympy import integrate,diff

from sympy.core.basic import Basic
from sympy.matrices.matrices import MatrixBase


x1,x2,x3,x4 = symbols("x1 x2 x3 x4")
y1,y2,y3,y4 = symbols("y1 y2 y3 y4")


from IPython.display import display, Markdown

def deg(a_rad):
    "Converts radians to degrees"
    return a_rad * 180 / pi

# decimal

def decimal(exp, place=1):
    "Evaluates EXP to specified decimal places as Float or Matrix"
    if isinstance(exp, MatrixBase): return exp.evalf().applyfunc(lambda x: Float(round(float(x), place)))
    return Float(round(float(N(exp)), place))

def to_decimal(self,place=3):
    return decimal(self,place=place)

sympy.Basic.to_decimal = to_decimal
sympy.MatrixBase.to_decimal = to_decimal
