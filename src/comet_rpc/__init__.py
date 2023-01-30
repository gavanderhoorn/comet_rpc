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

from .comet import (
    change_override,
    dpewrite_str,
    dpread,
    exec_kcl,
    get_macro_list,
    get_raw_file,
    gtfilist,
    iocksim,
    iodefpn,
    iogetasg,
    iogethdb,
    iogetpn,
    iogtall,
    iosim,
    iounsim,
    iovalrd,
    iovalset,
    local_start,
    posregvalrd,
    prog_abort,
    regvalrd,
    rprintf,
    txchgprg,
    txml_curang,
    txml_curpos,
    txsetlin,
    vmip_readva,
    vmip_writeva,
)

from .exceptions import (
    AuthenticationException,
    BadElementInStructureException,
    BadVariableOrRegisterIndexException,
    CometRpcException,
    DeserialisationException,
    DictElementNotFoundException,
    DictNotFoundException,
    InvalidIoIndexException,
    InvalidIoTypeException,
    LockedResourceException,
    NoCommentOnIoPortException,
    NoDataDefinedForProgramException,
    NoSuchMethodException,
    ProgramDoesNotExistException,
    UnexpectedResponseContentException,
    UnexpectedResultCodeException,
    UnexpectedRpcStatusException,
    UnknownVariableException,
)

from .kliotyps import IoType

__version__ = "0.2.0"

__all__ = [
    "AuthenticationException",
    "BadElementInStructureException",
    "BadVariableOrRegisterIndexException",
    "change_override",
    "CometRpcException",
    "DeserialisationException",
    "DictElementNotFoundException",
    "DictNotFoundException",
    "dpewrite_str",
    "dpread",
    "exec_kcl",
    "get_macro_list",
    "get_raw_file",
    "gtfilist",
    "InvalidIoIndexException",
    "InvalidIoTypeException",
    "iocksim",
    "iodefpn",
    "iogetasg",
    "iogethdb",
    "iogetpn",
    "iogtall",
    "iosim",
    "IoType",
    "iounsim",
    "iovalrd",
    "iovalset",
    "local_start",
    "LockedResourceException",
    "NoCommentOnIoPortException",
    "NoDataDefinedForProgramException",
    "NoSuchMethodException",
    "posregvalrd",
    "prog_abort",
    "ProgramDoesNotExistException",
    "regvalrd",
    "rprintf",
    "txchgprg",
    "txml_curang",
    "txml_curpos",
    "txsetlin",
    "UnexpectedResponseContentException",
    "UnexpectedResultCodeException",
    "UnexpectedRpcStatusException",
    "UnknownVariableException",
    "vmip_readva",
    "vmip_writeva",
]
