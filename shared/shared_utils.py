from abc import ABC, abstractmethod
from typing import List, Union, Tuple

from numpy import sqrt, cos, sin, radians
from sympy import Expr, Symbol, symbols, integrate


class EulerAngle:
    def __init__(self, roll: float, pitch: float, yaw: float):
        self._roll: float = roll
        self._pitch: float = pitch
        self._yaw: float = yaw

    def roll(self) -> float:
        return self._roll

    def pitch(self) -> float:
        return self._pitch

    def yaw(self) -> float:
        return self._yaw

    def inverse(self) -> "EulerAngle":
        return EulerAngle(-1 * self.roll(), -1 * self.pitch(), -1 * self.yaw())

    def __str__(self):
        return (
            "[roll: "
            + str(self.roll())
            + ", pitch: "
            + str(self.pitch())
            + ", yaw: "
            + str(self.yaw())
            + "]"
        )

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, EulerAngle)
            and o.roll() == self.roll()
            and o.pitch() == self.pitch()
            and o.yaw() == self.yaw()
        )


class Cartesian3D:
    def __init__(self, x: float, y: float, z: float):
        self._x: float = x
        self._y: float = y
        self._z: float = z

    def x(self):
        return self._x

    def y(self):
        return self._y

    def z(self):
        return self._z

    def distance(self, point: "Cartesian3D") -> float:
        return sqrt(
            (self.x() - point.x()) ** 2
            + (self.y() - point.y()) ** 2
            + (self.z() - point.z()) ** 2
        )

    def rotate(self, euler: EulerAngle):
        cosa = cos(radians(euler.yaw()))
        sina = sin(radians(euler.yaw()))

        cosb = cos(radians(euler.pitch()))
        sinb = sin(radians(euler.pitch()))

        cosc = cos(radians(euler.roll()))
        sinc = sin(radians(euler.roll()))

        Axx = cosa * cosb
        Axy = cosa * sinb * sinc - sina * cosc
        Axz = cosa * sinb * cosc + sina * sinc

        Ayx = sina * cosb
        Ayy = sina * sinb * sinc + cosa * cosc
        Ayz = sina * sinb * cosc - cosa * sinc

        Azx = -sinb
        Azy = cosb * sinc
        Azz = cosb * cosc

        # rounds to 15 decimals places so cuz floats are having issues with whole numbers so round 0.000...001 to 0
        return Cartesian3D(
            round(Axx * self.x() + Axy * self.y() + Axz * self.z(), 15),
            round(Ayx * self.x() + Ayy * self.y() + Ayz * self.z(), 15),
            round(Azx * self.x() + Azy * self.y() + Azz * self.z(), 15),
        )

    def __sub__(self, subtrahend) -> "Cartesian3D":
        if not isinstance(subtrahend, Cartesian3D):
            raise Exception("cannot subtract type: " + type(subtrahend) + " from Cartesian3D object")
        return Cartesian3D(
            self.x() - subtrahend.x(),
            self.y() - subtrahend.y(),
            self.z() - subtrahend.z(),
        )

    def __add__(self, term) -> "Cartesian3D":
        if not isinstance(term, Cartesian3D):
            raise Exception("cannot subtract type: " + type(term) + " from Cartesian3D object")
        return Cartesian3D(
            self.x() + term.x(),
            self.y() + term.y(),
            self.z() + term.z(),
        )

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, Cartesian3D)
            and o.x() == self.x()
            and o.y() == self.y()
            and o.z() == self.z()
        )

    def __str__(self) -> str:
        return "(" + str(self.x()) + "," + str(self.y()) + "," + str(self.z()) + ")"


class SensorCoordinate:
    def __init__(self, time: float, value: float):
        self._value = value
        self._time = time

    def value(self) -> float:
        return self._value

    def time(self) -> float:
        return self._time

    def __str__(self) -> str:
        return "[time=" + str(self.time()) + ", value=" + str(self.value()) + "]"

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, SensorCoordinate)
            and o.value() == self.value()
            and o.time() == self.time()
        )


class SensorCoordinate3D:
    def __init__(self, x: SensorCoordinate, y: SensorCoordinate, z: SensorCoordinate):
        self._x: SensorCoordinate = x
        self._y: SensorCoordinate = y
        self._z: SensorCoordinate = z

    def x(self) -> SensorCoordinate:
        return self._x

    def y(self) -> SensorCoordinate:
        return self._y

    def z(self) -> SensorCoordinate:
        return self._z

    def toCartesian3D(self) -> Cartesian3D:
        return Cartesian3D(self.x().value(), self.y().value(), self.z().value())

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, SensorCoordinate3D)
            and o.x() == self.x()
            and o.y() == self.y()
            and o.z() == self.z()
        )

    def __str__(self) -> str:
        return "(" + str(self.x()) + "," + str(self.y()) + "," + str(self.z()) + ")"


