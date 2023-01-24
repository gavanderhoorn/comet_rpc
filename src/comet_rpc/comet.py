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

from json import loads as json_loads
import requests
import typing as t

from urllib import parse

from .exceptions import (
    AuthenticationException,
    BadElementInStructureException,
    BadVariableOrRegisterIndexException,
    DeserialisationException,
    DictElementNotFoundException,
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
from .fr_errors import ErrorDictionary
from .kliotyps import IoType
from .messages import (
    DpeWriteStrResponse,
    ExecKclCommandResponse,
    GetFileListResponse,
    GetRawFileResponse,
    IoDefPnResponse,
    IoGetAllResponse,
    IoGetPnResponse,
    LocalStartResponse,
    PosRegValReadResponse,
    ProgAbortResponse,
    ReadIoResponse,
    RegisterReadResponse,
    RemotePrintfResponse,
    RpcId,
    RpcResponse,
    TxChgPrgResponse,
    TxMlCurAngResponse,
    TxMlCurPosResponse,
    TxSetLinResponse,
    VariableReadResponse,
    VariableWriteResponse,
    WriteIoResponse,
)


def _call(
    server: str,
    function: RpcId,
    return_raw: bool = False,
    request_timeout: float = 1.0,
    query_str: str = "",
    **kwargs,
) -> t.Union[RpcResponse, str]:
    """Invoke the RPC `function` via the COMET interface on `server`.

    This uses `requests.get(..)` to interact with `COMET` on the FANUC
    controller. All keyword arguments are passed as parameters to
    `requests.get(..)`, and they are expected to be the parameters the
    invoked RPC requires.

    By default, this function will try to parse the returned JSON response
    document. Callers can set `return_raw` to `True` to disable this and
    get access to the raw response text.

    If `query_str` is not the empty string, no query arguments / parameters
    will be encoded (ie: any `kwargs` present will be ignored). Instead, the
    query string passed will be appended to the base COMET rpc URL path and
    directly forwarded to `requests.get(..)`.

    NOTE: `query_str` MUST NOT include the question mark.

    So far, only RPCs which take their arguments in the form of query
    parameters have been observed. Therefore, only the GET HTTP method
    is used to interface with COMET. It's possible POST can also be used,
    but there is no information on how or which RPCs take their arguments
    in the form of a POST body.

    :param server: Hostname or IP address of COMET RPC server
    :param function: The RPC to invoke
    :param return_raw: Whether or not the caller expects a parsed response document
      to be returned
    :param request_timeout: How long to wait on a response from COMET
    :param query_str: Query to send to COMET instead of keyword args
    :param kwargs: All named key:value pairs will be forwarded as query parameters
      to `requests.get(..)`
    :returns: A parsed response document object or a raw response string (depending
      on `return_raw`)
    :raises AuthenticationException: If COMET returned an unauthenticated error
    :raises DeserialisationException: If the response document could be parsed, but
      contains an expected number of RPC elements
    :raises LockedResourceException: If COMET returned an access is forbidden error
    :raises NoSuchMethodException: If the COMET server does not recognise the passed
      RPC ID
    :raises UnexpectedResponseContentException: If the JSON response document was
      malformed, or contained unexpected content
    :raises UnexpectedResultCodeException: If COMET returned any status code than
      OK (200)
    """

    # TODO: see whether we can use the server on :3080 instead
    port = 80
    url = f"http://{server}:{port}/COMET/rpc"
    # see how much we need to pretend to be iRProgrammer
    headers = {
        "Referer": f"http://{server}:{port}",
        "Accept": "application/json, text/javascript, */*",
    }
    if query_str:
        if kwargs:
            raise ValueError("Keyword args cannot be combined with a 'query_str'")

        # be nice
        if query_str[0] == "?":
            query_str = query_str[1:]
        if query_str[0] == "&":
            query_str = query_str[1:]

        # assume caller has provided a custom query string, so do not construct
        # nor encode a 'params' dict, but GET just the URL passed in
        url = f"{url}?func={function.name}&{query_str}"
        r = requests.get(url, headers=headers, timeout=request_timeout)

    else:
        # COMET server expects percent-quoted entities, so quote ourselves using
        # the correct function
        params = parse.urlencode(
            {"func": function.name, **kwargs}, quote_via=parse.quote
        )
        r = requests.get(url, headers=headers, params=params, timeout=request_timeout)

    # provide caller with appropriate exceptions
    if r.status_code == requests.codes.unauthorized:
        raise AuthenticationException("Authentication failed (Karel?)")
    if r.status_code == requests.codes.forbidden:
        raise LockedResourceException("Access is forbidden/locked (Karel?)")
    if r.status_code != requests.codes.ok:
        raise UnexpectedResultCodeException(
            f"Expected: {requests.codes.ok}, got: {r.status_code}"
        )

    # if requested, return the complete response in text form. This can help
    # callers deal with malformed JSON returned by COMET sometimes (looking
    # at you IOVALSET)
    if return_raw:
        return r.text

    # Check whether we got a malformed response document. It could look like
    # this:
    #
    #   {"FANUC":{"name":"<HOSTNAME>","fastclock":"<SOME_VALUE>","RPC":]}}
    #
    # This has been reported on a real R-30iB+ running V9.3074 of the system
    # software. iRProgrammer seems to ignore this, so we will as well.
    #
    # For now we add special handling for the IOVALSET case here. Not sure I
    # like this very much.
    #
    # TODO: come up with a better way to deal with malformed responses
    response_text = r.text
    if '"RPC":]}}' in response_text:
        if function == RpcId.IOVALSET:
            # we can only assume the call succeeded, so fixup the response
            response_text = response_text.replace(
                '"RPC":]}}',
                f'"RPC":[{{"rpc":"{RpcId.IOVALSET.value}","status":"0x0"}}]}}}}',
            )

        # no special handling, just inform caller
        else:
            raise UnexpectedResponseContentException(
                f"Malformed response: '{response_text}'"
            )

    # try to parse as JSON. If we've patched the response document earlier
    # this should now succeed for those cases where we initially received a
    # problematic response as well.
    ret = json_loads(response_text)

    # make sure we've received a "Fanuc RPC response"
    if not len(ret) == 1 or "FANUC" not in ret:
        raise UnexpectedResponseContentException("No 'FANUC' in response")

    # parse (and validate) response JSON
    response = RpcResponse(**ret["FANUC"])
    num_rpc_eles = len(response.RPC)
    if num_rpc_eles != 1:
        raise DeserialisationException(
            f"Too many response elements: expected 1, got {num_rpc_eles}"
        )
    if response.RPC[0].rpc == -1:
        raise NoSuchMethodException(f"No such RPC: '{function.value}'")

    # leave checking RPC status codes to caller. They'll have more context.

    return response


def dpewrite_str(server: str, error_code: int) -> DpeWriteStrResponse:
    """Return a string rendering of `error_code`.

    :param server: Hostname or IP address of COMET RPC server
    :param error_code: FANUC facility + error code integer
    :returns: The parsed response document
    :raises DictElementNotFoundException: If `error_code` cannot be found in any
      dictionary
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(server, function=RpcId.DPEWRITE_STR, ercode=error_code)

    ret = response.RPC[0]

    if ret.status == ErrorDictionary.DICT_005:
        raise DictElementNotFoundException(f"No such element: 0x{error_code:06X}")
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)

    return ret


def exec_kcl(server: str, cmd: str) -> ExecKclCommandResponse:
    """Execute the KCL command `cmd` on the controller.

    This is similar to the `KCL` and `KCLDO` 'CGI programs' supported by FANUC
    controllers, but wrapped in a JSON-RPC interface.

    Command strings may contain whitespace, which will be correctly encoded by
    `comet_rpc` before passing it to `COMET`.

    Refer to the FANUC Karel Reference Manual for more information on KCL commands.

    :param server: Hostname or IP address of COMET RPC server
    :param cmd: The KCL command string to execute
    :returns: The parsed response document
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(server, function=RpcId.CPKCL, kcl_cmd=cmd)

    ret = response.RPC[0]
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)
    return ret


