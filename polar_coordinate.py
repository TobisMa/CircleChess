from typing import Tuple, Union
import pygame
import math

FULL_CIRCLE_ANGLE = math.pi * 2

class PolarCoordinate():
    __slots__ = ('__r', '__phi')
    def __init__(self, r: float = 1, phi: float = 0):
        self.r = r
        self.phi = phi
    
    def __repr__(self) -> str:
        return "Polar<%i * e^(%fi)>" % (self.r, self.phi)
    
    @property
    def r(self) -> float:
        return self.__r
    
    @r.setter
    def r(self, r: float):
        if r < 0:
            r = -r
            self.phi += math.pi
        self.__r = r
        
    @property
    def phi(self) -> float:
        return self.__phi
    
    @phi.setter
    def phi(self, phi: float):
        while phi > FULL_CIRCLE_ANGLE:
            phi -= FULL_CIRCLE_ANGLE
        
        while phi < 0:
            phi += FULL_CIRCLE_ANGLE
        
        self.__phi = phi
    
    def __complex__(self) -> complex:
        if self.phi == math.pi:
            return complex(-1)
        return complex(self.r * math.cos(self.phi), self.r * math.sin(self.phi))
    
    def to_cartesian(self, screen: pygame.Surface) -> Tuple[float, float]:
        x, y = screen.get_size()
        c = complex(self)
        return (c.real + x // 2, c.imag + y // 2)
    
    @classmethod
    def from_complex(cls, compl: complex) -> "PolarCoordinate":
        return cls(math.sqrt(compl.imag * compl.imag + compl.real * compl.real), math.atan2(compl.imag, compl.real))
    
    @classmethod
    def from_cartesian(cls, x: int, y: int) -> "PolarCoordinate":
        return cls.from_complex(complex(x, y))

    def __neg__(self):
        return PolarCoordinate(self.r, self.phi + math.pi)

    def __add__(self, other: "PolarCoordinate"):
        return PolarCoordinate.from_complex(complex(self) + complex(other))

    def __sub__(self, other: "PolarCoordinate"):
        return self + (-other)
    
    def __mul__(self, other: Union["PolarCoordinate", float, int]) -> "PolarCoordinate":
        if isinstance(other, (float, int)):
            return PolarCoordinate(other * self.r, self.phi)
        return PolarCoordinate(self.r * other.r, self.phi + other.phi)
    
    def __div__(self, other: Union["PolarCoordinate", float, int]) -> "PolarCoordinate":
        if isinstance(other, (float, int)):
            return PolarCoordinate(self.r / other, self.phi)
        return PolarCoordinate(self.r / other.r, self.phi - other.phi)
    
    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __rdiv__ = __div__
