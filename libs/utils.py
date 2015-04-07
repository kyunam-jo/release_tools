#!/usr/bin/python
import subprocess
import os
import sys

def exec_cmd(cmd, shell=True, returnType=False ,loc=None):
    if returnType:
        stdin = subprocess.PIPE
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
    else:
        stdin=None
        stdout=None
        stderr=None
    p = subprocess.Popen(cmd,
                         cwd=loc,
                         shell=shell,
                         stdin=stdin,
                         stdout=stdout,
                         stderr=stderr,
                         executable='/bin/bash')
    return p.communicate()

def watch_parent_dir(name):
    cwd = os.getcwd()
    while True:
        loc = os.getcwd()
        print loc
        if loc == '/':
            os.chdir(cwd)
            return None
        else:
            if os.path.exists(name) and os.path.isdir(name):
                os.chdir(cwd)
                return loc
            else:
                os.chdir('..')

def change_parent_dir(name):
    local_path = watch_parent_dir(name)
    if local_path != None:
        os.chdir(local_path)
        return True
    else:
        return False


def find_all_file_in_dir(dir_name):
    all_files = []
    for root, dirs, files in os.walk(dir_name):
        if root != dir_name:
            try:
                dirs.index(".git")
                break
            except ValueError:
                pass
        if files:
            for f in files:
                if root[-1] == '/':
                    full_name = root + f
                else:
                    full_name = root + '/' + f

                if (not os.path.islink(full_name)) and full_name.find('.git') == -1:
                    all_files.append(full_name)
    return all_files


Verbose = False

def print_verbose(values):
    if Verbose == True:
        print >> sys.stderr, str(values)


def print_err(valuse, exit=None):
    print >> sys.stderr, str(valuse)
    if exit != None and isinstance(exit, int): sys.exit(exit)


if __name__ == "__main__":
    print "== this is module =="
