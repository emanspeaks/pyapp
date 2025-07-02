# This module contains functions that interact either with the operating system
# the Python interpreter, or conda environments.  Many of these are used in
# early "bootstrap" functions to set up the logging system initially, and thus
# we have versions of these that use the "default" logger or no logging at all.
# There are equivalent functions for each of these in the "plain" system module
# that provide wrappers around these once the logging system is initialized in
# the app.

import sys
from types import ModuleType
from pathlib import Path
from shutil import chown, copy2
from logging import getLogger, Logger
from importlib.util import spec_from_file_location, module_from_spec
from shlex import split as shsplit

from ..logging import DEBUGLOW, log_func_call
from .string import quote_str


@log_func_call
def nolog_mkdir_chgrp(p: Path, group: str, mode: int, log: Logger = None):
    log = log or getLogger(__name__)
    log.log(DEBUGLOW, 'in mkdir_chgrp')
    if p:
        p.mkdir(exist_ok=True, parents=True, mode=mode)
        if group:
            chown(p, group=group)


@log_func_call
def nolog_chmod_chgrp(p: Path, group: str, mode: int, log: Logger = None):
    log = log or getLogger(__name__)
    log.log(DEBUGLOW, 'in chmod_chgrp')
    if p:
        p.chmod(mode=mode)
        if group:
            chown(p, group=group)


@log_func_call
def nolog_file_copy_chmod_chgrp(src: Path, dest: Path, group: str, mode: int,
                                log: Logger = None):
    log = log or getLogger(__name__)
    log.log(DEBUGLOW, 'in copy_chmod_chgrp')
    copy2(src, dest)  # preserves file stat metadata (like mtime, etc.)
    nolog_chmod_chgrp(dest, group, mode, log)


@log_func_call
def nolog_import_python_file(pyfile: Path, as_name: str = None,
                             log: Logger = None) -> ModuleType:
    log = log or getLogger(__name__)
    log.debug('in import_python_file')
    as_name = as_name or pyfile.stem
    spec = spec_from_file_location(as_name, str(pyfile))
    mod = module_from_spec(spec)
    sys.modules[as_name] = mod
    spec.loader.exec_module(mod)
    return mod


@log_func_call
def nolog_add_path_to_syspath(p: Path | str, log: Logger = None):
    log = log or getLogger(__name__)
    log.debug(f'attempt to add {p} to sys.path')
    ppath = Path(p).resolve()
    pstr = str(p)
    log.debug(f'(before) sys.path={sys.path}')
    for x in sys.path:
        if Path(x).resolve() == ppath:
            log.debug('directory already in sys.path, taking no action')
            return

    sys.path.insert(0, pstr)
    log.debug(f'updated sys.path to include {p}')
    log.debug(f'(after) sys.path={sys.path}')


@log_func_call
def nolog_build_cmd_arg_dict(value: list[str] | dict | str = None):
    value = value or dict()
    args = dict()
    if isinstance(value, str):
        args = shsplit(value)

    if isinstance(value, list):
        lastkey = None
        for x in value:
            if x[0] == '-':
                if lastkey:
                    args[lastkey] = True

                lastkey = x[1:]

            elif lastkey:
                if lastkey in args:
                    orig = args[lastkey]
                    if not isinstance(orig, list):
                        orig = [orig]

                    x = orig + [x]
                args[lastkey] = x
                lastkey = None

            else:
                ValueError('multiple values with no command or parse error')

        if lastkey:
            args[lastkey] = True

    else:
        args = value

    return args


@log_func_call
def _add_arg_to_list(args: list, k: str, v: str,
                     quotekeys: list[str] | tuple[str] = ()):
    args.append(f'-{k}')
    if v is not True:
        if k in quotekeys:
            v = quote_str(v)

        args.append(str(v))


@log_func_call
def nolog_build_cmd_arg_list(value: list[str] | dict | str = None,
                             quotekeys: list[str] | tuple[str] = ()):
    value = value or list()
    args = list()
    if isinstance(value, dict):
        for k, v in value.items():
            if v is False:
                continue

            v = v if isinstance(v, list) else [v]
            for x in v:
                _add_arg_to_list(args, k, x, quotekeys)

    elif isinstance(value, str):
        args = shsplit(value)

    else:
        args = value

    return args
