#!/usr/bin/env python2
import sys, os, argparse
import config

usrPass = config.CONFIG_PATHS['usrPass']

def main(usrPass, url, input):
        curl_command = """curl --ntlm -u "{usrPass}" -T {input} "{url}" -k"""
        print(curl_command.format(usrPass=usrPass,input=input,url=url))
        os.system(curl_command.format(usrPass=usrPass,input=input,url=url))

# Parameters
if __name__ == "__main__":
        parser= argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('url',help='Sharepoint url to upload to')
        parser.add_argument('input',help='Spreadsheet to upload to Sharepoint')
        args = parser.parse_args()

main(usrPass,args.url,args.input)