class IEquation2D(ABC):
    @abstractmethod
    def tangent(self, x: float) -> float:
        raise NotImplemented

    @abstractmethod
    def integral(
        self,
        c: Union[float, None] = None,
        known_coordinate: Union[Tuple[float, float], None] = None,
    ) -> "IEquation2D":
        """
        get a definite integral of the IEquation2D. Only one of c or known_coordinate can be used, but not both.
        :param c: set the c value
        :param known_coordinate: calculate the c value using a known coordinate on the integral curve
        :return: integral of the equation
        """
        raise NotImplemented

    @abstractmethod
    def bounded_integral(self, lower_bound: float, upper_bound: float) -> float:
        raise NotImplemented

    @abstractmethod
    def y(self, x: float) -> float:
        raise NotImplemented


class Equation2D(IEquation2D):
    def __init__(self, equation: Expr, symbol: Symbol):
        self.equation: Expr = equation
        self.x = symbol
        self._integral = integrate(self.equation, self.x)
        self.derivative = self.equation.diff(self.x)

    def tangent(self, x: float) -> float:
        return self.derivative.subs(self.x, x)

    def integral(
        self,
        c: Union[float, None] = None,
        known_coordinate: Union[Tuple[float, float], None] = None,
    ) -> "Equation2D":
        if c is not None and known_coordinate is not None:
            raise Exception(
                "Cannot set c and use known coordinate. Pick one or neither."
            )
        if c is None:
            c = 0
        if known_coordinate is not None:
            y = self._integral.y(known_coordinate[0])
            c = y - known_coordinate[1]
        return Equation2D(self._integral + c, self.x)

    def integral_at(self, x: float) -> float:
        return float(self._integral.subs(self.x, x))

    def bounded_integral(self, lower_bound: float, upper_bound: float) -> float:
        return self.integral_at(upper_bound) - self.integral_at(lower_bound)

    def y(self, x: float) -> float:
        # y = mx + b
        return float(self.equation.subs(self.x, x))


class ILine2D(IEquation2D):
    def m(self) -> float:
        raise NotImplemented

    def b(self) -> float:
        raise NotImplemented


class SymPyLine2D(Equation2D, ILine2D):
    def __init__(self, slope: float, y_intercept: float):
        self._m = slope
        self._b = y_intercept
        x = symbols("x")
        super().__init__(slope * x + y_intercept, x)

    def m(self) -> float:
        return self._m

    def b(self) -> float:
        return self._b


class Polynomial(IEquation2D):
    def __init__(self, cofactors: List[float]):
        self.cofactors = cofactors
        self._integral: Union[Polynomial, None] = None

    # TODO: Polynomial derivative calculation
    def tangent(self, x: float) -> float:
        pass

    def integral(
        self,
        c: Union[float, None] = None,
        known_coordinate: Union[Tuple[float, float], None] = None,
    ) -> IEquation2D:
        if c is not None and known_coordinate is not None:
            raise Exception(
                "Cannot set c and use known coordinate. Pick one or neither."
            )

        if self._integral is None:
            newCofactors = []
            for i in range(len(self.cofactors)):
                divisor = len(self.cofactors) - i
                newCofactors.append(self.cofactors[i] / divisor)

            newCofactors.append(0)
            self._integral = Polynomial(newCofactors)

        if c is None:
            c = 0
        if known_coordinate is not None:
            y = self._integral.y(known_coordinate[0])
            c = known_coordinate[1] - y

        newCofactors = self._integral.cofactors.copy()
        newCofactors[-1] = c
        return Polynomial(newCofactors)

    def bounded_integral(self, lower_bound: float, upper_bound: float) -> float:
        if self._integral is None:
            self.integral()
        return self._integral.y(upper_bound) - self._integral.y(lower_bound)

    def y(self, x: float) -> float:
        toReturn = 0
        for i in range(len(self.cofactors)):
            exponent = len(self.cofactors) - i - 1
            toReturn += self.cofactors[i] * (x**exponent)
        return toReturn

    def __str__(self):
        toReturn = ""
        for i, a in enumerate(self.cofactors):
            if 0 == len(self.cofactors) - 1 - i and a != 0:
                toReturn += str(a)
            elif 1 == len(self.cofactors) - 1 - i and a != 0:
                toReturn += str(a) + "x + "
            elif a != 0 and toReturn != "":
                toReturn += str(a) + " + x^" + str(len(self.cofactors) - 1 - i)
            elif a != 0:
                toReturn += str(a) + "x^" + str(len(self.cofactors) - 1 - i)
        return toReturn


class Line2D(ILine2D, Polynomial):
    def __init__(self, slope: float, y_intercept: float):
        super().__init__([slope, y_intercept])

    def m(self) -> float:
        return self.cofactors[0]

    def b(self) -> float:
        return self.y(0)


class Line2DFromSlopeAndPoint(Line2D):
    def __init__(self, slope: float, x: float, y: float):
        b: float = y - x * slope
        super().__init__(slope, b)


class Line2DFrom2Points(Line2DFromSlopeAndPoint):
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        # slope calculation of line from (x1, y1) to (x2, y2)
        # m = (y2 - y1) / (x1 - x2)
        # y = mx + b
        # y - mx = b
        m: float = 0
        if x2 - x1 != 0:
            m: float = (y2 - y1) / (x2 - x1)
        # b = y - x * m
        super().__init__(m, x1, y1)


class Line3D:
    def __init__(self, initial: Cartesian3D, final: Cartesian3D):
        self._initial: initial = initial
        self._final: final = final
        self.y_line = Line2DFrom2Points(initial.x(), initial.y(), final.x(), final.y())
        self.z_line = Line2DFrom2Points(initial.x(), initial.z(), final.x(), final.z())

    def final(self) -> Cartesian3D:
        return self._final

    def initial(self) -> Cartesian3D:
        return self._initial

    def evaluate_at(self, x) -> Cartesian3D:
        return Cartesian3D(x, self.y_line.y(x), self.z_line.y(x))

    def nearest_coordinate_on_line(self, point: Cartesian3D) -> Cartesian3D:
        zero = self.distance_prime_root(point)
        return self.evaluate_at(zero)

    def distance_prime_root(self, point: Cartesian3D) -> float:
        """
        Calculate the point on the 3d line represented by the lines y_line and z_line closest to the given point

        math:
        let (x_p, y_p, z_p) represent the (x, y, z) components of a point
        let y(x) = m_y * x + b_y represent the y coordinate of a 3d line at x
        let z(x) = m_z * x + b_z represent the z coordinate of a 3d line at x
        let function d(x) be the distance from (x_p, y_p, z_p) to the 3d line at x

        d(x) = sqrt((x_p - x)^2 + (y_p - y(x))^2 + (z_p - z(x))^2)

        To find the coordinate on the 3d line with the smallest d(x), I find the d'(x) with respect to x which I'm not gonna
        write down cuz its big and long and gross. Once finding the d'(x), I calculated the x value where d'(x) = 0

        let m_z be the slope of line z(x)
        let b_z be the slope of line z(x)
        let m_y be the slope of line y(x)
        let b_y be the slope of line y(x)

        d'(x) = 0 when x = (m_z * z_p + m_y * y_p + x_p - b_z * m_z - b_y * m_y) / (m_z^2 + m_y^2 + 1)

        :param point: Point in space
        :return: Point on line closest to the given point
        """

        return float(
            (
                self.z_line.m() * point.z()
                + self.y_line.m() * point.y()
                + point.x()
                - self.z_line.b() * self.z_line.m()
                - self.y_line.b() * self.y_line.m()
            )
            / (self.z_line.m() ** 2 + self.y_line.m() ** 2 + 1)
        )

    def is_between_initial_coordinates(self, x: float) -> bool:
        return (
            max(self._initial.x(), self._final.x())
            >= x
            >= min(self._initial.x(), self._final.x())
        )

    def length(self) -> float:
        return self.initial().distance(self.final())

    def angle(self) -> EulerAngle:
        pass


def eulerRotate(euler: EulerAngle, point: Cartesian3D) -> Cartesian3D:
    cosa = cos(radians(euler.yaw()))
    sina = sin(radians(euler.yaw()))

    cosb = cos(radians(euler.pitch()))
    sinb = sin(radians(euler.pitch()))

    cosc = cos(radians(euler.roll()))
    sinc = sin(radians(euler.roll()))

    Axx = cosa * cosb
    Axy = cosa * sinb * sinc - sina * cosc
    Axz = cosa * sinb * cosc + sina * sinc

    Ayx = sina * cosb
    Ayy = sina * sinb * sinc + cosa * cosc
    Ayz = sina * sinb * cosc - cosa * sinc

    Azx = -sinb
    Azy = cosb * sinc
    Azz = cosb * cosc

    # rounds to 15 decimals places cuz floats are having issues with whole numbers so round 0.000...001 to 0
    return Cartesian3D(
        round(Axx * point.x() + Axy * point.y() + Axz * point.z(), 15),
        round(Ayx * point.x() + Ayy * point.y() + Ayz * point.z(), 15),
        round(Azx * point.x() + Azy * point.y() + Azz * point.z(), 15),
    )