def get_raw_file(server: str, file: str) -> GetRawFileResponse:
    """Retrieve contents of `file` as a sequence of byte strings.

    NOTE: COMET returns lines from the file exactly as they are, so including
    the last null-byte.

    :param server: Hostname or IP address of COMET RPC server
    :param file: Windows-like path to the file to download
    :returns: The parsed response document
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(server, function=RpcId.GET_RAW_FILE, file=file)

    ret = response.RPC[0]
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)
    return ret


def gtfilist(server: str, path_name: str) -> GetFileListResponse:
    """Download a directory listing for the drive/device/directory `path_name`.

    Setting `path_name="*"` will return all files and directories in the
    current working directory on the controller (ie: active device and directory).

    NOTE: for listing files and directories in the root of a device, make sure
    to append `:`, but not `\\`.

    :param server: Hostname or IP address of COMET RPC server
    :param path_name: A Windows-style path to list the contents of
    :returns: The parsed response document
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(server, function=RpcId.GTFILIST, path_name=path_name)

    ret = response.RPC[0]
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)
    return ret


def iodefpn(server: str, typ: IoType, index: int, comment: str) -> IoDefPnResponse:
    """Set the comment of the IO port at `index` to `comment`.

    :param server: Hostname or IP address of COMET RPC server
    :param typ: The type of IO port
    :param index: The specific port to retrieve the comment for (1-based)
    :param comment: The new comment
    :returns: The parsed response document
    :raises InvalidIoIndexException: If the `index` is not a valid value for the
      `type` specified
    :raises InvalidIoTypeException: If `type` is not a recognised IO type
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(
        server,
        function=RpcId.IODEFPN,
        type=typ.value,
        index=index,
        comment=comment,
    )

    ret = response.RPC[0]

    # check call succeeded
    if ret.status == ErrorDictionary.PRIO_001:
        raise InvalidIoTypeException(f"Illegal port type: {typ.value}")
    if ret.status == ErrorDictionary.PRIO_002:
        raise InvalidIoIndexException(f"Illegal port number for port: {index}")
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)

    return ret


def iogetpn(server: str, typ: IoType, index: int) -> IoGetPnResponse:
    """Retrieve the comment of the IO port at `index`.

    :param server: Hostname or IP address of COMET RPC server
    :param typ: The type of IO port
    :param index: The specific port to retrieve the comment for (1-based)
    :returns: The parsed response document
    :raises InvalidIoIndexException: If the `index` is not a valid value for the
      `type` specified
    :raises InvalidIoTypeException: If `type` is not a recognised IO type
    :raises NoCommentOnIoPortException: If the port has no comment configured
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(server, function=RpcId.IOGETPN, type=typ.value, index=index)

    ret = response.RPC[0]

    # check call succeeded
    if ret.status == ErrorDictionary.PRIO_001:
        raise InvalidIoTypeException(f"Illegal port type: {typ.value}")
    if ret.status == ErrorDictionary.PRIO_002:
        raise InvalidIoIndexException(f"Illegal port number for port: {index}")
    if ret.status == ErrorDictionary.PRIO_030:
        raise NoCommentOnIoPortException(f"No comment available for port: {index}")
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)

    return ret


def iogtall(server: str, typ: IoType, index: int, count: int) -> IoGetAllResponse:
    """Retrieve state of `count` IO ports of type `type` starting at `index`.

    NOTE: might not be supported on all versions of V9.30 system software.

    NOTE 2: `COMET` does not appear to check whether the controller is configured
    with the request type of IO port, nor whether the requested number of IO
    ports to be read exists. This means requests for 1e6 ports of type 12345 will
    be serviced. The returned data will be bogus, and the controller will
    struggle to process the request.

    :param server: Hostname or IP address of COMET RPC server
    :param typ: The type of IO port
    :param index: The specific port to retrieve the comment for (1-based)
    :param count: The number of IO ports to read
    :returns: The parsed response document
    :raises InvalidIoIndexException: If the `index` is not a valid value for the
      `type` specified
    :raises InvalidIoTypeException: If `type` is not a recognised IO type
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(
        server, function=RpcId.IOGTALL, type=typ.value, index=index, cnt=count
    )

    ret = response.RPC[0]

    if ret.status == ErrorDictionary.PRIO_001:
        raise InvalidIoTypeException(f"Illegal port type: {typ.value}")
    if ret.status == ErrorDictionary.PRIO_002:
        raise InvalidIoIndexException(f"Illegal port number for port: {index}")
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)

    return ret


def iovalrd(server: str, typ: IoType, index: int) -> ReadIoResponse:
    """Retrieve the value of the IO port of type `typ` at `index`.

    :param server: Hostname or IP address of COMET RPC server
    :param typ: The type of IO port to read from
    :param index: The specific port to read from (1-based)
    :returns: The parsed response document
    :raises InvalidIoIndexException: If the `index` is not a valid value for the
      `type` specified
    :raises InvalidIoTypeException: If `type` is not a recognised IO type
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(server, function=RpcId.IOVALRD, type=typ.value, index=index)

    ret = response.RPC[0]

    # check call succeeded
    if ret.status == ErrorDictionary.PRIO_001:
        raise InvalidIoTypeException(f"Illegal port type: {typ.value}")
    if ret.status == ErrorDictionary.PRIO_002:
        raise InvalidIoIndexException(f"Illegal port number for port: {index}")
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)

    return ret


