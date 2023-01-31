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

from enum import IntEnum


class IoType(IntEnum):
    """from kliotyps.kl, V9.40"""

    None_ = 0
    DigitalIn = 1  # Digital input
    DigitalOut = 2  # Digital output
    AnalogIn = 3  # Analog input
    AnalogOut = 4  # Analog output
    ToolOut = 5  # Tool output
    PlcIn = 6  # PLC input
    PlcOut = 7  # PLC output
    RobotDigitalIn = 8  # Robot digital input
    RobotDigitalOut = 9  # Robot digital output
    BrakeOut = 10  # Brake output
    # old names (?)
    OpPanelIn = 11  # Operator panels input
    OpPanelOut = 12  # Operator panels output
    # new names (?)
    SoPanelIn = 11  # Same as OpPanelIn
    SoPanelOut = 12  # Same as OpPanelOut
    Estop = 13  # Emergency stop
    TpIn = 14  # Teach pendant digital input
    TpOut = 15  # Teach pendant digital output
    WeldDigitalIn = 16  # Weld inputs
    WeldDigitalOut = 17  # Weld outputs
    GroupedIn = 18  # Grouped inputs (16 bits)
    GroupedOut = 19  # Grouped outputs (16 bits)
    UserOpPanelIn = 20  # User operator's panel input
    UserOpPanelOut = 21  # User operator's panel output
    LaserDigIn = 22  # Laser DIN
    LaserDigOut = 23  # Laser DOUT
    LaserAnaIn = 24  # Laser AIN
    LaserAnaOut = 25  # Laser AOUT
    WeldStickInput = 26  # Weld stick input
    WeldStickOutput = 27  # Weld stick output
    MemImgBoolean = 28  # Memory image boolean's
    MemImgDigIn = 29  # Memory image din's
    DummyBoolPort = 30  # Dummy boolean port type
    DummyNumPort = 31  # Dummy numeric port type
    ProcessAxis = 32  # Process axes
    InternalOpPanelInput = 33  # Internal operator's panel input
    InternalOpPanelOutput = 34  # Internal operator's panel output
    Flag = 35  # Flag (F[ ])
    Marker = 36  # Marker (M[ ])
    GroupedIn32 = 37  # Grouped inputs (32 bits)
    GroupedOut32 = 38  # Grouped outputs (32 bits)

    # physical only
    InternalRelayBackup = 41  # Backuped internal relay
    InternalRelay = 42  # No backuped internal relay
    InternalRegBackup = 43  # Backuped internal register
    InternalReg = 44  # No backuped internal register
