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


class CometRpcException(Exception):
    pass


class LockedResourceException(CometRpcException):
    pass


class AuthenticationException(CometRpcException):
    pass


class UnexpectedResultCodeException(CometRpcException):
    pass


class UnexpectedResponseContentException(CometRpcException):
    pass


class UnexpectedRpcStatusException(CometRpcException):
    def __init__(self, status):
        self._status = status

    @property
    def status(self) -> int:
        return self._status


class DeserialisationException(CometRpcException):
    pass


class InvalidIoTypeException(CometRpcException):
    pass


class InvalidIoIndexException(CometRpcException):
    pass


# PRIO-023
class NoPortsOfThisTypeException(CometRpcException):
    pass


class NoSuchMethodException(CometRpcException):
    pass


# VARS-006
class UnknownVariableException(CometRpcException):
    pass


# VARS-011
class NoDataDefinedForProgramException(CometRpcException):
    pass


# VARS-024: You are attempting to use an invalid index into an array or path
class BadVariableOrRegisterIndexException(CometRpcException):
    pass


# VARS-049: ASCII value specified is invalid
class BadElementInStructureException(CometRpcException):
    pass


# MEMO-071
class PositionDoesNotExistException(CometRpcException):
    pass


# MEMO-073: The specified program does not exist in the system
class ProgramDoesNotExistException(CometRpcException):
    pass


# DICT-004: Dictionary not found
class DictNotFoundException(CometRpcException):
    pass


# DICT-005: Dictionary element not found
class DictElementNotFoundException(CometRpcException):
    pass


# PRIO-030: <doesn't appear to have a documented cause>
class NoCommentOnIoPortException(CometRpcException):
    pass
