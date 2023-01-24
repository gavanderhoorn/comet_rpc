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

from base64 import urlsafe_b64decode

from enum import Enum

import typing as t
import typing_extensions as te

from pydantic import (
    BaseModel,
    Field,
    validator,
)

from .fr_types import PositionType
from .kliotyps import IoType


# TODO: use StrEnum when we have Python 3.11+
class RpcId(str, Enum):
    # COMET's response-JSON quotes integers, and it looks like discriminators
    # are checked before validators are run (so the conversion to int in
    # BaseRpcResponse only happens after the discriminator field has been
    # checked)
    CPKCL = "87"
    DPEWRITE_STR = "83"
    DPREAD = "148"
    ERPOST = "85"
    GET_RAW_FILE = "251"
    GTFILIST = "234"
    IODEFPN = "68"
    IOGETPN = "67"
    IOGTALL = "226"
    IOVALRD = "62"
    IOVALSET = "63"
    LOCAL_START = "245"
    MMCREMN = "22"
    MMMSOPEN = "9"
    PGABORT = "102"
    POSREGVALRD = "248"
    RECPOS = "236"
    REGVALRD = "247"
    RPRINTF = "89"
    TXCHGPRG = "43"
    TXML_CURANG = "91"
    TXML_CURPOS = "90"
    TXSETLIN = "237"
    VMIP_READVA = "31"
    VMIP_WRITEVA = "32"


class BaseRpcResponse(BaseModel):
    rpc: int
    status: int

    @validator("status", pre=True)
    def set_status(cls, v, values, **kwargs):
        return int(v, 16) if isinstance(v, str) else v


class ReadIoResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.IOVALRD]
    type: IoType
    index: int
    value: int


class WriteIoResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.IOVALSET]


class VariableReadResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.VMIP_READVA]
    prog_name: str
    var_name: str
    type_code: int
    value: str


class VariableWriteResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.VMIP_WRITEVA]


class RegisterReadResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.REGVALRD]
    type: int
    value: t.Union[int, float]
    comment: str


class PosRegValReadResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.POSREGVALRD]
    type: PositionType
    comment: str
    value: str


class DpReadResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.DPREAD]
    value: str


class DpeWriteStrResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.DPEWRITE_STR]
    value: str


class TxSetLinResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.TXSETLIN]


class TxChgPrgResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.TXCHGPRG]


class LocalStartResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.LOCAL_START]


class ExecKclCommandResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.CPKCL]


class RemotePrintfResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.RPRINTF]


class IoGetPnResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.IOGETPN]
    value: str


class IoDefPnResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.IODEFPN]


class IoGetAllResponseElement(BaseModel):
    index: int
    val: int
    sim: bool
    comment: str


class IoGetAllResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.IOGTALL]
    value: t.List[IoGetAllResponseElement]


class GetRawFileLine(BaseModel):
    buf: bytes

    @validator("buf", pre=True)
    def decode_buf(cls, v):
        return urlsafe_b64decode(v)


class GetRawFileResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.GET_RAW_FILE]
    lines: t.List[GetRawFileLine]


class GetFileListResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.GTFILIST]
    value: str


class TxMlCurPosResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.TXML_CURPOS]
    value: str


class TxMlCurAngResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.TXML_CURANG]
    value: str


class ProgAbortResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.PGABORT]


# from https://github.com/pydantic/pydantic/discussions/3754#discussioncomment-2076473
AnnotatedResponseType = te.Annotated[
    t.Union[
        ExecKclCommandResponse,
        DpeWriteStrResponse,
        DpReadResponse,
        GetRawFileResponse,
        GetFileListResponse,
        IoGetPnResponse,
        IoDefPnResponse,
        IoGetAllResponse,
        LocalStartResponse,
        PosRegValReadResponse,
        ProgAbortResponse,
        ReadIoResponse,
        RegisterReadResponse,
        RemotePrintfResponse,
        TxChgPrgResponse,
        TxSetLinResponse,
        TxMlCurAngResponse,
        TxMlCurPosResponse,
        VariableReadResponse,
        WriteIoResponse,
    ],
    # unfortunately, it looks like discriminator values are checked before type
    # coercion, so 'rpc' will still be a 'str' instead of an 'int'
    Field(discriminator="rpc"),
]


class RpcResponse(BaseModel):
    name: str
    fastclock: int
    # this will/can break for some COMET responses
    #
    # Only responses with a single element in the 'RPC' field have been
    # observed, but it's formatted as an unbounded list, so technically
    # it would be possible for multiple elements to be returned.
    #
    # either a specific type, or on error, try BaseRpcResponse (it's likely
    # parsing fails because status != 0x00)
    RPC: t.List[t.Union[AnnotatedResponseType, BaseRpcResponse]]