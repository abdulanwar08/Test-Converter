import pandas as pd
import numpy as np
import csv
import optparse
import subprocess
import os
import tempfile

import sys
sys.path.append("..")

from util.mylogs import Logger
from util.htmlstyling import highlight_color, html
from util.properties import getconfigprop


#Initiate Logs
LOG = Logger()
LOG.info("Test Execution is Started...")
 
#Read input file path
configs=getconfigprop()
input=configs.get("input").data

#Run Transformation through command line

LOG.info("Transformation ran succesfully")
##subprocess.call(r'RunPentahoJob.bat')

#Read the output files from pentaho
LOG.info("Read pentaho output files for comparison...")
try:
    usg_tot_path=input+'\\'+configs.get("UsageTotal").data
    inv_tot_path=input+'\\'+configs.get("InvoiceTotal").data
    exp_tot_path=input+'\\'+configs.get("ExpectedTotal").data
except Exception as e:
    LOG.error("Output filenames are not available in property file")
    LOG.error(e)
    
usage_total_file=pd.read_csv(usg_tot_path,sep=';',index_col=0)
usage_total_file.columns += '_output'
invoice_total_file=pd.read_csv(inv_tot_path,sep=';')
invoice_total_file.columns += '_output'

#Modify index name for invoice_total
try:
    LOG.info("Modify index value")
    df=pd.DataFrame(invoice_total_file)
    df1=df.set_index([pd.Index(['Charges'])])
    df1.to_csv(inv_tot_path, index=True)
    invoice_total_file_new=pd.read_csv(inv_tot_path,sep=',',index_col=0)
    LOG.info("Modified index value")
except Exception as e:
    LOG.error("Unable to modify index value")
    LOG.error(e)

LOG.info("Read the mapping files for comparison")
try:
    keyword = 'mapping'
    for fname in os.listdir(input):
        if keyword in fname:
            mapping_file=pd.read_excel(input+'\\'+fname,sheet_name='Notes',usecols=[0,1])
    map_df = pd.DataFrame(mapping_file)
    map_df=map_df[(map_df["Reports"] == "Charges")  | (map_df["Reports"] == "Messages") | (map_df["Reports"] == "Data") | (map_df["Reports"] == "Minutes")]
    map_df.to_csv(exp_tot_path, index=True)
    mapping_file=pd.read_csv(exp_tot_path,sep=',',index_col=1)
    mapping_file.columns += ' Expected'
except Exception as e:
    LOG.error("Unable to read the mapping files")
    LOG.error(e)

#merge the files
try:
    LOG.info("Merge the files")
    merge_calc_file = pd.merge(left=invoice_total_file_new, right=usage_total_file, how='outer', left_index=True, right_index=True) 
    merge_file = pd.merge(left=merge_calc_file, right=mapping_file['Line Totals Expected'], how='outer', left_index=True, right_index=True) 
    LOG.info("Merging is successful")
except Exception as e:
    LOG.error("Merging is not successful")
    LOG.error(e)
    

try:
    LOG.info("Compare Usage Total values")
    for i in range(len(merge_file)) :
        if(merge_file.index.values[i] != 'Charges'):
            #compare the usage_total values between two files
            merge_file['Usg_Total_Match?'][i] = np.where(merge_file['Line Totals Expected'][i] == merge_file['usage_total_output'][i], 'Matching', 'Not Matching')
            merge_file['Usg_Total_Diff?'][i] = np.where(merge_file['Line Totals Expected'][i] == merge_file['usage_total_output'][i], 0, str(merge_file['Line Totals Expected'][i] - merge_file['usage_total_output'][i]))
            LOG.info("Comparison of Usage Total values is Successful")
            merge_file['Inv_Total_Match?'][i] = 'NA'
            merge_file['Inv_Total_Diff?'][i] = 'NA'
        else:
            #compare the invoice_total values between two files
            merge_file['Inv_Total_Match?'] = np.where(merge_file['Line Totals Expected'] == merge_file['invoice_total_output'], 'Matching', 'Not Matching')
            merge_file['Inv_Total_Diff?'] = np.where(merge_file['Line Totals Expected'] == merge_file['invoice_total_output'], 0, str(merge_file['Line Totals Expected'] - merge_file['invoice_total_output']))
            LOG.info("Comparison of Invoice Total values is Successful")
            merge_file['Usg_Total_Match?'] = 'NA'
            merge_file['Usg_Total_Diff?'] = 'NA'
    
except Exception as e:
    LOG.error("Comparison of Usage Total values is not Successful")
    LOG.error(e)
    
#arrange columns
columns = ['Line Totals Expected','invoice_total_output','Inv_Total_Match?','Inv_Total_Diff?','usage_total_output','Usg_Total_Match?','Usg_Total_Diff?']
merge_file = merge_file.replace(np.nan, 0)
merge_file.columns = merge_file.columns.str.capitalize()
pd.set_option('display.max_columns', None)
merge_file.head()

#apply styling
try:
    output=merge_file.style.applymap(highlight_color)
    LOG.info("Generate HTML Report")
    report=input+'\\'+configs.get("Report").data
    html_output = output.render()
    with open(report,"w") as file:
        file.write(html_output)
    with open(report) as file:
            file = file.read()
    file = file.replace("<table ", "<table class='rwd-table'")
    with open(report, "w") as file_to_write:
            file_to_write.write(html + file)
    os.startfile(report)
    LOG.info("HTML Report generation is successful")
    LOG.info("Test Execution is Successful")
except Exception as e:
    LOG.error("Unable to generate HTML Report")
    LOG.error(e)
    LOG.error("Execution is Failed")
