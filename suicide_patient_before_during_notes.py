import read_files as read
from collections import Counter,OrderedDict
from datetime import *
import csv
import os

import configparser
config = configparser.ConfigParser()
config.read('data/data.conf')
mimic = config['MIMIC']['mimic']
cache_folder = config['CACHE']['processed_suicide']
output_folder = config['OUTPUT']['output_suicide']

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


def read_all_notes_for_patients_admission_time():
    patient_id = []
    admission_id = []
    patient_notes_all = read.read_from_tsv(os.path.join(output_folder,"note_events_all.tsv"))[1:]
    row_patient_admission_time = {}

    for row in patient_notes_all:
        row_patient_admission = row[0] + "_" + row[1] + "_" + row[2]
        add_key_dict(row_patient_admission_time, row_patient_admission, row[3])

    read.save_in_json(os.path.join(cache_folder,"suicide_patient_id/allnotes_row_patient_admission_time"),
                      row_patient_admission_time)

    patient_notes_suicide = read.read_from_tsv(os.path.join(output_folder,"note_events_suicidal.tsv"))[1:]

    suicide_patient_admission_time = {}
    for row in patient_notes_suicide:
        if row[1] not in patient_id:
            patient_id.append(row[1])
        if row[2] not in admission_id:
            admission_id.append(row[2])

        add_key_dict(suicide_patient_admission_time, row[1], row[3])

    read.save_in_json(os.path.join(cache_folder,"suicide_patient_id/suicidalnotes_patient_admission_time"),suicide_patient_admission_time)
    read.save_in_json(os.path.join(cache_folder,"suicide_patient_id/patient_id"),patient_id)
    print(len(admission_id))
    print(len(patient_id))


read_all_notes_for_patients_admission_time()


def analyze_patient_admission_date():
    patient_ids = read.read_from_json(os.path.join(cache_folder,"suicide_patient_id/patient_id"))

    patient_admission_time = read.read_from_json(os.path.join(cache_folder,"suicide_patient_id/allnotes_row_patient_admission_time"))
    patient_admission_time_formatted ={}
    for key, value in patient_admission_time.items():
        time_items = value[0].split("-")
        datetime_new = date(int(time_items[0]), int(time_items[1]), int(time_items[2]))
        patient_admission_time_formatted[key] = datetime_new

    suicide_patient_admission_time = read.read_from_json(os.path.join(cache_folder,"suicide_patient_id/suicidalnotes_patient_admission_time"))
    suicide_patient_admission_time = get_duration(suicide_patient_admission_time)

    patient_admission_before = {}
    patient_admission_meanwhile = {}
    patient_admission_after = {}
    for patient_id in patient_ids:

        suicide_admission_time = suicide_patient_admission_time[patient_id]
        patient_admission_time = get_patient_for_admission(patient_admission_time_formatted ,patient_id)

        for key, admission_time in patient_admission_time.items():
            row_id, _, _ = key.split("_")
            if admission_time< suicide_admission_time[0]:
                add_key_dict(patient_admission_before,patient_id, row_id)
            elif admission_time > suicide_admission_time[1]:
                add_key_dict(patient_admission_after,patient_id, row_id)
            else:
                add_key_dict(patient_admission_meanwhile,patient_id, row_id)

    print(len(patient_admission_before))
    #print(patient_admission_before)
    read.save_in_json(os.path.join(cache_folder,"suicide_patient_id/suicide_before_patient_admission"),patient_admission_before)
    print(len(patient_admission_after))
   # print(patient_admission_after)
    read.save_in_json(os.path.join(cache_folder,"suicide_patient_id/suicide_after_patient_admission"), patient_admission_after)
    print(len(patient_admission_meanwhile))
    #print(patient_admission_meanwhile)
    read.save_in_json(os.path.join(cache_folder,"suicide_patient_id/suicide_meanwhile_patient_admission"), patient_admission_meanwhile)

analyze_patient_admission_date()

