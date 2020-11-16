"""
VCF.py

This module is for parsing a VCF's fields into a dict. It is not platform
specific. It can also handle parsing out multiple VCFs that are contained
within a compressed archive.
"""

import gzip
import zipfile
import re
import sys
import json
from csv import reader
from collections import namedtuple
from StringIO import StringIO
from os.path import basename

class VCFError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

def process_zip(infile):
    vcf_objects = []
    ziphandle = zipfile.ZipFile(infile, 'r')
    non_hidden = [f for f in ziphandle.namelist() if basename(f) != '' and basename(f)[0] != "."]
    for filename in non_hidden:
        vcf_contents = StringIO(ziphandle.read(filename))
        try:
            vcf_object = read_vcf(vcf_contents, filename)
            vcf_objects.append(vcf_object)
            print "File {0} processed.".format(filename)
        except VCFError:
            continue
        #    print "{} was not a valid VCF.".format(filename)
    ziphandle.close()
    if not vcf_objects:
        raise VCFError('There were no valid VCFs inside the ZIP.')
    return vcf_objects

def read_vcf(fileobj, filename):
    fileobj = _retrieve_content_stream(fileobj)
    metadata, headers, records = _read_contents(fileobj)
    _check_info(metadata, headers)
    field_types = _get_field_types(metadata)
    records = _process_records(headers, records, field_types)
    VCF = namedtuple('VCF', 'filename, field_types, headers, records')
    return VCF(filename, field_types, headers, records)

def _retrieve_content_stream(fileobj):
    try:
        g = gzip.GzipFile(fileobj=fileobj)
        return StringIO(g.read())
    except IOError:
        return StringIO(fileobj.read())
    finally:
        g.close()
        fileobj.close()

def _check_info(metadata, headers):
    if "fileformat=VCF" not in metadata[0]:
        raise VCFError('This file does not have the correct file format '
                       'information.')
    if not headers:
        raise VCFError('This file does not have header line.')

def _read_contents(fileobj):
    metadata, headers, records = [], [], []
    metadata.append(fileobj.readline()) # For some reason the ## on the first line falls off
    for line in fileobj:
        if '##' in line:
            metadata.append(line.strip())
        elif '#' in line:
            headers = line.lstrip('#').strip().split("\t")
        else:
            records.append(line.strip().split("\t"))
    fileobj.close()
    return (metadata, headers, records)

def _get_field_types(metadata):
    field_types = {}
    for line in metadata:
        if '##INFO' in line or '##FORMAT' in line:
            keys = re.match(".*<(.*),Description.*>.*", line).group(1).split(',')
            fieldinfo = {}

            for key in keys:
                try:
                    k, v = key.split('=')
                    fieldinfo[k] = v
                    field_types[fieldinfo['ID']] = fieldinfo
                except:
                    print Exception
    return field_types

def _process_records(headers, records, field_types):
    record_dicts = []
    for record in records:
        r = {}
        format_fields = []
        for field, header in zip(record, headers):
            if header in ['CHROM', 'POS', 'REF', 'QUAL', 'FILTER']:
                r[header] = field
            elif header == 'ID':
                r['ID'] = field.split(';')
            elif header == 'ALT':
                r['ALT'] = field.split(',')
            elif header == 'INFO':
                r['INFO'] = _process_info_subfields(field, field_types)
            elif header == 'FORMAT':
                r['GENO'] = field.split(':')
            else:
                r[header] = _process_geno_subfields(field, r['GENO'],
                                                    field_types)
        record_dicts.append(r)
    return record_dicts


def _process_info_subfields(info_field, field_types):
    # Called from process_records to split & assign the INFO fields
    info = {}
    for subfield in info_field.split(';'):
        key, eq, value = subfield.partition('=')
        if value == "":
            info[key] = True
        elif '{' in value:
            info[key] = json.loads(value.replace('\'', '"'))
        elif field_types[key]['Number'] == '1':
            info[key] = _assign_type(value, key, field_types)
        else:
            info[key] = _assign_type(value.split(','), key, field_types)
    return info

def _process_geno_subfields(genotype_field, format_fields, field_types):
    # Called from process_records to split & assign the FORMAT/Genotype fields
    geno_fields = genotype_field.split(':')
    geno_values = {}
    for formatf, geno in zip(format_fields, geno_fields):
        if field_types[formatf]['Number'] == '1':
            geno_values[formatf] = _assign_type(geno, formatf, field_types)
        else:
            geno_values[formatf] = _assign_type(geno.split(','), formatf,
                                                field_types)
    return geno_values

def _assign_type(values, key, field_types):
    field_type = field_types.get(key)
    if field_type['Type'] == 'Float':
        if isinstance(values, list):
            values = [float(v) for v in values if v != "."]
        else:
            values = float(values)
    elif field_type['Type'] == 'Integer':
        if isinstance(values, list):
            values = [int(v) for v in values if v != "."]
        else:
            try:
                values = int(values)
            except:
                values = None
    return values

if __name__ == '__main__':
    filename = sys.argv[1]
    with open(filename, 'r') as file:
        v = read_vcf(file, filename)
        print json.dumps(v.records)
