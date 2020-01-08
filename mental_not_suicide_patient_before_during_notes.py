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

def get_patient_for_admission(patient_admissions,patient):
    patient_admissions_subset = {}
    for key, value in patient_admissions.items():
        if key.split("_") [1] == patient:
            patient_admissions_subset[key] = value
    return patient_admissions_subset

def get_duration(dictionary):
    dictionary_new = {}
    for patient_admission_id, times in dictionary.items():
        datetimes = []
        for time in times:
            time_items = time.split("-")
            datetime_new = date(int(time_items[0]), int(time_items[1]), int(time_items[2]))
            datetimes.append(datetime_new)
        datetimes.sort()
        if len(datetimes)>1:
            dictionary_new[patient_admission_id] = {}
            dictionary_new[patient_admission_id] = [datetimes[0],datetimes[-1]]
            # print(datetimes[0],datetimes[-1])
        else:
            dictionary_new[patient_admission_id] = [datetimes[0], datetimes[0]]
            # print(datetimes[0],datetimes[0])
    return dictionary_new


def patient_admission_duration():
    patient_ids = []
    admission_id = []
    patient_mental_not_suicide_all = read.read_from_tsv(os.path.join(output_folder,"mental_patient_all_notes.tsv"))
    row_patient_admission_time ={}

    for row in patient_mental_not_suicide_all:
        row_patient_admission= row[0]+"_"+row[1] + "_" + row[2]
        add_key_dict(row_patient_admission_time, row_patient_admission, row[3])

    print("patients (mental_not_suicide) time information are collected......")

    patient_mental_not_suicide_admission = read.read_from_tsv(os.path.join(output_folder,"mental_patient_admission_notes.tsv"))

    mental_not_suicide_patient_admission_time = {}
    for row in patient_mental_not_suicide_admission:
        if row[1] not in patient_ids:
            patient_ids.append(row[1])
        if row[2] not in admission_id:
            admission_id.append(row[2])

        add_key_dict(mental_not_suicide_patient_admission_time, row[1], row[3])

    print("patients_admission (mental_not_suicide) timelines are collected......")
    mental_not_suicide_patient_all_time_formatted ={}
    for key, value in row_patient_admission_time.items():
        time_items = value[0].split("-")
        datetime_new = date(int(time_items[0]), int(time_items[1]), int(time_items[2]))
        mental_not_suicide_patient_all_time_formatted[key] = datetime_new

    mental_not_suicide_patient_admission_period = get_duration(mental_not_suicide_patient_admission_time)
    print("patients_admission (mental_not_suicide) timelines are calculated......")

    patient_admission_before = []
    patient_admission_meanwhile = []

    for patient_id in patient_ids:

        mental_not_suicide_admission_time = mental_not_suicide_patient_admission_period[patient_id]
        mental_not_suicide_patient_all_time = get_patient_for_admission(mental_not_suicide_patient_all_time_formatted, patient_id)

        for key, admission_time in mental_not_suicide_patient_all_time.items():
            row_id, _, _ = key.split("_")
            if admission_time < mental_not_suicide_admission_time[0]:
                patient_admission_before.append(row_id)
            elif admission_time > mental_not_suicide_admission_time[1]:
                None
            else:
                patient_admission_meanwhile.append(row_id)

    read.save_in_json(os.path.join(cache_folder,"mental_not_suicide_patient_admission_before"),patient_admission_before)
    read.save_in_json(os.path.join(cache_folder,"mental_not_suicide_patient_admission_meanwhile"),patient_admission_meanwhile)
    return patient_admission_before, patient_admission_meanwhile

def get_documents():
    patient_admission_before, patient_admission_meanwhile  = patient_admission_duration()
    file_notes_title_before = []
    file_notes_title_meanwhile = []

    with open(  "data/NOTEEVENTS.csv", 'r') as mycsvfile:
        files = csv.reader(mycsvfile, delimiter=',')
        for idx,row in enumerate(files):
            if row[0] in patient_admission_before:
                if row[6] == "Discharge summary":
                    file_notes_title_before.append(row[:-1])
                    read.save_in_txt_string(os.path.join(output_folder,
                        "discharge_summaries/mental_not_suicide_patient_before/" + row[0] + "_" + row[1] + "_" + row[2] + ".txt"), row[-1])

            elif row[0] in patient_admission_meanwhile:
                if row[6] == "Discharge summary":
                    file_notes_title_meanwhile.append(row[:-1])
                    read.save_in_txt_string(os.path.join(output_folder,
                        "discharge_summaries/mental_not_suicide__patient_during/" + row[0] + "_" + row[1] + "_" + row[2] + ".txt"), row[-1])

    read.save_in_tsv(os.path.join(output_folder,"discharge_summaries/mental_not_suicide_patient_before.tsv"),
                      file_notes_title_before)

    read.save_in_tsv(os.path.join(output_folder,"discharge_summaries/mental_not_suicide_patient_during.tsv"),
                      file_notes_title_meanwhile)


get_documents()
