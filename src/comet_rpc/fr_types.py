# Copyright (c) 2023, G.A. vd. Hoorn
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# author: G.A. vd. Hoorn

from dataclasses import dataclass
from enum import IntEnum


class PositionType(IntEnum):
    XYZWPR = 2
    JOINTPOS = 9


@dataclass
class Configuration:
    flip: bool
    up: bool
    top: bool
    turn_no1: int
    turn_no2: int
    turn_no3: int

    # TODO: this will be incorrect for non-6-axes systems
    def __repr__(self) -> str:
        f = "F" if self.flip else "N"
        u = "U" if self.up else "D"
        t = "T" if self.top else "B"
        return f"Config: {f} {u} {t}, {self.turn_no1}, {self.turn_no2}, {self.turn_no3}"


@dataclass
class JointPos9:
    group: int
    j1: float
    j2: float
    j3: float
    j4: float
    j5: float
    j6: float
    j7: float
    j8: float
    j9: float

    # TODO: this will be incorrect for non-6-axes systems
    def __repr__(self) -> str:
        return (
            f"Group: {self.group}\n"
            f"J1: {self.j1:8.3f}   J2: {self.j2:8.3f}   J3: {self.j3:8.3f}\n"
            f"J4: {self.j4:8.3f}   J5: {self.j5:8.3f}   J6: {self.j6:8.3f}\n"
        )


@dataclass
class XyzWpr:
    config: Configuration
    group: int
    x: float
    y: float
    z: float
    w: float
    p: float
    r: float

    # TODO: this might be incorrect for non-6-axes systems
    def __repr__(self) -> str:
        return (
            f"Group: {self.group}\n"
            f"Config: {self.config}\n"
            f"X: {self.x:8.3f}   Y: {self.y:8.3f}   Z: {self.z:8.3f}\n"
            f"W: {self.w:8.3f}   P: {self.p:8.3f}   R: {self.r:8.3f}\n"
        )
