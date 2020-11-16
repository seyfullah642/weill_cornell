#!/usr/bin/env python2.7
#####
import sys
import json
import copy
from os import path

import xlrd, datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import BaseDocTemplate, Frame, Spacer, Table, TableStyle, Paragraph, PageTemplate, PageBreak, Image

from static import static_text

def create_reports(infile,MSfile,outdir):
    
    data = read_input_file(infile)
    
    sampleName = path.basename(infile)
    sampleName = sampleName.split(".")
    sampleName = sampleName[0].split("_")
        
    msData = read_MSfile(MSfile, sampleName[0])
    
    for sample, sample_data in data.iteritems():
        if sample == '':
            pass
        else:
            Report(sample, sample_data, msData, outdir)

    print ('Reports written successfully.')

def read_input_file(infile):
    print ('Reading reporting spreadsheet {}...'.format(infile))

    workbook = xlrd.open_workbook(infile)

    data = {}
    sheet_names = workbook.sheet_names()

    for sheet_name in sheet_names:
        worksheet = workbook.sheet_by_name(sheet_name)

        headers = []
        for ncol in xrange(0, worksheet.ncols):
            headers.append(worksheet.cell_value(0, ncol))

        for nrow in xrange(1, worksheet.nrows):
            row = {}
            for ncol, header in enumerate(headers):
                row[header] = worksheet.cell_value(nrow, ncol)

            sample_name = row['Sample ID']
            if data.get(sample_name) is None:
                data[sample_name] = copy.copy(row)
            if data[sample_name].get(sheet_name) is None:
                data[sample_name][sheet_name] = [[], [], [], []]
            #print(row)
            tier = row['Tier']
            #print(tier)
            if tier == '':
                data[sample_name][sheet_name][3].append(row)
            else:
                data[sample_name][sheet_name][int(tier)-1].append(row)
    #print(data)
    return data

def read_MSfile(MSfile, sampleName):
    #MSfile = path.basename(MSfile)
    print(MSfile, sampleName)
    
    msData = []

    workbook = xlrd.open_workbook(MSfile)
    patientDemo = workbook.sheet_by_index(1)
    masterReg = workbook.sheet_by_index(0)

    #print(patientDemo)
    for row, line in enumerate(patientDemo.col_values(0)):
        #print(line)
        if line == sampleName:
            mrn = patientDemo.cell_value(rowx=row,colx=4)
            msData.append(mrn)
            try:
                date = xlrd.xldate.xldate_as_tuple(patientDemo.cell_value(rowx=row,colx=5),workbook.datemode)
                dateOfBirth = "{}/{}/{}".format(date[1],date[2],date[0])
                msData.append(dateOfBirth)
            except ValueError:
                print("Invalid date of birth, exiting report generation...")
                sys.exit(1)
            #date = datetime.datetime(date)
            #print(date)
            sex = patientDemo.cell_value(rowx=row,colx=6)
            msData.append(sex)
            pn = patientDemo.cell_value(rowx=row,colx=3)
            msData.append(pn)
    
    for row, line in enumerate(masterReg.col_values(0)):
        if line == sampleName:
            try:
                date = xlrd.xldate.xldate_as_tuple(masterReg.cell_value(rowx=row,colx=8),workbook.datemode)
                sampleCollected = "{}/{}/{}".format(date[1],date[2],date[0])
                msData.append(sampleCollected)
            except ValueError:
                print("Invalid date for sample collected, exiting report generation...")
                sys.exit(1)
            try:
                date = xlrd.xldate.xldate_as_tuple(masterReg.cell_value(rowx=row,colx=7),workbook.datemode)
                sampleReceived = "{}/{}/{}".format(date[1],date[2],date[0])
                msData.append(sampleReceived)
            except ValueError:
                print("Invalid date for sample received, exiting report generation...")
                sys.exit(1)
            
            sampleType = masterReg.cell_value(rowx=row,colx=9)
            msData.append(sampleType)
            orderPhys = masterReg.cell_value(rowx=row,colx=4)
            msData.append(orderPhys)
            tissueTested = masterReg.cell_value(rowx=row,colx=13)
            msData.append(tissueTested)
            
            try:
                date = xlrd.xldate.xldate_as_tuple(masterReg.cell_value(rowx=row,colx=23),workbook.datemode)
                dateOfService = "{}/{}/{}".format(date[1],date[2],date[0])
                msData.append(dateOfService)
            except ValueError:
                print("Invalid date for date of service, exiting report generation...")
                sys.exit(1)
            
            gxn = masterReg.cell_value(rowx=row,colx=22)
            msData.append(gxn)
            spn = masterReg.cell_value(rowx=row,colx=1)
            msData.append(spn)
            tt = masterReg.cell_value(rowx=row,colx=11)
            msData.append(tt)
            ps = masterReg.cell_value(rowx=row,colx=12)
            msData.append(ps)
            nc = masterReg.cell_value(rowx=row,colx=14)
            msData.append(nc)

    return msData

