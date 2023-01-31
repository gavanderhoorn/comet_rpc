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


class ErrorDictionary(IntEnum):
    DICT_004 = 0x210004
    DICT_005 = 0x210005

    HRTL_022 = 0x420016

    MEMO_027 = 0x07001B
    MEMO_071 = 0x070047
    MEMO_073 = 0x070049

    PRIO_001 = 0x0D0001
    PRIO_002 = 0x0D0002
    PRIO_007 = 0x0D0007
    PRIO_011 = 0x0D000B
    PRIO_023 = 0x0D0017
    PRIO_030 = 0x0D001E

    VARS_006 = 0x100006
    VARS_011 = 0x10000B
    VARS_024 = 0x100018
    VARS_049 = 0x100031
