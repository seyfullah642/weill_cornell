#!/usr/bin/env python
import sys, os, argparse
import config

usrPass = config.CONFIG_PATHS['usrPass']

def main(usrPass, url, output):
        curl_command = """curl --ntlm -u "{usrPass}" -o {output} "{url}" -k"""
        print(curl_command.format(usrPass=usrPass,output=output,url=url))
        os.system(curl_command.format(usrPass=usrPass,output=output,url=url))

# Parameters
if __name__ == "__main__":
	parser= argparse.ArgumentParser(
	description=__doc__,
	formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('url',help='Sharepoint url to download file from')
	parser.add_argument('output',help='Local name to save file to')
	args = parser.parse_args()

main(usrPass,args.url,args.output)
