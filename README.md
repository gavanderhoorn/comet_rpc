# comet_rpc

[![license - apache 2.0](https://img.shields.io/:license-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/gavanderhoorn/comet_rpc/workflows/CI/badge.svg?branch=master)](https://github.com/gavanderhoorn/comet_rpc/actions?query=workflow%3ACI)
[![Github Issues](https://img.shields.io/github/issues/gavanderhoorn/comet_rpc.svg)](https://github.com/gavanderhoorn/comet_rpc/issues)

## Discussion

If you happen to find this useful, leave a quick note in the [Discussions section](https://github.com/gavanderhoorn/comet_rpc/discussions).
If something doesn't work, open an issue [on the tracker](https://github.com/gavanderhoorn/comet_rpc/issues).

## Overview

This is a low-level Python wrapper around the JSON-RPC interface offered by the `COMET` extension of FANUC's web server on R-30iB and R-30iB+ controllers (ie: V8 and up, although older than V9 has a (very) limited interface).
`COMET` is used by iRProgrammer and a couple of other web-based UIs offered by FANUC on their more recent controller series.

See [Requirements](#requirements) for some more information on required options.

**NOTE**: this is only meant as an example of using `COMET`'s RPC interface.
There is no official documentation on this interface, and it's likely not intended to be used by anything other than FANUC's own products.
Use with caution.

Proper integration of a FANUC controller with an external application or workcell should be done using either the PCDK, RMI (`R912`), OPC-UA, a fieldbus or similar technology.
The scripts and functionality provided here are only a convenience and are only intended to be used in academic and laboratory settings.
They allow incidental external access to a controller without needing to use any additional hardware.
Do not use this on production systems or in contexts where any kind of determinism is required.
The author recommends using PCDK, RMI, OPC-UA and/or any of the supported fieldbuses in those cases.

## TOC

1. [Status](#status)
1. [Requirements](#requirements)
1. [Compatibility](#compatibility)
1. [Installation](#installation)
1. [Example usage](#example-usage)
1. [Supported RPCs](#supported-rpcs)
1. [Limitations / Known issues](#limitations--known-issues)
1. [Performance](#performance)
1. [Security](#security)
1. [Related projects](#related-projects)
1. [Bugs, feature requests, etc](#bugs-feature-requests-etc)
1. [FAQ](#faq)
1. [Disclaimer](#disclaimer)

## Status

This package is a work-in-progress.
As there is no documentation on `COMET`, it's been implemented based on information learned from observing iRProgrammer and related web-based UIs.

Expect frequent breakage and missing functionality.

See also the [FAQ](#faq).

## Requirements

Requirements are a little unclear at this moment, but it appears `COMET` is installed on all controllers with the base *Web Server* (`HTTP`) option and at least V8 of the system software (see notes about [Compatibility](#compatibility) below).
Interestingly, even though `COMET` is primarily used by iRProgrammer, option `J767` does not appear to be a requirement for it to be installed.

The main other requirement is a functioning networking setup.
Make sure you can ping the controller and the controller's website shows up when opening `http://robot_ip` in a browser.
Configuration of *HTTP Authentication* is not needed, as `COMET` RPCs do not appear to be affected by it (see [Security](#security) for some more discussion).

## Compatibility

### Controllers

Compatibility has only been tested with R-30iB+ controllers running V9.30 and V9.40 of the system software.
It's possible R-30iB with V8.x supports the `COMET` RPC interface as well, but this has not been tested.

### Operating Systems

The library has been written for Python version 3.
No specific OS dependencies are known, meaning all platforms with a Python 3 interpreter should be supported.
Only Windows 10, Ubuntu Bionic and Focal have been extensively tested however.

## Installation

### Controller

As the `COMET` RPC interface is part of the controller's web server, no installation nor setup on the FANUC side should be necessary.

### Package

It's recommended to use a virtual Python 3 environment and install the package in it.
The author has primarily used Python 3.8, but other versions are expected to work, though they are not actively tested.

Future versions may be released to PyPi.

Example (installs `comet_rpc` `0.2.4`; be sure to update the URL to download the desired version):

```shell
python3 -m venv $HOME/venv_comet_rpc
source $HOME/venv_comet_rpc/bin/activate
pip install -U pip
pip install -U wheel setuptools
pip install https://github.com/gavanderhoorn/comet_rpc/archive/0.2.4.tar.gz
```

## Example usage

The current version of this package does not come with any example scripts.
The subsection below is expected to be sufficient to clarify basic usage of the RPC interface.

### Library

This resets the controller, sets the override to 100% and finally reads the `DO[1]` IO port and retrieves its comment:

```python
from comet_rpc import (
    exec_kcl,
    IoType,
    iogetpn,
    iovalrd,
    vmip_writeva,
)

# IP address or hostname of the R-30iB(+) controller
server = "..."

exec_kcl(server, "reset")
vmip_writeva(server, "*SYSTEM*", "$MCR.$GENOVERRIDE", value=100)
dout1_val = iovalrd(server, IoType.DigitalOut, index=1).value
dout1_cmt = iogetpn(server, IoType.DigitalOut, index=1).value
...
```

Note the lack of error detection and handling to keep the example brief.

## Supported RPCs

The following table shows an overview of known RPCs, whether they are currently supported by `comet_rpc` (column `Supp.?`) and which version of `COMET` appears to support them ("appears", as this information is based on experiments, there is no public, authoritative source of truth available).

The last two columns of the table clarify the minimum version of system software that supports a particular RPC.
An entry in the `8.x` column implies an RPC is supported starting with version `8.x`.
Use the value in the cell to determine the minor version number.

For RPCs with no information in those columns this information hasn't been determined yet.

<details>
<summary>Click to expand</summary>
<br/>

| Name              | Description                       | Supp.? | 8.x  | 9.x  |
|:------------------|:----------------------------------|:------:|:-----|:-----|
| CHGOVRD           | Change override                   |   Y    |      | .40+ |
| CKTRKPRG          | Check linetrack attributes        |   N    |      | .40+ |
| CLLB_CODE_REQ     |                                   |   N    |      | .40+ |
| CLLB_PAYLOAD_CONF |                                   |   N    |      | .40+ |
| CPKCL             | Execute KCL command               |   Y    |      | .30+ |
| DCS_CHECK_APPLY   |                                   |   N    |      | .40+ |
| DCS_CHECK_CODE    |                                   |   N    |      | .40+ |
| DCS_VRFY_REQ      |                                   |   N    |      | .40+ |
| DPEWRITE_STR      | Retrieve error code description   |   Y    |      | .10+ |
| DPREAD            | Read element from dictionary      |   Y    | .30+ |      |
| ERPOST            | Post an error to the log          |   N    |      | .10+ |
| EXEC_TXCMND       |                                   |   N    | .10+ |      |
| GET_FORM          |                                   |   N    | .10+ |      |
| GET_RAW_FILE      | Get raw byte contents of file     |   Y    |      | .10+ |
| GETFOCUS          |                                   |   N    |      | .10+ |
| GTFILIST          | Get list of files in directory    |   Y    |      | .40+ |
| GTMCRLST          | Get list of macros                |   Y    |      | .10+ |
| GTPIDLST          | Get list of posregs in TP program |   Y    |      | .40+ |
| IOASGLOG          | Update IO configuration           |   Y    |      | .40+ |
| IOCKSIM           | Check simulated status of IO port |   Y    | .30+ |      |
| IODEFPN           | Set/update comment on IO port     |   Y    |      | .10+ |
| IODRYRUN          | Treat all IO as-if simulated      |   N    |      | .40+ |
| IOGETASG          | Retrieve IO configuration         |   Y    |      | .40+ |
| IOGETHDB          | Retrieve the "HW database"        |   Y    |      | .40+ |
| IOGETPN           | Retrieve comment on IO port       |   Y    |      | .10+ |
| IOGTALL           | Read IO ports, batch-wise         |   Y    |      | .30+ |
| IOSIM             | Set IO port to simulated          |   Y    | .30+ |      |
| IOUNSIM           | Clear simulated state of IO port  |   Y    | .30+ |      |
| IOVALRD           | Read IO port                      |   Y    | .30+ |      |
| IOVALSET          | Write to IO port                  |   Y    | .30+ |      |
| IOWETRUN          | Stop treating all IO as simulated |   N    |      | .40+ |
| LOCAL_PAUSE       |                                   |   N    |      | .10+ |
| LOCAL_START       |                                   |   Y    |      | .10+ |
| MG_RECPOS         |                                   |   N    |      | .40+ |
| MMCHGTYP          | Change the type of a program      |   N    |      | .10+ |
| MMCREMN           | Create a TP program               |   N    |      | .10+ |
| MMDELPOS          | Remove a position from a program  |   N    |      | .10+ |
| MMDELPRG          | Delete a program                  |   N    |      | .10+ |
| MMGETATR          | Read program attribute            |   N    |      | .10+ |
| MMGETTYP          | Read 'program type' (TP, PC, etc) |   Y    |      | .10+ |
| MMRENPRG          | Rename a program                  |   N    |      | .10+ |
| MMSETATR          | Write program attribute           |   N    |      | .10+ |
| MNCHGREP          | Convert position representation   |   N    |      | .10+ |
| MNCPYPRG          | Copy a program                    |   N    |      | .10+ |
| OSSNDPKT_EXT      |                                   |   N    |      | .10+ |
| PASTELIN          | Duplicate/move lines in a TP prog |   Y    |      | .40+ |
| PGABORT           | Abort all/a specific program(s)   |   Y    |      | .10+ |
| PMCUPFN           |                                   |   N    |      | .10+ |
| PMCUPRQ           |                                   |   N    |      | .10+ |
| PMCVALRD          |                                   |   N    |      | .10+ |
| PMON_CAN_PKT      |                                   |   N    | .10+ |      |
| PMON_DISCONNECT   |                                   |   N    | .10+ |      |
| PMON_GET_PKT      |                                   |   N    | .10+ |      |
| PMON_START_MON    |                                   |   N    | .10+ |      |
| PMON_STOP_MON     |                                   |   N    | .10+ |      |
| PMON_VERIFY_PKT   |                                   |   N    | .30+ |      |
| POSREGVALRD       | Read a position register          |   Y    |      | .10+ |
| RECPOS            | Teach position (in program)       |   N    |      | .10+ |
| REGVALRD          | Read a register (int/real)        |   Y    |      | .10+ |
| RPRINTF           | Print to the controllers conslog  |   Y    | .10+ |      |
| RUN_TASK          | Start a program on the controller |   N    |      | .30+ |
| SCDELETE          | Delete line from program          |   N    |      | .10+ |
| SCEDIT            | Add/replace line to/in program    |   N    |      | .10+ |
| SCGETPOS          | Get position from program         |   N    |      | .40+ |
| SCSETPOS          | Update position in program        |   N    |      | .10+ |
| SET_FORM          |                                   |   N    | .10+ |      |
| SKIP_LINE         | Change active line in paused prog |   N    |      | .40+ |
| TPEXTREQ          |                                   |   N    | .10+ |      |
| TPLINK_DISCONNECT |                                   |   N    |      | .10+ |
| TPLINK_NEW_URL    |                                   |   N    | .10+ |      |
| TPMODE_CHG        |                                   |   N    |      | .40+ |
| TPMULTI_TASKIDX   |                                   |   N    | .30+ |      |
| TPXENSBV_KRL_EXT  |                                   |   N    |      | .10+ |
| TPXENSBV_KRL_TEXT |                                   |   N    |      | .10+ |
| TPXENSUB_EXT      |                                   |   N    |      | .10+ |
| TPXFILSB_EXT      |                                   |   N    |      | .10+ |
| TPXPRGSB_EXT      |                                   |   N    |      | .10+ |
| TXCHGPRG          | Open (and make active) a TP prog  |   Y    |      | .10+ |
| TXLSTPRG_FC       | List programs (specific types)    |   N    |      | .10+ |
| TXML_CURANG       | Return current joint angles       |   Y    |      | .10+ |
| TXML_CURPOS       | Return current TCP pose (XYZWPR)  |   Y    |      | .10+ |
| TXSETLIN          | Open TP prog at specific line     |   Y    |      | .10+ |
| VMIP_READVA       | Read a (system) variable          |   Y    |      | .10+ |
| VMIP_WRITEVA      | Write to a (system) variable      |   Y    | .30+ |      |
| XMLCOPY           | Copy an XML file to another       |   N    |      | .30+ |

</details>

Total supported RPCs: 32 of 85.

## Limitations / Known issues

The following limitations and known issues exist:

* `COMET` (and/or FANUC's web server) seems to return response documents with a `Content-type: text/html` header.
  Because of this, `comet_rpc` just assumes it receives JSON, even if the `content-type` header states otherwise.
* `COMET` sometimes returns malformed response documents.
  `comet_rpc` tries to detect this and either fixes those responses before parsing and validation, or mimics iRProgrammer's behaviour (which is to ignore).
  This makes some actual errors hard to detect.
  A better way to deal with this is being investigated.
* Only a subset of the RPCs exposed by `COMET` is supported by this library.
  Future updates may add support for more RPCs.
* No version checking is implemented (ie: `comet_rpc` will not prevent invoking an RPC on a V8 controller which requires V9)
* Reading and writing (system) variables (`vmip_readva` and `vmip_writeva`) returns and takes `str` representations of those variables instead of more specific types as their values.
  This is partly due to the way `COMET` expects and returns those values and partly due to limited insight into which types are used by FANUC for those values.
  Future updates may improve on this.

## Performance

Even though this library should not be used when performance is a concern, some preliminary figures are presented in this section.

See the following table for an indication of expected RPC performance:

| Platform | SW version | RPC         | avg ms/call |
|:---------|-----------:|-------------|------------:|
| RG       | V9.30P/26  | IOVALRD     |          ~8 |
| RG       | V9.30P/26  | VMIP_READVA |         ~14 |
| R-30iB+  | V9.30P/??  | IOVALRD     |         ~18 |

Note: this is without connection reuse, as it's unclear whether `COMET` supports this for regular RPC invocations.

## Security

`COMET` does not appear to be affected by the settings configured under `Host Comm`, section *HTTP Authentication*.

No authentication challenges have been observed so far, although that does not mean they are not used.

Some RPCs do appear to require a valid connection id argument, and starting up such a session will lock-out the physical teach pendant with a very clear message shown to operators (stating a "remote pendant" is in use).
`comet_rpc` does not currently support any RPCs requiring a connection id, nor does it lock-out the physical pendant.

Users concerned about potential undesired and uncontrolled access to the web server and `COMET` could look into configuring the host blocklist part of the *FANUC Server Access Control* feature.
It's unclear at this point whether any fine-grained control is possible (ie: allow reads, deny all writes), but blocking unknown hosts from interacting with `COMET` would be a first step to making it harder to abuse the JSON-RPC interface.

Refer to section 2.5 *FANUC SERVER ACCESS CONTROL (FSAC)* of the *FANUC Robot series - Ethernet Function - Operator's Manual* (document B-82974EN for the R-30iA, R-30iB and R-30iB+) for more information.

## Related projects

For a similar library which doesn't use `COMET` (and is compatible with older controllers), see [gavanderhoorn/dominh](https://github.com/gavanderhoorn/dominh).

## Bugs, feature requests, etc

Please use the [GitHub issue tracker](https://github.com/gavanderhoorn/comet_rpc/issues).

## FAQ

### What's the status of COMET?

It's likely only intended to be used by FANUC internally in their products.
There is no public documentation which mentions it, which implies it's not a public interface.

### Should this be used in production?

Apart from the fact that `comet_rpc` is a work-in-progress at the moment, it makes use of a (most likely) private interface.
This means FANUC has no obligation to maintain compatibility and they are free to change `COMET` in any way they see necessary without regards for users of this Python library.

Both of these facts make use in production deployments problematic.

See also the *NOTE* in the [Overview](#overview) section, and [Status](#status).

### This is far from production-ready code

Yes, I agree.
See also the *NOTE* in the *Overview* section.

### Why did you not use Go/Rust/Java/Kotlin/Swift/anything but Python?

Time and application requirements: target framework supported Python, so writing `comet_rpc` in Python made sense.

### Should this not be async?

Perhaps.
All implemented RPCs so far are executed in a blocking manner on the FANUC side though, with none of the streaming or event-based ones supported (`PMON_START_MON` et al.).
Future versions may change the default to `async` while offering a blocking version of the API for bw compatibility.

### Does this use Karel?

No.
`COMET` is an extension to / integrated with the embedded web server running on R-30iB(+) controllers and is a native binary.
It does not use Karel, nor is it run in the Karel VM.

### Performance is not as good as it could be

Compared to the PCDK: certainly, but if you need a more performant solution, ask FANUC for a PCDK license or use a fieldbus.
If you have ideas on how to improve performance, post an issue [on the tracker](https://github.com/gavanderhoorn/comet_rpc/issues).

### Can I submit feature/enhancement requests?

Of course!
I can't guarantee I'll have time to work on them though.

### Would you take pull requests which add new features?

Most certainly.
As long as new features (or enhancements of existing functionality) pass CI and are reasonably implemented, they will be merged.

### What's the relation to Dominh?

[gavanderhoorn/dominh](https://github.com/gavanderhoorn/dominh) is/was an experiment to see whether an RPC library for FANUC controllers could be created with as few required options on the controller as possible.
Because of this, it uses methods which are perhaps not the most efficient (such as Karel programs, KCL and `.stm` pages), but at least work on as many controllers as possible.

`comet_rpc` is different: it's a low-level library which directly interfaces with an RPC interface implemented by FANUC, used by some of their web based UIs for CRX robots, iRProgrammer and remote iPendants.
There is no use of Karel, nor KCL.
The only functionality supported is what is offered by `COMET` and known from looking at iRProgrammer.

Technically, Dominh and `comet_rpc` could be used at the same time.

It's also likely Dominh will optionally use `comet_rpc` in the future to make some operations more efficient.

## Disclaimer

The author of this software is not affiliated with FANUC Corporation in any way.
All trademarks and registered trademarks are property of their respective owners, and company, product and service names mentioned in this readme or appearing in source code or other artefacts in this repository are used for identification purposes only.
Use of these names does not imply endorsement by FANUC Corporation.
