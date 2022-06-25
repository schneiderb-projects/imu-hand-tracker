import time

from hand_ import test_hand as test_hand
from imu import test_imu as test_imu
from positioning_control import (
    test_positioning_controller as test_positioning_controller,
)
from shared import test_shared as shared_utils

def test():
    test_it(test_hand, "hand_")
    test_it(test_imu, "imu")
    test_it(test_positioning_controller, "positioning_control")
    test_it(shared_utils, "shared_utils")


def test_it(tester, comment):
    start = time.time()
    print(comment + " tests:")
    tester.test()
    print("---", comment, "runtime: %s seconds ---" % (time.time() - start))
    print()


if __name__ == "__main__":
    start_time = time.time()
    test()
    t = time.time() - start_time
    print("--- total runtime: %s seconds ---" % (time.time() - start_time))