def suicide_meanwhile_notes(file_name):
    target_description = ["Nursing/other", "Nursing", "Physician", "Discharge summary", "Social Work", "General",
                          "Nutrition", "Rehab Services", "Case Management", "Consult"]

    suicide_meanwhile = read.read_from_json(os.path.join(cache_folder,"suicide_patient_id/"+file_name))
    title = read.read_from_tsv(os.path.join(cache_folder,"suicide_patient_notes_all.tsv"))[:1]
    patient_notes_all = read.read_from_tsv(os.path.join(cache_folder,"suicide_patient_notes_all.tsv"))[1:]
    suicide_meanwhile_notes = title
    none_admission_id = []
    admission_id =[]
    notes_all  = []
    notes_all_subset = []
    # admission_id_new = read.read_from_json(os.path.join(cache_folder,"suicide_patient_id/admission_id"))

    for row in patient_notes_all:
        if row[1] in suicide_meanwhile:
            if row[0]  in suicide_meanwhile[row[1]]:
                if row[2] =="":
                    # print(row)
                    none_admission_id.append(row[0])
                elif row[2] not in admission_id:
                    admission_id.append(row[2])
                else:
                    None
                if row[6] in target_description:
                    notes_all_subset.append(row[0])
                suicide_meanwhile_notes.append(row)
                notes_all.append(row[0])

    print("patients: ", len(suicide_meanwhile))
    print("admission with id: ", len(admission_id))
    print("admission without id: ", len(none_admission_id))
    print("all notes: ", len(notes_all))

    # for admission_id_1 in admission_id:
    #     if admission_id_1 not in admission_id_new:
    #         print(admission_id_1)

    read.save_in_tsv(os.path.join(output_folder,"suicide_patient_id/"+ file_name + ".tsv"),
                      suicide_meanwhile_notes)

suicide_meanwhile_notes("suicide_before_patient_admission")
suicide_meanwhile_notes("suicide_after_patient_admission")
suicide_meanwhile_notes("suicide_meanwhile_patient_admission")

def get_documents():
    suicide_meanwhile_patient_admission = read.read_from_tsv(
        os.path.join(output_folder,"suicide_patient_id/suicide_meanwhile_patient_admission.tsv"))

    file_notes_title_meanwhile = suicide_meanwhile_patient_admission[:1]
    file_notes_meanwhile = suicide_meanwhile_patient_admission[1:]
    row_meanwhile = [row[0] for row in file_notes_meanwhile]

    suicide_before_patient_admission = read.read_from_tsv(
        os.path.join(output_folder, "suicide_patient_id/suicide_before_patient_admission.tsv"))
    file_notes_title_before = suicide_before_patient_admission[:1]
    file_notes_before = suicide_before_patient_admission[1:]
    row_before = [row[0] for row in file_notes_before]

    with open(  "data/NOTEEVENTS.csv", 'r') as mycsvfile:
        files = csv.reader(mycsvfile, delimiter=',')
        for row in files:
            if row[0] in row_before:
                if row[6] == "Discharge summary":
                    file_notes_title_before.append(row[:-1])
                    read.save_in_txt_string(
                        os.path.join(output_folder,"discharge_summaries/suicide_patient_before/" + row[0] + "_" + row[1] + "_" + row[2] + ".txt"), row[-1])

            elif row[0] in row_meanwhile:
                if row[6] == "Discharge summary":
                    file_notes_title_meanwhile.append(row[:-1])
                    read.save_in_txt_string(
                        os.path.join(output_folder , "discharge_summaries/suicide_patient_during/" + row[0] + "_" + row[1] + "_" + row[2] + ".txt"), row[-1])

    read.save_in_tsv(os.path.join(output_folder, "discharge_summaries/suicide_patient_before.tsv"),
                      file_notes_title_before)

    read.save_in_tsv(os.path.join(output_folder,"discharge_summaries/suicide_patient_during.tsv"),
                      file_notes_title_meanwhile)

get_documents()

################   Get all discharge summaries notes #################


# def get_all_discharge():
#     file_notes_title_meanwhile = read.read_from_tsv(
#         "data/processed/suicide_patient_id/suicide_before_patient_admission.tsv")[:1]
#
#     with open(  "data/NOTEEVENTS.csv", 'r') as mycsvfile:
#         files = csv.reader(mycsvfile, delimiter=',')
#         for row in files:
#             if row[6] == "Discharge summary":
#                 file_notes_title_meanwhile.append(row[:-1])
#                 read.save_in_txt_string(
#                         "data/processed/discharge_summaries/overall/" + row[0] + "_" + row[1] + "_" + row[2] + ".txt", row[-1])
#
#     read.save_in_tsv("data/processed/discharge_summaries/overall.tsv",
#                       file_notes_title_meanwhile)

# get_all_discharge()