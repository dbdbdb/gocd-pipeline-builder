#!/usr/bin/python -tt
# coding:utf-8
import sys
import getpass
import argparse
from go_proxy import GoProxy
from model import JsonSettings, YamlSettings


def list2dict(list_of_pairs):
    return dict(tuple(pair.split('=', 1) for pair in list_of_pairs or []))


def add_secrets_to_config(config, password_parameters):
    for password_parameter in password_parameters or []:
        config[password_parameter] = getpass.getpass(password_parameter + ': ')


def main(args=sys.argv):
    argparser = argparse.ArgumentParser(
        description="Add pipeline to Go CD server."
    )
    main_action_group = argparser.add_mutually_exclusive_group()
    main_action_group.add_argument(
        "-j", "--json-settings",
        type=argparse.FileType('r'),
        help="Read json file with settings for GoCD pipeline."
    )
    main_action_group.add_argument(
        "-y", "--yaml-settings",
        type=argparse.FileType('r'),
        help="Read yaml files with parameters for GoCD pipeline."
    )
    argparser.add_argument(
        "-D", "--define",
        action="append",
        help="Define setting parameter on command line."
    )
    argparser.add_argument(
        "-c", "--config",
        type=argparse.FileType('r'),
        help="Yaml file with configuration."
    )
    argparser.add_argument(
        "-C", "--config-param",
        action="append",
        help="Define config parameter on command line."
    )
    argparser.add_argument(
        "-P", "--password-prompt",
        action="append",
        help="Prompt for config parameter without echo."
    )
    argparser.add_argument(
        "--set-test-config",
        type=argparse.FileType('r'),
        help="Set some sections in config first. (For test setup.)"
    )
    argparser.add_argument(
        "--dump-test-config",
        type=argparse.FileType('w'),
        help="Copy of some sections of new GoCD configuration XML file."
    )
    argparser.add_argument(
        "-d", "--dump",
        type=argparse.FileType('w'),
        help="Copy of new GoCD configuration XML file."
    )
    argparser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Write status of created pipeline."
    )

    pargs = argparser.parse_args(args[1:])

    extra_config = list2dict(pargs.config_param)
    add_secrets_to_config(extra_config, pargs.password_prompt)
    go = GoProxy(pargs.config, pargs.verbose, extra_config)

    if pargs.set_test_config is not None:
        go.tree.set_test_settings_xml(pargs.set_test_config)
        go.upload_config()

    if pargs.json_settings is not None:
        JsonSettings(pargs.json_settings, list2dict(pargs.define)
                     ).server_operations(go)

    if pargs.yaml_settings is not None:
        YamlSettings(pargs.yaml_settings, list2dict(pargs.define)
                     ).server_operations(go)

    if pargs.dump is not None:
        go.init()
        envelope = '<?xml version="1.0" encoding="utf-8"?>\n%s'
        pargs.dump.write(envelope % go.cruise_xml)

    if pargs.dump_test_config is not None:
        go.init()
        envelope = '<?xml version="1.0" encoding="utf-8"?>\n%s'
        pargs.dump_test_config.write(envelope % go.cruise_xml_subset)


if __name__ == '__main__':
    main()
