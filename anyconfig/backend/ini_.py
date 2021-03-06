#
# Copyright (C) 2011 - 2013 Satoru SATOH <ssato @ redhat.com>
# License: MIT
#
import anyconfig.backend.base as Base
import anyconfig.parser as P

import logging
import os.path

try:
    import ConfigParser as configparser
except ImportError:
    import configparser  # python > 3.0

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


SUPPORTED = True  # It should be available w/ python dist always.

_SEP = ','


# FIXME: Ugly
def _parse(v, sep=_SEP):
    """
    :param v: A string represents some value to parse
    :param sep: separator between values

    >>> _parse(r'"foo string"')
    'foo string'
    >>> _parse("a, b, c")
    ['a', 'b', 'c']
    >>> _parse("aaa")
    'aaa'
    """
    if (v.startswith('"') and v.endswith('"')) or \
            (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    elif sep in v:
        return [P.parse(x) for x in P.parse_list(v)]
    else:
        return P.parse(v)


def _to_s(v, sep=_SEP):
    if isinstance(v, list):
        return ", ".join(x for x in v)
    else:
        return str(v)


def load_impl(config_fp, container, sep=_SEP):
    """
    :param config_fp: File or file-like object provides ini-style conf
    :param container: Object container to hold parsed objects

    :return: Dict or dict-like object represents config values
    """
    config = container()

    try:
        parser = configparser.SafeConfigParser()
        parser.readfp(config_fp)

        if parser.defaults():
            config["DEFAULT"] = container()

            for k, v in parser.defaults().iteritems():
                config["DEFAULT"][k] = _parse(v, sep)

        for s in parser.sections():
            config[s] = container()

            for k, v in parser.items(s):
                config[s][k] = _parse(v, sep)

    except Exception, e:
        logging.warn(e)

    return config


def mk_lines_g(data):
    has_default = "DEFAULT" in data

    def is_inherited_from_default(k, v):
        return has_default and data["DEFAULT"].get(k, None) == v

    for sect, params in data.iteritems():
        yield "[%s]\n" % sect

        for k, v in params.iteritems():
            if sect != "DEFAULT" and is_inherited_from_default(k, v):
                continue

            yield "%s = %s\n" % (k, _to_s(v))

        yield "\n"  # put an empty line just after each sections.


class IniConfigParser(Base.ConfigParser):
    _type = "ini"
    _extensions = ["ini"]

    @classmethod
    def loads(cls, config_content, sep=_SEP, **kwargs):
        config_fp = StringIO.StringIO(config_content)
        return load_impl(config_fp, cls.container(), sep)

    @classmethod
    def load(cls, config_path, sep=_SEP, **kwargs):
        config = cls.container()()

        if not os.path.exists(config_path):
            logging.warn("Not exist: " + config_path)
            return config

        logging.info("Loading config: " + config_path)
        return load_impl(open(config_path), cls.container(), sep)

    @classmethod
    def dumps(cls, data, *args, **kwargs):
        config_fp = StringIO.StringIO()
        for l in mk_lines_g(data):
            config_fp.write(l)

        return config_fp.getvalue()

    @classmethod
    def dump(cls, data, config_path, *args, **kwargs):
        with open(config_path, 'w') as config_fp:
            for l in mk_lines_g(data):
                config_fp.write(l)

# vim:sw=4:ts=4:et:
