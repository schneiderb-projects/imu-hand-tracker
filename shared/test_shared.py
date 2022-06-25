from shared.shared_utils import (
    Line2DFrom2Points,
    Line3D,
    Cartesian3D,
    EulerAngle,
    Polynomial,
)


def test_EulerAngle():
    ea = EulerAngle(1, 2, 5)
    assert ea.roll() == 1
    assert ea.pitch() == 2
    assert ea.yaw() == 5

    ea_inverse = ea.inverse()
    assert ea_inverse.roll() == -1
    assert ea_inverse.pitch() == -2
    assert ea_inverse.yaw() == -5

    print("EulerAngle asserts passed")


def test_Cartesian3D():
    c3d = Cartesian3D(1, 2, 5)
    assert c3d.x() == 1
    assert c3d.y() == 2
    assert c3d.z() == 5
    assert c3d.distance(Cartesian3D(-1, -2, 1)) == 6

    c3d2 = c3d - c3d
    assert c3d2.x() == 0
    assert c3d2.y() == 0
    assert c3d2.z() == 0

    print("Cartesian3D asserts passed")


def test_Line2D():
    line = Line2DFrom2Points(0, 0, 1, 2)
    assert line.m() == 2 / 1
    assert line.b() == 0
    assert line.y(10) == 2 * 10 + 0
    assert line.bounded_integral(0, 1) == 0.5 * 1 * 2
    print("Line2D asserts passed")


def test_Polynomial():
    poly = Polynomial([1, 2, 3, 4])
    assert poly.y(0) == 4
    assert poly.y(10) == 10**3 + 2 * 10**2 + 3 * 10 + 4
    assert (
        poly.bounded_integral(0, 1)
        == 0.25 * 1**4 + (1 / 3) * 2 * 1**3 + 0.5 * 3 * 1**2 + 4 * 1**1
    )
    assert poly.bounded_integral(3, 4) == 0.25 * 4**4 + (
        1 / 3
    ) * 2 * 4**3 + 0.5 * 3 * 4**2 + 4 * 4**1 - (
        0.25 * 3**4 + (1 / 3) * 2 * 3**3 + 0.5 * 3 * 3**2 + 4 * 3**1
    )
    assert poly.integral(c=0).y(0) == 0
    assert poly.integral(known_coordinate=(0, 0)).y(0) == 0
    assert poly.integral(c=4).y(0) == 4
    assert poly.integral(known_coordinate=(0, 4)).y(0) == 4
    assert poly.integral(known_coordinate=(4, 4)).y(0) == 4 - (
        0.25 * 4**4 + (1 / 3) * 2 * 4**3 + 0.5 * 3 * 4**2 + 4 * 4**1
    )

    print("Polynomial asserts passed")


def test_Line3D():
    z1 = -7.5
    z2 = 1
    z3 = 4.9

    y1 = 1
    y2 = -9
    y3 = 1.5

    x1 = 0
    x2 = 0.8
    x3 = 1

    l3d = Line3D(Cartesian3D(x1, y1, z1), Cartesian3D(x2, y2, z2))

    assert l3d.z_line.m() == Line2DFrom2Points(x1, z1, x2, z2).m()
    assert l3d.z_line.b() == Line2DFrom2Points(x1, z1, x2, z2).b()
    assert l3d.y_line.m() == Line2DFrom2Points(x1, y1, x2, y2).m()
    assert l3d.y_line.b() == Line2DFrom2Points(x1, y1, x2, y2).b()

    assert l3d.evaluate_at(10) == Cartesian3D(
        10,
        Line2DFrom2Points(x1, y1, x2, y2).y(10),
        Line2DFrom2Points(x1, z1, x2, z2).y(10),
    )

    assert l3d.nearest_coordinate_on_line(Cartesian3D(x3, y3, z3)) == Cartesian3D(
        0.46827462548441207,
        Line2DFrom2Points(x1, y1, x2, y2).y(0.46827462548441207),
        Line2DFrom2Points(x1, z1, x2, z2).y(0.46827462548441207),
    )

    assert l3d.is_between_initial_coordinates(10) is False
    assert l3d.is_between_initial_coordinates(0.5) is True
    assert l3d.is_between_initial_coordinates(-10) is False

    print("Line3D asserts passed")


def test():
    test_Line2D()
    test_Line3D()
    test_Cartesian3D()
    test_EulerAngle()
    test_Polynomial()


if __name__ == "__main__":
    test()
