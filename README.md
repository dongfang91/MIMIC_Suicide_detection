# MIMIC_Suicide_detection
Extract clinical notes from MIMIC dataset that are relevant to the suicidal events.

## Requirements
Python version: 3.6.2

## Usages
* 'data/data.conf' -configuration file for data folders:  MIMIC folder (including D_ICD_DIAGNOSES.csv, DIAGNOSES_ICD.csv
NOTEEVENTS.csv), processed folder (saving cache files), output folder.



* `suicide_patient_all_notes.py` - Extract clinical notes and their attributes for patients attempted suicide.
Two type of notes: 1) all the clinical notes; 2) clinical notes recorded during the admission for suicidal events.

* To extract these notes, please run:
```
$ python suicide_patient_all_notes.py
```

* `suicide_patient_before_during_notes.py` - Extract clinical notes and their attributes for patients attempted suicide.
Two type of notes: 1) all the clinical notes recorded before the admission for suicidal events; 2) all clinical notes recorded during the admission for suicidal events.

* To extract these notes, please run:
```
$ python suicide_patient_before_during_notes.py
```

* `suicide_patient_all_notes.py` - Extract clinical notes and their attributes for patients who have mental issues but do not attempt suicide.
Two type of notes: 1) all the clinical notes; 2) clinical notes recorded during the admission for mental issues.

* To extract these notes, please run:
```
$ python mental_not_suicide_patient_all_notes.py
```

* `suicide_patient_before_during_notes.py` - Extract clinical notes and their attributes for patients who have mental issues but do not attempt suicide.
Two type of notes: 1) all the clinical notes recorded before the admission for mental issues; 2) all clinical notes recorded during the admission for mental issues.

* To extract these notes, please run:
```
$ python mental_not_suicide_patient_before_during_notes.py
```


