#!/usr/bin/env python

import os
import re
import xml.etree.ElementTree as ET
from libs import utils
from optparse import OptionParser

ID_RE = re.compile(r'^[0-9a-f]{40}$')

parser = OptionParser(description="Get common project")

parser.add_option('-v', '--verbose', dest="verbose", action="store_true",
                 default=False, help="print pass project")

parser.add_option('-c', '--common', dest="common", action="store_true",
                 default=False, help="print common project")
parser.add_option('-d', '--diff', dest="diff", action="store_true",
                 default=False, help="print differential project")


def getManifestInfo(project, default, manifestFile=None):
    utils.change_parent_dir(".repo")

    if manifestFile == None:
        manifestFile = '.repo/manifest.xml'

    if not os.path.exists(manifestFile):
        utils.print_err("fatal : No such default.xml file", exit_code=-1)

    srcTree = ET.ElementTree()
    srcRoot = srcTree.parse(manifestFile)

    for node in srcRoot:
        if node.tag == "default":
            if len(default) == 0:
                default.update(node.attrib)
            else:
                utils.print_err(">>fatal: default value is not set twice", exit_code=-1)
        elif node.tag == 'project':
            project.append(node.attrib)
        elif node.tag == 'include':
            includedManifestFile = ".repo/manifests/"+node.attrib['name'].strip()
            if os.path.exists(includedManifestFile):
                getManifestInfo(project, default, includedManifestFile)
        else:
            continue


def main(options, args):
    utils.Verbose = options.verbose
    common = []
    diff = []
    projects = []
    default = {}

    # if specific manifest file is in args, check args and parsing manifest file
    if len(args) == 1:
        if os.path.exists(args[0]):
            getManifestInfo(projects, default, manifestFile=args[0])
        else:
            utils.print_err("fatal : manifest file is not exist", exit_code=-1)
    elif len(args) == 0:
            getManifestInfo(projects, default)
    else:
        utils.print_err("fatal : argument's length is only 1", exit_code=-1)

    for prj in projects:
        if 'device/lge' in prj['name'] or 'vendor/lge' in prj['name'] or 'LG_apps' in prj['name']:
            utils.print_verbose("pass : " + prj['name'])
            continue
        if prj.has_key('revision'):
            if ID_RE.match(prj["revision"]):
                if prj.has_key('upstream'):
                    if prj['upstream'] != default['revision']:
                        diff.append(prj)
                    else:
                        common.append(prj)

            else:
                if prj['revision'] == default['revision']:
                    common.append(prj)
                else:
                    diff.append(prj)

        else:
            common.append(prj)

    if options.common and len(common) !=0 :
        print "\n".join([ prj['name'] for prj in common ])
    elif options.diff and len(diff) != 0:
        print "\n".join([ prj['name'] for prj in diff ])
    else:
        utils.print_err("fatal: please choose -c or -d options", exit=-1)


if __name__ == "__main__":
    option, args = parser.parse_args()
    main(option,args)
