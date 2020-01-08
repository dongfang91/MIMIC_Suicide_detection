import csv as csv
import read_files as read
import configparser
import os
from datetime import *

config = configparser.ConfigParser()
config.read('data/data.conf')
mimic = config['MIMIC']['mimic']
cache_folder = config['CACHE']['processed_mental_not_suicide']
output_folder = config['OUTPUT']['mental_not_suicide']

def add_key_dict(dict,key,item):
    if key in dict:
        dict[key].append(item)
    else:
        dict[key] = [item]

def read_suicide_icd_code_from_dicddiagnoses(icd = "D_ICD_DIAGNOSES.csv"):
    with open( os.path.join(mimic, icd), 'r') as mycsvfile:
        files = csv.reader(mycsvfile, delimiter=',')
        dataset = list()
        for row in files:
            if "suicide" in row[3].lower():
                dataset.append(row)
    return dataset

def read_mental_disorder_icd_code_from_dicddiagnoses(icd = "D_ICD_DIAGNOSES.csv"):
    icd_codes = read.read_from_csv(os.path.join(mimic, icd))[1:]
    row = []
    for item in icd_codes:
        if all([letter not in item[1] for letter in ["V","E","M"]]):
            code = int(item[1][:3])
            if int(item[0])>2000 and code <= 319 and code>=290:
                row.append(item)
    return row

def read_patient_admission_from_diagnosesicd(icds):

    suicide_icd_codes = [icd[1] for icd in icds]
    patient = []
    with open( os.path.join(mimic,"DIAGNOSES_ICD.csv"), 'r') as mycsvfile:
        files = csv.reader(mycsvfile, delimiter=',')
        for idx, row in enumerate(files):
            if row[4] in suicide_icd_codes:
                patient.append(row)
    return patient

dataset = read_patient_admission_from_diagnosesicd()

def read_event_info_from_noteevents():

    suicide_icds = read_suicide_icd_code_from_dicddiagnoses(os.path.join(mimic,"D_ICD_DIAGNOSES.csv"))
    mental_icds = read_mental_disorder_icd_code_from_dicddiagnoses(os.path.join(mimic,"D_ICD_DIAGNOSES.csv"))


    patient_suicide = read_patient_admission_from_diagnosesicd(suicide_icds)
    patient_mental = read_patient_admission_from_diagnosesicd(mental_icds)

    # read.save_in_tsv("data/new/suicide_patient_admission_id.tsv",dataset)

    suicide_patient_id = list(set([item[1] for item in patient_suicide]))
    mental_patient_id = list(set([item[1] for item in patient_mental]))


    patient_mental_not_suicide = [item for item in patient_mental if item[1] not in suicide_patient_id]


    ######################### no. of patient with suicidal events #####################
    print("no. of patient with suicidal events: ", len(suicide_patient_id))


    ######################### no. of patient with mental disorders #####################
    print("no. of patient with mental disorders: ", len(mental_patient_id))

    ######### no. of patient with mental disorders attempted suicide ####################
    dataset_mental_suicide = [item for item in mental_patient_id if item in suicide_patient_id]
    print("no. of patient with mental disorders attempted suicide: ", len(dataset_mental_suicide))

    ######### no. of patient with mental disorders do not attempte suicide ####################
    dataset_mental_not_suicide = [item for item in mental_patient_id if item not in suicide_patient_id]
    print("no. of patient with mental disorders do not attempte suicide: ", len(dataset_mental_not_suicide))

    ######### no. of patient with suicidal events with mental disorder ####################
    dataset_suicide_mental = [item for item in suicide_patient_id if item  in mental_patient_id ]
    print("no. of patient with suicidal events with mental disorder: ", len(dataset_suicide_mental))

    ######### no. of patient with suicidal events but do not have mental disorder ####################
    dataset_suicide_not_mental = [item for item in suicide_patient_id if item not in mental_patient_id ]
    print("no. of patient with suicidal events but do not have mental disorder: ", len(dataset_suicide_not_mental))

    hadm = list(set([item[2] for item in patient_mental_not_suicide]))
    patient_mental_not_suicide_id = list(set([item[1] for item in patient_mental_not_suicide]))
    mental_not_suicide_patient_admission = []
    mental_not_suicida_patient = []

    with open( os.path.join(mimic, "NOTEEVENTS.csv"), 'r') as mycsvfile:
        files = csv.reader(mycsvfile, delimiter=',')
        for row in files:
            if row[1] in patient_mental_not_suicide_id:
                mental_not_suicida_patient.append(row[:-1])
                if row[2] in hadm:
                    mental_not_suicide_patient_admission.append(row[:-1])

    read.save_in_tsv(os.path.join(output_folder,"mental_patient_admission_notes.tsv"),mental_not_suicide_patient_admission)
    read.save_in_tsv(os.path.join(output_folder,"mental_patient_all_notes.tsv"), mental_not_suicida_patient)


###########  Get patint (all and only for addmission) notes for patients with mental issues but not attempting suicide ##########################
read_event_info_from_noteevents()