class Report():

    def __init__(self, sample_name, sample_data, msData, outdir):
        self.sample_name = sample_name
        self.sample_data = sample_data
        self.msData = msData
        self.outfile = path.join(outdir, 
                                 '{}.pdf'.format(sample_name.strip()))
        #print("In report class")
        #print(self.msData)
        self.__set_styles()
        self.__set_tables()
        self.__set_heading_table()
        self.generate_report()

        #print(sample_name)

    def __set_styles(self):
        self.styles = getSampleStyleSheet()
        self.standard_spacer = Spacer(1, 0.2*inch)
        self.smaller_spacer = Spacer(1, 0.15*inch)
        self.table_style = [
            ('BACKGROUND', 
                (0,0), (-1,0), colors.HexColor('#99CCFF')),
            ('LINEBELOW', 
                (0,0), (-1,0), 0.5, colors.black),
            ('BOX', 
                (0,0), (-1,-1), 0.5, colors.black), 
            ('VALIGN', 
                (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW', 
                (0,'splitlast'), (-1,'splitlast'), 0.5, colors.black),
            ('ROWBACKGROUNDS',
                (0,1), (-1,-1), 
                (colors.HexColor('#FFFFFF'), colors.HexColor('#D6EBFF')))
        ]
        self.comment_style = ParagraphStyle('Regular indents', firstLineIndent=25, spaceAfter=10)
        self.text_block_style = ParagraphStyle('Fine Print', fontSize=9)
        self.tier_text_style = ParagraphStyle('Hanging indents', fontSize=9, leftIndent=35, firstLineIndent=-35)
        self.centered_text = ParagraphStyle('Centered', alignment='TA_CENTER')
        self.reference_text_style = ParagraphStyle('Regular indents', fontSize=10, leftIndent=35, firstLineIndent=-20)

    def __set_tables(self):

        self.available_table_names = []
        self.all_tables = {}
        self.interpretations = {}
        self.static_text = static_text()

        self.__format_variants()

    def __set_heading_table(self):
        self.heading_table = [
            ['Patient Name:', self.msData[3]],
            ['DOB:', self.msData[1]],
            ['Sex:', self.msData[2]],
            ['MRN:', self.msData[0]],
            ['Tumor Type:', self.msData[12]],
            ['Primary site:', self.msData[13]],
            ['Tissue Tested:' , self.msData[8]]
        ]

        self.heading_table_2 = [
            ['Ordering Physician:', self.msData[7]],
            ['Neoplastic content:', "{}%".format(int(self.msData[14]))],
            ['Specimen ID:', self.msData[11]],
            ['Sample Type:', self.msData[6]],
            ['Sample Collected:', self.msData[4]],
            ['Sample Received:', self.msData[5]],
            ['Date of Service:', self.msData[9]]
        ]

    def __variant_table_mutation_format(self, row):
        if row.get('Mutation') is not None:
            return Paragraph(row['Mutation'], self.styles['Normal'])
        else:
            return Paragraph(row['Genes'], self.styles['Normal'])

    def __table_headers(self, key):
        if key == 'Variants':
            return [
                {
                    'header': 'Variant',
                    'field': self.__variant_table_mutation_format,
                    'width': 200
                },
                { 
                    'header': 'Type',
                    'field': (lambda row: row['Type']),
                    'width': 155
                },
                #{
                #    'header': 'Cosmic ID',
                #    'field': (lambda row: Paragraph(row['COSMIC ID'], self.styles['Normal'])
                #                          if row.get('COSMIC ID') is not None
                #                          else 'N/A'),
                #    'width': 90
                #},
                {
                    'header': 'VAF',
                    'field': (lambda row: "{0:.1f}%".format(float(row['Frequency'].replace("%","")))
                                          if row.get('Frequency') is not None 
                                          else 'N/A'),
                    'width': 50
                },
                {
                    'header': 'CN',
                    'field': (lambda row: row['Copy Number'] 
                                        if row.get('Copy Number') is not None 
                                        else 'N/A'),
                    'width': 50
                }
            ]

        if key == 'CNVs':
            return [
                {
                    'header': 'Genes',
                    'field': (lambda row: row['Genes']),
                    'width': 70
                },
                {
                    'header': 'Cytoband',
                    'field': (lambda row: row['Cytoband'].split('(')[0]),
                    'width': 75
                },
                {
                    'header': 'CNV Type',
                    'field': (lambda row: row['CNV Type']),
                    'width': 75
                },
                {
                    'header': 'Copy Number',
                    'field': (lambda row: row['Copy Number']),
                    'width': 75
                },
                {
                    'header': 'CNV Confidence',
                    'field': (lambda row: row['CNV Confidence']),
                    'width': 125
                },
                {
                    'header': 'Gene Class',
                    'field': (lambda row: row['Oncomine Gene Class']),
                    'width': 125
                }
            ]

    def __format_variants(self):
        variants = self.sample_data.get('Variants')
        fusions = self.sample_data.get('Fusions')
        cnvs = self.sample_data.get('CNVs')

        headers = self.__table_headers('Variants')

        self.interpretations['Variants'] = []

        tables = []
        all_fusions = []

        if fusions is not None:
            for tier in fusions:
                for fusion in tier:
                    all_fusions.append(fusion)

        for tier in xrange(0, 3):
            mutations = []
            if variants is not None:
                mutations += variants[tier]
            if cnvs is not None:
                mutations += cnvs[tier]
            if fusions is not None:
                mutations += fusions[tier]
            #if tier == 0:
            #    mutations += all_fusions

            tab = self.__format_table(mutations, 
                                      self.__table_headers('Variants'), 
                                      self.interpretations['Variants'])
            tables.append(tab)
        #print(mutations)
        #print(self.all_tables['Variants'])
        self.all_tables['Variants'] = tables
        #print(self.all_tables['Variants'])

    def __format_cnvs(self):
        cnvs = self.sample_data.get('CNVs')
        headers = self.__table_headers('CNVs')

        self.interpretations['CNVs'] = []

        all_cnvs = []
        if cnvs is not None:
            for tier in cnvs:
                for cnv in tier:
                    all_cnvs.append(cnv)

        table = self.__format_table(all_cnvs,
                                    self.__table_headers('CNVs'),
                                    self.interpretations['CNVs'])

        self.all_tables['CNVs'] = table

    def __format_table(self, mutations, headers, interpretation_holder):
        table_headers = [ x['header'] for x in headers ]
        colWidths = tuple([ x['width'] for x in headers ])

        table = []
        table.append(table_headers)

        if mutations:
            for mutation in mutations:
                if mutation['Exclude'] == "exclude":
                    continue
                #else:
                #    print(mutation)
                #    print("\n")
                row = []
                
                for header in headers:
                    row.append(header['field'](mutation))
                if mutation['Interpretation'] != '':
                    interpretation_holder.append({
                        'interp': mutation['Interpretation'],
                        'citations': mutation['Citations'].split('|')
                    })
                table.append(row)
                #print(row)
        
        #print(table)
        #else:
        #    row = ['No mutations were found.'] + ['']*(len(headers)-1)
        #    table.append(row)

        reportlab_table = Table(table, colWidths=colWidths)
        reportlab_table.setStyle(self.table_style)

        return reportlab_table

    def __resize(self, img, height):
        iw, ih = img.getSize()
        aspect = iw / float(ih)
        width = height*aspect
        return (width, height)

    def __page_header(self, canvas, doc):
        canvas.saveState()
        high=10.3

        #logo = ImageReader('{}/logo.jpg'.format(path.dirname(path.realpath(__file__))))
        logo = ImageReader('{}/wcm_nyp_ClinicalGenomicsLab_Letterhead_CB_Opt01r.png'.format(path.dirname(path.realpath(__file__))))
        logo_width, logo_height = self.__resize(logo, inch*0.75)
        canvas.drawImage(logo, inch*0.5, inch*10.1, width=logo_width, 
                                                     height=logo_height, 
                                                     mask='auto')
        canvas.setFont("Helvetica",14)
        canvas.drawString(inch*2.75, inch*(high-.4), 'Oncomine Comprehensive Report')
        canvas.setFont("Helvetica",8)
        canvas.drawString(inch*6.175, inch*10.6, 'Wayne Tam, MD, PhD - Director')
        canvas.drawString(inch*6.175, inch*10.5, 'Lab of Oncology-Molecular Detection')
        canvas.drawString(inch*6.175, inch*10.4, 'Weill Cornell Medicine')
        canvas.drawString(inch*6.175, inch*10.3, '1300 York Avenue K502, LC-904')
        canvas.drawString(inch*6.175, inch*10.2, 'New York, NY 10065')
        canvas.drawString(inch*6.175, inch*10.1, 'T:646.962.3816 F:212.746.8362')

        canvas.setFillColorRGB(255,0,0)
        #canvas.drawString(inch*3, inch*high, 'PRELIMINARY - FOR INVESTIGATIONAL USE ONLY')
        canvas.setFillColorRGB(0,0,0)

        canvas.drawString(inch*7.5, inch*(0.4), 'Page {}'.format(doc.page))
        canvas.line(inch/2, inch*(high-0.5), inch*8, inch*(high-0.5))
        canvas.drawString(inch/2, inch*(high-0.4), "GX{}".format(self.msData[10]))
        
        canvas.restoreState()

    def generate_report(self):
        #print(self.outfile)
        print ('Writing report PDF {}...'.format(self.outfile))

        report = BaseDocTemplate(self.outfile,
                                 pagesize=letter,
                                 leftMargin=inch/2,
                                 rightMargin=inch/2,
                                 topMargin=inch,
                                 bottomMargin=inch)
        frame = Frame(report.leftMargin, 
                      report.bottomMargin, 
                      report.width, 
                      report.height - inch*0.3)
        report.addPageTemplates([PageTemplate(id='normal', 
                                              frames=frame, 
                                              onPage=self.__page_header
                                              )])

        el = []

        #el.append(Spacer(1, 0.2*inch))

        ht = Table(self.heading_table, hAlign='LEFT')
        ht.setStyle(TableStyle([('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold')]))
        #el.append(ht)

        ht2 = Table(self.heading_table_2, hAlign='RIGHT')
        ht2.setStyle(TableStyle([('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold')]))

        ht_w = 3.75 * inch
        ht2_w = 4 * inch

        data = [[ht, ht2]]
        data_table = Table(data, colWidths=[ht_w, ht2_w])
        el.append(data_table)

        el.append(Spacer(1, 0.2*inch))

        # Variants
        for tier in xrange(0,3):
            el.append(Paragraph('Tier {} Variants'.format(tier+1), 
                                self.styles['Heading3']))
            el.append(self.all_tables['Variants'][tier])
            #print(self.all_tables['Variants'][tier])

        el.append(Paragraph('VAF = Variant Allele Frequency, CN = Copy Number, N/A = Not Applicable', self.styles['Heading6']))
        #el.append(Paragraph('CN = Copy Number', self.styles['Heading6']))
        #el.append(Paragraph('N/A = Not Applicable', self.styles['Heading6']))

        #el.append(Spacer(1, 0.2*inch))

        non_dups_interp = []

        el.append(Paragraph('Comments', self.styles['Heading5']))
        if self.interpretations['Variants']:
            for interp in self.interpretations['Variants']:
                if interp['interp'] != "This gene is a known cancer gene.":
                    non_dups_interp.append(interp['interp'])
                    #el.append(Paragraph(interp['interp'], self.comment_style))

            non_dups_interps = list(set(non_dups_interp))

            for i in non_dups_interps:
                el.append(Paragraph(i, self.comment_style))

        #el.append(self.standard_spacer)

        for text in self.static_text['tiers']:
            el.append(Paragraph(text, self.tier_text_style)) #tier_text_style

        el.append(self.standard_spacer)

        el.append(Paragraph(self.static_text['method'], self.text_block_style))
        el.append(Spacer(1, 0.2*inch))

        el.append(Paragraph(self.static_text['technical assessment'], self.text_block_style))
        el.append(Spacer(1, 0.2*inch))

        el.append(Paragraph(self.static_text['disclaimer'], self.text_block_style))

        el.append(self.standard_spacer)

        hotspot_1 = [(Paragraph(self.static_text['hotspot_1'], self.text_block_style))]
        hotspot_2 = [(Paragraph(self.static_text['hotspot_2'], self.text_block_style))]
        hotspot_3 = [(Paragraph(self.static_text['hotspot_3'], self.text_block_style))]

        cds = [(Paragraph(self.static_text['cds'], self.text_block_style))]

        cnv_1 = [(Paragraph(self.static_text['cnv_1'], self.text_block_style))]
        cnv_2 = [(Paragraph(self.static_text['cnv_2'], self.text_block_style))]

        fusion = [(Paragraph(self.static_text['fusion'], self.text_block_style))]
        
        gene_list = [[hotspot_1, hotspot_2, hotspot_3, cds, cnv_1, cnv_2, fusion]]

        gene_list_table = Table(gene_list)
        el.append(gene_list_table)

        citnum = 0
        el.append(Paragraph('References', self.styles['Heading5']))
        non_dups_citation = []
        
        for vartype, interps in self.interpretations.iteritems():
            for interp in interps:
                for i in range(0,len(interp['citations'])):
                    non_dups_citation.append(interp['citations'][i].encode('utf-8'))
        
        non_dup_cites = list(set(non_dups_citation))

        for cites in non_dup_cites:
            citnum += 1
            el.append(Paragraph('{}) {}'.format(citnum, cites), self.reference_text_style))

        if citnum == 0:
            el.append(Paragraph('No citations.', self.styles['Normal']))

        report.build(el)

if __name__ == '__main__':
    infile = sys.argv[1]
    MSfile = sys.argv[2]
    outdir = sys.argv[3]

    create_reports(infile,MSfile,outdir)
