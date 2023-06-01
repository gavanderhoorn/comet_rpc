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

from enum import Enum, IntEnum

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
    CHGOVRD = "220"
    CPKCL = "87"
    DPEWRITE_STR = "83"
    DPREAD = "148"
    ERPOST = "85"
    GET_RAW_FILE = "251"
    GTFILIST = "234"
    GTMCRLST = "244"
    GTPIDLST = "228"
    IOASGLOG = "61"
    IOCKSIM = "64"
    IODEFPN = "68"
    IOGETASG = "219"
    IOGETHDB = "218"
    IOGETPN = "67"
    IOGTALL = "226"
    IOSIM = "65"
    IOUNSIM = "66"
    IOVALRD = "62"
    IOVALSET = "63"
    LOCAL_START = "245"
    MMCREMN = "22"
    MMGETTYP = "246"
    MMMSOPEN = "9"
    PASTELIN = "225"
    PGABORT = "102"
    POSREGVALRD = "248"
    RECPOS = "236"
    REGVALRD = "247"
    REMARKLIN = "215"
    RPRINTF = "89"
    SCGETPOS = "14"
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


class IoValRdResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.IOVALRD]
    type: IoType
    index: int
    value: int


class IoValSetResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.IOVALSET]


class VmIpReadVaResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.VMIP_READVA]
    prog_name: str
    var_name: str
    type_code: int
    value: str


class VmIpWriteVaResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.VMIP_WRITEVA]


class RegValRdResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.REGVALRD]
    type: int
    value: t.Union[int, float]
    comment: str


class PosRegValRdResponse(BaseRpcResponse):
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


class CpKclResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.CPKCL]


class RPrintfResponse(BaseRpcResponse):
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


class GtFiListResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.GTFILIST]
    value: t.List[str]

    @validator("value", pre=True)
    def decode_value(cls, v):
        return v.split(",") if isinstance(v, str) else v


class TxMlCurPosResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.TXML_CURPOS]
    value: str


class TxMlCurAngResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.TXML_CURANG]
    value: str


class PgAbortResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.PGABORT]


class IoGetHdbResponseElement(BaseModel):
    rack: int
    slot: int
    devname: str
    pd_port_type: t.List[int]

    @validator("pd_port_type", pre=True)
    def decode_pd_port_type(cls, v):
        return list(map(int, v.split(","))) if isinstance(v, str) else v


class IoGetHdbResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.IOGETHDB]
    data: t.List[IoGetHdbResponseElement]


class ChgOvrdResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.CHGOVRD]


class GtMcrLstResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.GTMCRLST]
    macrolist: t.List[str]


class IoCkSimResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.IOCKSIM]
    type: IoType
    index: int
    # officially an 'int', but bool makes more sense
    value: bool


class IoAsgStatus(IntEnum):
    INVALID = 1
    ACTIVE = 2
    PENDING = 3


class IoGetAsgResponseElement(BaseModel):
    log_port_type: IoType
    fst_log_port: int
    n_log_ports: int
    rack_no: int
    slot_no: int
    phy_port_type: IoType
    fst_phy_port: int
    valid: IoAsgStatus


class IoGetAsgResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.IOGETASG]
    data: t.List[IoGetAsgResponseElement]


class IoSimResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.IOSIM]
    type: IoType
    index: int
    # officially an 'int', but bool makes more sense
    value: bool


class IoUnsimResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.IOUNSIM]


class GetPIdListResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.GTPIDLST]
    pos_cnt: int
    posidlist: t.List[int]


class ScGetPosResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.SCGETPOS]
    comment: str
    value: t.List[str]


class PasteLinResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.PASTELIN]
    lin_num: int


class IoAsgLogResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.IOASGLOG]
    asg_stat: int

    @validator("asg_stat", pre=True)
    def set_asg_stat(cls, v, values, **kwargs):
        return int(v, 16) if isinstance(v, str) else v

class RemarkLinResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.REMARKLIN]



class ProgramType(IntEnum):
    UNKNOWN = 0
    TP = 1  # PT_MNE_UNDEF
    PC = 2  # PT_KRLPRG


class ProgramSubType(IntEnum):
    UNDEF = 0  # PT_MNE_UNDEF
    JOB = 1  # PT_MNE_JOB
    PROC = 2  # PT_MNE_PROC
    MACRO = 3  # PT_MNE_MACRO
    COND = 4  # PT_MNE_COND


class MmGetTypResponse(BaseRpcResponse):
    rpc: t.Literal[RpcId.MMGETTYP]
    prg_typ: ProgramType
    sub_typ: ProgramSubType


# from https://github.com/pydantic/pydantic/discussions/3754#discussioncomment-2076473
AnnotatedResponseType = te.Annotated[
    t.Union[
        ChgOvrdResponse,
        CpKclResponse,
        DpeWriteStrResponse,
        DpReadResponse,
        GetPIdListResponse,
        GetRawFileResponse,
        GtFiListResponse,
        GtMcrLstResponse,
        IoAsgLogResponse,
        IoCkSimResponse,
        IoDefPnResponse,
        IoGetAllResponse,
        IoGetAsgResponse,
        IoGetHdbResponse,
        IoGetPnResponse,
        IoSimResponse,
        IoUnsimResponse,
        IoValRdResponse,
        IoValSetResponse,
        LocalStartResponse,
        MmGetTypResponse,
        PasteLinResponse,
        PgAbortResponse,
        PosRegValRdResponse,
        RegValRdResponse,
        RemarkLinResponse,
        RPrintfResponse,
        ScGetPosResponse,
        TxChgPrgResponse,
        TxMlCurAngResponse,
        TxMlCurPosResponse,
        TxSetLinResponse,
        VmIpReadVaResponse,
        VmIpWriteVaResponse,
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
