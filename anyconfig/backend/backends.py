#
# Copyright (C) 2011, 2012 Satoru SATOH <ssato @ redhat.com>
# License: MIT
#
import anyconfig.backend.base as Base
import anyconfig.backend.ini_ as BINI
import anyconfig.backend.json_ as BJSON
import anyconfig.backend.xml_ as BXML
import anyconfig.backend.yaml_ as BYAML
import anyconfig.backend.properties_ as BPROP

_CPs = [
    BINI.IniConfigParser,
    BJSON.JsonConfigParser,
]

if BYAML.SUPPORTED:
    _CPs.append(BYAML.YamlConfigParser)

if BXML.SUPPORTED:
    _CPs.append(BXML.XmlConfigParser)

if BPROP.SUPPORTED:
    _CPs.append(BPROP.PropertiesParser)


def find_by_file(config_file, cps=_CPs):
    """
    Find config parser by file's extension.

    :param config_file: Config file path
    """
    for cp in cps:
        if cp.supports(config_file):
            return cp

    return None


def find_by_type(cptype, cps=_CPs):
    """
    Find config parser by file's extension.

    :param cptype: Config file's type
    """
    for cp in cps:
        if cp.type() == cptype:
            return cp

    return None


def list_types(cps=_CPs):
    """List available config types."""
    return [cp.type() for cp in cps]

# vim:sw=4:ts=4:et:
