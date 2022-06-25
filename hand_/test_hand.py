from hand_.finger import Finger, Cartesian3D
from hand_.hand import Hand


def test_finger():
    f = Finger([Cartesian3D(1, 2, 3), Cartesian3D(4, 5, 6), Cartesian3D(7, 8, 9)])
    assert f.joints() == [
        Cartesian3D(1, 2, 3),
        Cartesian3D(4, 5, 6),
        Cartesian3D(7, 8, 9),
    ]
    print("Finger asserts passed")


def test_hand():
    h = Hand(
        Finger([Cartesian3D(1, 2, 3), Cartesian3D(4, 5, 6), Cartesian3D(7, 8, 9)]),
        Finger(
            [Cartesian3D(10, 11, 12), Cartesian3D(13, 14, 15), Cartesian3D(16, 17, 18)]
        ),
        Finger(
            [Cartesian3D(19, 20, 21), Cartesian3D(22, 23, 24), Cartesian3D(25, 26, 27)]
        ),
        Finger(
            [Cartesian3D(28, 29, 30), Cartesian3D(31, 32, 33), Cartesian3D(34, 35, 36)]
        ),
        Finger(
            [Cartesian3D(37, 38, 39), Cartesian3D(40, 41, 42), Cartesian3D(43, 44, 45)]
        ),
        Finger(
            [Cartesian3D(46, 47, 48), Cartesian3D(49, 50, 51), Cartesian3D(52, 53, 54)]
        ),
    )

    assert h.thumb() == Finger(
        [Cartesian3D(1, 2, 3), Cartesian3D(4, 5, 6), Cartesian3D(7, 8, 9)]
    )
    assert h.pointer() == Finger(
        [Cartesian3D(10, 11, 12), Cartesian3D(13, 14, 15), Cartesian3D(16, 17, 18)]
    )
    assert h.middle() == Finger(
        [Cartesian3D(19, 20, 21), Cartesian3D(22, 23, 24), Cartesian3D(25, 26, 27)]
    )
    assert h.ring() == Finger(
        [Cartesian3D(28, 29, 30), Cartesian3D(31, 32, 33), Cartesian3D(34, 35, 36)]
    )
    assert h.pinky() == Finger(
        [Cartesian3D(37, 38, 39), Cartesian3D(40, 41, 42), Cartesian3D(43, 44, 45)]
    )
    assert h.palm() == Finger(
        [Cartesian3D(46, 47, 48), Cartesian3D(49, 50, 51), Cartesian3D(52, 53, 54)]
    )
    assert h.thumb() == Finger(
        [Cartesian3D(1, 2, 3), Cartesian3D(4, 5, 6), Cartesian3D(7, 8, 9)]
    )

    assert h["thumb"] == Finger(
        [Cartesian3D(1, 2, 3), Cartesian3D(4, 5, 6), Cartesian3D(7, 8, 9)]
    )
    assert h["pointer"] == Finger(
        [Cartesian3D(10, 11, 12), Cartesian3D(13, 14, 15), Cartesian3D(16, 17, 18)]
    )
    assert h["middle"] == Finger(
        [Cartesian3D(19, 20, 21), Cartesian3D(22, 23, 24), Cartesian3D(25, 26, 27)]
    )
    assert h["ring"] == Finger(
        [Cartesian3D(28, 29, 30), Cartesian3D(31, 32, 33), Cartesian3D(34, 35, 36)]
    )
    assert h["pinky"] == Finger(
        [Cartesian3D(37, 38, 39), Cartesian3D(40, 41, 42), Cartesian3D(43, 44, 45)]
    )
    assert h["palm"] == Finger(
        [Cartesian3D(46, 47, 48), Cartesian3D(49, 50, 51), Cartesian3D(52, 53, 54)]
    )
    assert h["thumb"] == Finger(
        [Cartesian3D(1, 2, 3), Cartesian3D(4, 5, 6), Cartesian3D(7, 8, 9)]
    )

    print("Hand asserts passed")


def test():
    test_finger()
    test_hand()


if __name__ == "__main__":
    test()
