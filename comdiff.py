#!/usr/bin/env python

from optparse import OptionParser
import xml.etree.ElementTree as ET
import sys,os
import re

ID_RE = re.compile(r'^[0-9a-f]{40}$')


parser = OptionParser(description="Get common project")

parser.add_option('-v', '--verbose', dest="verbose", action="store_true",
                 default=False, help="print pass project")

parser.add_option('-c', '--common', dest="common", action="store_true",
                 default=False, help="print common project")
parser.add_option('-d', '--diff', dest="diff", action="store_true",
                 default=False, help="print differential project")

def changeRootDir():
    while True:
        loc = os.getcwd()
        if loc == '/':
            print 'error: repo is not installed.  Use "repo init" to install it here.'
            sys.exit(-1)
        else:
            if os.path.isdir('.repo'):
                return loc
            else:
                os.chdir('..')


def getManifestInfo(project, default, manifestFile=None):
    changeRootDir()

    if manifestFile == None:
        manifestFile = '.repo/manifest.xml'

    if not os.path.exists(manifestFile):
        print >> sys.stderr, "fatal : No such default.xml file"
        sys.exit(1)

    srcTree = ET.ElementTree()
    srcRoot = srcTree.parse(manifestFile)

    for node in srcRoot:
        if node.tag == "default":
            if len(default) == 0:
                default.update(node.attrib)
            else:
                print >> sys.stderr, ">>fatal: default value is not set twice"
                sys.exit(-1)
        elif node.tag == 'project':
            project.append(node.attrib)
        elif node.tag == 'include':
            includedManifestFile = ".repo/manifests/"+node.attrib['name'].strip()
            print includedManifestFile
            if os.path.exists(includedManifestFile):
                getManifestInfo(project, default, includedManifestFile)
        else:
            continue


def main(options, args):
    common = []
    diff = []
    projects = []
    default = {}

    # if specific manifest file is in args, check args and parsing manifest file
    if len(args) == 1:
        if os.path.exists(args[0]):
            getManifestInfo(projects, default, manifestFile=args[0])
        else:
            print >> sys.stderr, "fatal : manifest file is not exist"
            sys.exit(-1)
    elif len(args) == 0:
            projects, default = getManifestInfo()
    else:
        print >> sys.stderr, "fatal : argument's length is only 1"
        sys.exit(-1)

    for prj in projects:
        if prj['name'].find('device/lge') != -1 or prj['name'].find('vendor/lge') != -1 or prj['name'].find('LG_apps') != -1:
            if options.verbose:
                print >> sys.stderr, "pass : " + prj['name']
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

    if options.common :
        for prj in common:
            print prj['name']
    elif options.diff:
        for prj in diff:
            print prj['name']
    else:
        print >> sys.stderr, "fatal: please choose -c or -d options"
        sys.exit(-1)


if __name__ == "__main__":
    option, args = parser.parse_args()
    main(option,args)