def iovalset(server: str, typ: IoType, index: int, value: int) -> WriteIoResponse:
    """Update the `value` of the IO port of type `typ` at `index`.

    `value` will be `int`, even for `BOOLEAN` ports on the controller. In those
    cases, zero appears to be interpreted as `FALSE` (or `OFF`), while any non-zero
    value appears to be interpreted as `TRUE` (or `ON`).

    Analogue IO ports should also be written to using `int` (instead of `float`),
    just as in Karel programs.

    NOTE: certain system software versions (V9.3074 on R-30iB+ fi) appear to
    return a malformed response for this RPC. _call(..) handles this for us by
    patching up the returned JSON. Just as iRProgrammer, we pretend everything
    is fine (as we have no way of knowing whether it isn't). This will make
    detecting errors more difficult/impossible, but there doesn't appear to be
    a way around this.

    :param server: Hostname or IP address of COMET RPC server
    :param typ: The type of IO port to write to
    :param index: The specific port to write to (1-based)
    :param value: The value to write to the port
    :returns: The parsed response document
    :raises InvalidIoIndexException: If the `index` is not a valid value for the
      `type` specified
    :raises InvalidIoTypeException: If `type` is not a recognised IO type
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(
        server, function=RpcId.IOVALSET, type=typ.value, index=index, value=value
    )

    ret = response.RPC[0]

    # check call succeeded
    if ret.status == ErrorDictionary.PRIO_001:
        raise InvalidIoTypeException(f"Illegal port type: {typ.value}")
    if ret.status == ErrorDictionary.PRIO_002:
        raise InvalidIoIndexException(f"Illegal port number for port: {index}")
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)

    return ret


def local_start(server: str, value: int) -> LocalStartResponse:
    response = _call(server, function=RpcId.LOCAL_START, value=value)

    ret = response.RPC[0]
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)
    return ret


def posregvalrd(server: str, index: int, grp_num: int = 1) -> PosRegValReadResponse:
    """Retrieve the contents of the position register at `index` for group `grp_num`.

    :param server: Hostname or IP address of COMET RPC server
    :param index: The index of the position register (1-based)
    :param grp_num: The motion group to retrieve the position register contents for
    :returns: The parsed response document
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(server, function=RpcId.POSREGVALRD, grp_num=grp_num, index=index)

    ret = response.RPC[0]
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)
    return ret


def prog_abort(server: str, prog_name: str = "*ALL*") -> ProgAbortResponse:
    """Attempt to ABORT the program `prog_name`.

    Set `prog_name` to `"*ALL"` to attempt to abort all (user) tasks.

    :param server: Hostname or IP address of COMET RPC server
    :param prog_name: Name of the program to abort
    :returns: The parsed response document
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(server, function=RpcId.PGABORT, task_name=prog_name)

    ret = response.RPC[0]
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)
    return ret


def regvalrd(server: str, index: int) -> RegisterReadResponse:
    """Retrieve the contents of the register at `index`.

    Depending on the value stored in the register, this will return an `int` or
    a `float`.

    :param server: Hostname or IP address of COMET RPC server
    :param index: The index of the position register (1-based)
    :returns: The parsed response document
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(server, function=RpcId.REGVALRD, index=index)

    ret = response.RPC[0]
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)
    return ret


def rprintf(server: str, line: str) -> RemotePrintfResponse:
    """Append the string `line` to the console log on the controller.

    This will cause the string `line` to be appended to the console log on the
    FANUC controller (and consequently show up in `CONSLOG.DG` and `CONSTAIL.DG`)
    as if it was logged by a program running on the controller.

    Log lines may contain whitespace, which will be correctly encoded by
    `comet_rpc` before passing it to `COMET`.

    :param server: Hostname or IP address of COMET RPC server
    :param line: The line to append to the log
    :returns: The parsed response document
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    # COMET expects an anonymous query arg for RPRINTF, which requests doesn't
    # support, so compose query string ourselves and pass to _call(..)
    query_str = f"={parse.quote(line)}"
    response = _call(server, function=RpcId.RPRINTF, query_str=query_str)
    ret = response.RPC[0]
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)
    return ret


def txchgprg(server: str, prog_name: str) -> TxChgPrgResponse:
    """Open the program `prog_name` on the TP.

    :param server: Hostname or IP address of COMET RPC server
    :param prog_name: Name of the program to open
    :returns: The parsed response document
    :raises ProgramDoesNotExistException: If the program `prog_name` does not actually
      exist on the controller
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(server, function=RpcId.TXCHGPRG, prog_name=prog_name.upper())

    ret = response.RPC[0]

    # check call succeeded
    if ret.status == ErrorDictionary.MEMO_073:
        raise ProgramDoesNotExistException(prog_name.upper())
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)

    return ret


def txml_curang(server: str, grp_num: int = 1) -> TxMlCurAngResponse:
    """Returns the current pose of group `grp_num`, in joint angles.

    :param server: Hostname or IP address of COMET RPC server
    :param grp_num: The motion group (ie: robot) for which to retrieve the current pose
    :returns: The parsed response document
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(server, function=RpcId.TXML_CURANG, grp_num=grp_num)

    ret = response.RPC[0]
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)
    return ret


def txml_curpos(
    server: str, pos_rep: int, pos_type: int = 6, grp_num: int = 1
) -> TxMlCurPosResponse:
    """Returns the current pose of group `grp_num`, as a Cartesian pose.

    :param server: Hostname or IP address of COMET RPC server
    :param pos_rep:
    :param pos_type:
    :param grp_num: The motion group (ie: robot) for which to retrieve the current pose
    :returns: The parsed response document
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(
        server,
        function=RpcId.TXML_CURPOS,
        pos_rep=pos_rep,
        pos_type=pos_type,
        grp_num=grp_num,
    )

    ret = response.RPC[0]
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)
    return ret


def txsetlin(server: str, prog_name: str, line_num: int = 1) -> TxSetLinResponse:
    """Open the program `prog_name` and move cursor to `line_num`.

    NOTE: this most likely can only open TP programs, not Karel.

    :param server: Hostname or IP address of COMET RPC server
    :param prog_name: Name of the program to open
    :param line_num: Line number within `prog_name` to move cursor to (1-based)
    :returns: The parsed response document
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    """
    response = _call(
        server,
        function=RpcId.TXSETLIN,
        prog_name=prog_name.upper(),
        line_num=line_num,
    )

    ret = response.RPC[0]
    if ret.status != 0:
        raise UnexpectedRpcStatusException(ret.status)
    return ret


def vmip_readva(server: str, prog_name: str, var_name: str) -> VariableReadResponse:
    """Read the variable 'var_name' in program 'prog_name'.

    Set `prog_name` to `"*SYSTEM*"` to read system variables.

    :param server: Hostname or IP address of COMET RPC server
    :param prog_name: Name of the program hosting the variable
    :param var_name: Name of the variable to read
    :returns: The parsed response document
    :raises BadVariableOrRegisterIndexException: If the name used to refer to the
      variable is not formatted properly
    :raises NoDataDefinedForProgramException: If the program does not exist or hosts
      no readable variable data
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    :raises UnknownVariableException: If the variable cannot be found
    """
    response = _call(
        server,
        function=RpcId.VMIP_READVA,
        prog_name=prog_name.upper(),
        var_name=var_name.upper(),
    )

    ret = response.RPC[0]

    # check call succeeded
    if ret.status != 0:
        if ret.status == ErrorDictionary.VARS_006:
            raise UnknownVariableException(f"'{var_name.upper()}'")
        if ret.status == ErrorDictionary.VARS_011:
            raise NoDataDefinedForProgramException(f"'{prog_name.upper()}'")
        if ret.status == ErrorDictionary.VARS_024:
            raise BadVariableOrRegisterIndexException(f"'{var_name.upper()}'")
        raise UnexpectedRpcStatusException(ret.status)

    return ret


def vmip_writeva(
    server: str, prog_name: str, var_name: str, value: t.Union[str, int, float]
) -> VariableWriteResponse:
    """Write 'value' to the variable 'var_name' in program 'prog_name'.

    Set `prog_name` to `"*SYSTEM*"` to write to system variables.

    `value` will always be submitted as a string, even for (system) variables
    which are of a different type. `COMET` apparently tries to parse the
    string representation and converts it to the required type when possible.
    The string representations are expected to be identical to those found in
    `.VA` files.

    NOTE: this seems to be mostly used to write to variables with primitive
    types (ie: `INTEGER`, `REAL`, `BOOLEAN` and `STRING[n]`). Writing to
    arrays should be done one element at a time. Structures can most likely
    also only be written to by addressing individual fields.

    :param server: Hostname or IP address of COMET RPC server
    :param prog_name: Name of the program hosting the variable
    :param var_name: Name of the variable to read
    :param value: The (string representation of the) value to write to the variable
    :returns: The parsed response document
    :raises BadElementInStructureException: If the variable name does not correctly
      refer to a field
    :raises BadVariableOrRegisterIndexException: If the name used to refer to the
      variable is not formatted properly
    :raises NoDataDefinedForProgramException: If the program does not exist or hosts
      no readable variable data
    :raises UnexpectedRpcStatusException: on any other non-zero RPC status code
    :raises UnknownVariableException: If the variable cannot be found
    """
    response = _call(
        server,
        function=RpcId.VMIP_WRITEVA,
        prog_name=prog_name.upper(),
        var_name=var_name.upper(),
        value=value,
    )

    ret = response.RPC[0]

    # check call succeeded
    if ret.status != 0:
        if ret.status == ErrorDictionary.VARS_006:
            raise UnknownVariableException(f"'{var_name.upper()}'")
        if ret.status == ErrorDictionary.VARS_011:
            raise NoDataDefinedForProgramException(f"'{prog_name.upper()}'")
        if ret.status == ErrorDictionary.VARS_024:
            raise BadVariableOrRegisterIndexException(f"'{var_name.upper()}'")
        if ret.status == ErrorDictionary.VARS_049:
            raise BadElementInStructureException(f"'{var_name.upper()}'")
        raise UnexpectedRpcStatusException(ret.status)

    return ret
