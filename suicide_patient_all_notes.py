import configparser
import csv as csv
import os
from collections import Counter

import read_files as read

config = configparser.ConfigParser()
config.read('data/data.conf')
mimic = config['MIMIC']['mimic']
cache_folder = config['CACHE']['processed_suicide']
output_folder = config['OUTPUT']['output_suicide']



def suicial_icd_codes(icd = "D_ICD_DIAGNOSES.csv"):
    '''
    get icd codes that are relevant to suicidal events from table D_ICD_DIAGNOSES.csv
    :return:
    '''
    icd_path = os.path.join(mimic, icd)
    # data = read_from_csv_icd("data/D_ICD_DIAGNOSES.csv")
    with open(icd_path, 'r') as mycsvfile:
        files = csv.reader(mycsvfile, delimiter=',')
        dataset = list()
        for row in files:
            if "suicide" in row[3].lower():
                dataset.append(row)
    print("No. of icd codes that are relevant to suicidal events: ", len(dataset))
    print("For example, ")

    ########   Save sucidal ICD codes into the local repository  #######
    # read.save_in_tsv("data/processed/suicide_icd_9.tsv",dataset)
    # read.save_in_json("data/processed/suicide_icd_9",dataset)

    return dataset

def add_key_dict(dict,key,item):
    if key in dict:
        dict[key].append(item)
    else:
        dict[key] = [item]


def patients_attempt_suicide(d_icd = "data/DIAGNOSES_ICD.csv"):
    '''
    get patients whose diagnosis codes contain any of those suicidal codes from DIAGNOSES_ICD.csv
    :return:
    '''
    d_icd_path = os.path.join(mimic, d_icd)

    ### The following files could be extended ##########
    suicide_icds = suicial_icd_codes()    ####read.read_from_json("data/processed/suicide_icd_9")
    suicide_icd_codes = [suicide_icd[1] for suicide_icd in suicide_icds]
    with open(d_icd_path, 'r') as mycsvfile:
        files = csv.reader(mycsvfile, delimiter=',')
        dataset_diagnosis = []
        dataset_diagnosis_with_header =[]
        for idx, row in enumerate(files):
            if idx ==0:
                dataset_diagnosis_with_header.append(row)
            if row[4] in suicide_icd_codes:     ### Check whether the diagnosis codes contain any of the suicidal codes ###
                dataset_diagnosis.append(row)
                dataset_diagnosis_with_header.append(row+suicide_icds[suicide_icd_codes.index(row[4])])

    #####################  suicide_patient.tsv has the table header  ################
    read.save_in_tsv(os.path.join(cache_folder, "suicide_patient.tsv"), dataset_diagnosis_with_header)
    print("No. of patients that have attempted suicide: ", len(dataset_diagnosis))
    return dataset_diagnosis

def notes_suicidal_patients():
    dataset = patients_attempt_suicide()
    patient_s = Counter([item[1] for item in dataset])
    print(patient_s)
    patient_ids = list(set([item[1] for item in dataset]))
    print(len(patient_ids))
    hosp_adm_ids = list(set([item[2] for item in dataset]))
    print(len(hosp_adm_ids))

    with open(os.path.join(mimic,"NOTEEVENTS.csv"), 'r') as mycsvfile:
        files = csv.reader(mycsvfile, delimiter=',')
        note_events_all = []
        note_events_suicidal = []
        for row in files:
            if row[1] in patient_ids:
                note_events_all.append(row[:-1])
                if row[2] in hosp_adm_ids:
                    note_events_suicidal.append(row[:-1])

    read.save_in_tsv( os.path.join(output_folder,"note_events_suicidal.tsv"), note_events_suicidal)
    read.save_in_tsv( os.path.join(output_folder,"note_events_all.tsv"), note_events_all)



notes_suicidal_patients()





