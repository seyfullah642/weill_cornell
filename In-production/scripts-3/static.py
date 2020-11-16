# -*- coding: utf-8 -*-
###
def static_text():
    return {
        'method': '<b>Method</b>: DNA and RNA were extracted from macrodissected, paraffin-embedded tumor of the patient using the Maxwell 16 instrument (Promega, Madison, WI) and RecoverAll Total Nucleic Acid Isolation Kit (Life Technologies, Waltham, MA), respectively. The extracted DNA and synthesized cDNA from the extracted RNA were amplified by the Oncomine Comprehensive Panel (OCP) and subjected to Next Generation Sequencing (NGS) using the Ion Torrent S5™(Life Technologies). The targeted gene panel interrogates 143 unique cancer genes including 73 oncogenes, 49 copy number alteration (CNA) genes, 26 tumor suppressor genes, and 23 fusion driver genes. OCP is designed to detect mutations/single nucleotide variants (SNVs), insertion/deletion (Indel), copy number variants (CNVs), and gene fusions. This test is validated for SNVs in the BRAF, EGFR, KRAS, NRAS, IDH1, and PIK3CA genes, indel in the EGFR gene, CNVs in the HER2 gene, and gene fusions in the ALK and ERG genes. The limit of detection for SNVs and indels is precise and reproducible at 5% with 400X coverage and 3% with 1000X coverage. The minimum number of reads required for fusion positivity is 1000. Genes with 5% CI estimate of ≥4 is considered to have copy number gains. The data obtained was analyzed with the Ion Reporter™ Software 5.6 including Coverage Analysis, Fusion Analysis, and Torrent Variant Annotator v2.3 plug-ins. DNA sequences used as references for this panel of genes can be found at http://ncbi.nlm.nih.gov/refseq/rsg. The mutation nomenclature is based on the recommendations from the Human Genome Variation Society http://www.hgvs.org/mutnomen.',
        
        'technical assessment': '<b>Technical Assessment</b>: This panel is designed to detect mutations in 99 genes, CNVs in 49 genes, and fusions in 23 genes. Out of 130 DNA-sequenced genes, 104 genes are not sequenced in their entirely. Mutations outside the 2530 interrogated amplicons will not be detected. Due to the technology employed by this NGS assay, accurate indel identification in homopolymeric region is not optimal. For 23 fusion genes, 148 isoforms using 154 primer pairs are targeted, but potential isoforms which are not covered by the primer pairs will not be detected.',
        
        'disclaimer': '<b>Disclaimer</b>: The Oncomine Comprehensive Test was developed and its performance characteristics was determined by the Clinical Genomics Laboratory, Englander Institute for Precision Medicine/Department of Pathology and Laboratory Medicine at Weill Cornell Medicine/New York-Presbyterian Hospital; and approved by the New York-State Department of Health (NYS-DOH). This method has not been cleared by the Food and Drug Administration (FDA). The FDA has determined that such clearance or approval is not necessary.\n\tVariants of uncertain origin (germline versus somatic origin) cannot be determined unequivocally in this test, such that germline alterations are not reported. If a possible pathogenic germline mutation (inherited) is suspected, then counselling by a board certified genetic counselor will be recommended in note.',

        'hotspot_1':'<b>HOTSPOT</b><br />ABL1<br />AKT1<br />ALK<br />AR<br />ARAF<br />BRAF<br />BTK<br />CBL<br />CDK4<br />CHEK2<br />CSF1R<br />CTNNB1<br />DDR2<br />DNMT3A<br />EGFR<br />ERBB2<br />ERBB3<br />ERBB4<br />ESR1<br />EZH2<br />FGFR1<br />FGFR2<br />FGFR3<br />FLT3<br />FOXL2<br />GATA2<br />',
        'hotspot_2':'GNA11<br />GNAQ<br />GNAS<br />HNF1A<br />HRAS<br />IDH1<br />IDH2<br />IFITM1<br />IFITM3<br />JAK1<br />JAK2<br />JAK3<br />KDR<br />KIT<br />KNSTRN<br />KRAS<br />MAGOH<br />MAP2K1<br />MAP2K2<br />MAPK1<br />MAX<br />MED12<br />MET<br />MLH1<br />MPL<br />MTOR',
        'hotspot_3':'MYD88<br />NFE2L2<br />NPM1<br />NRAS<br />PAX5<br />PDGFRA<br />PIK3CA<br />PPP2R1A<br />PTPN11<br />RAC1<br />RAF1<br />RET<br />RHEB<br />RHOA<br />SF3B1<br />SMO<br />SPOP<br />SRC<br />STAT3<br />U2AF1<br />XPO1<br />&nbsp;<br />&nbsp;<br />&nbsp;<br />&nbsp;<br />&nbsp;',

        'cds':'<b>FULL GENE</b><br />APC<br />ATM<br />BAP1<br />BRCA1<br />BRCA2<br />CDH1<br />CDKN2A<br />FBXW7<br />GATA3<br />MSH2<br />NF1<br />NF2<br />NOTCH1<br />PIK3R1<br />PTCH1<br />PTEN<br />RB1<br />SMAD4<br />SMARCB1<br />STK11<br />TET2<br />TP53<br />TSC1<br />TSC2<br />VHL<br />WT1',

        'cnv_1':'<b>CNV</b><br />ACVRL1<br />AKT1<br />APEX1<br />AR<br />ATP11B<br />BCL2L1<br />BCL9<br />BIRC2<br />BIRC3<br />CCND1<br />CCNE1<br />CD274<br />CD44<br />CDK4<br />CDK6<br />CSNK2A1<br />DCUN1D1<br />EGFR<br />ERBB2<br />FGFR1<br />FGFR2<br />FGFR3<br />FGFR4<br />FLT3<br />GAS6<br />IGF1R',
        'cnv_2':'IL6<br />KIT<br />KRAS<br />MCL1<br />MDM2<br />MDM4<br />MET<br />MYC<br />MYCL<br />MYCN<br />MYO18A<br />NKX2-1<br />NKX2-8<br />PDCD1LG2<br />PDGFRA<br />PIK3CA<br />PNP<br />PPARG<br />SMARCB1<br />SOX2<br />TERT<br />TIAF1<br />ZNF217<br />&nbsp;<br />&nbsp;<br />&nbsp;',

        'fusion':'<b>FUSION</b><br />ABL1<br />AKT3<br />ALK<br />AXL<br />BRAF<br />ERG<br />ETV1<br />ETV4<br />ETV5<br />EGFR<br />ERBB2<br />FGFR1<br />FGFR2<br />FGFR3<br />MET<br />NTRK1<br />NTRK2<br />NTRK3<br />PDGFRA<br />PPARG<br />RAF1<br />RET<br />ROS1<br />&nbsp;<br />&nbsp;<br />&nbsp;',

        'tiers': [
            '<b>Classification of variants</b>: Variants are classified based on current evidence for clinical actionability.', 
            'Tier 1 - Clinical utility has been demonstrated - Actionable / Clinically Relevant variants. Variants in genes with approved therapeutic  implications in specified tumors.', 
            'Tier 2 - Clinical utility/actionability has diagnostic, prognostic or therapeutic implications. Variants with potential diagnostic/classification, prognostic implications. Variants with approved therapeutic implications in a different tumor type. Novel variants in genes that have approved therapeutic implications. Variants associated with Clinical trials.',
            'Tier 3 - Variants of Unknown Significance.'
            ]
}