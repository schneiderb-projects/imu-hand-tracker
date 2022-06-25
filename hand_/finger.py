from typing import List

from shared.shared_utils import Cartesian3D


class Finger:
    def __init__(self, coordinates: List[Cartesian3D]):
        self._coordinates: List[Cartesian3D] = coordinates

    def joints(self) -> List[Cartesian3D]:
        return self._coordinates

    def update_coordinates(self, coordinates: List[Cartesian3D]):
        if self.joints() != len(coordinates):
            raise Exception(
                "New list of coordinates does not have the correct number of joints"
            )
        self._coordinates = coordinates

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Finger) and o.joints() == self.joints()
