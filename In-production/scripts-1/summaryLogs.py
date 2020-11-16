#!/usr/bin/env python

import re
import sys

def main():

    data = sys.stdin.read().splitlines()

    if re.search(r'TsPluginActor finished.',data[len(data)-1]) or re.search(r'TsPluginActor/runPlugin succeeded.',data[len(data)-1]) \
           or re.search(r'AppRunnerActor finished.',data[len(data)-1]) or re.search(r'QcmoduleActor finished',data[len(data)-1]):
        print("Analysis complete")
    elif re.search(r'TsPluginActor cancelled because dependency failed.',data[len(data)-1]) or \
            re.search(r'AnnotatorActor cancelled because dependency failed.',data[len(data)-1]):
        print("Analysis failed")
    else:
        print("Analysis not complete")
    
if __name__ == '__main__':
  main()
