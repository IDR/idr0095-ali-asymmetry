#! /usr/bin/env python

import pandas
import sys


DATASET_MAPPINGS = {
    'AO1TO1_Trial1': 'AO1TO1-Trial1',
    'AO1TO1_Trial2': 'AO1TO1-Trial2',
    'AO1TO2_Trial1': 'AO1TO2-Trial1',
    'AO1TO2_Trial2': 'AO1TO2-Trial2',
    'AO1TOid_Trial1': 'AO1TOid-Trial1',
    'AO1TOid_Trial2': 'AO1TOid-Trial2',
    'DAStag_Trial1': 'DAStag_Trial1',
    'DAStag_Trial2': 'DAStag_Trial2',
    'DAStag_Trial3': 'DAStag_Trial3',
    'DAS+4tag_Trial1': 'DAS_4tag_Trial1',
    'DAS+4tag_Trial2': 'DAS_4tag_Trial2',
    'DAS+4tag_Trial3': 'DAS_4tag_Trial3',
    'LAAtag_Trial1': 'LAAtag_Trial1',
    'LAAtag_Trial2': 'LAAtag_Trial2',
    'LAAtag_Trial3': 'LAAtag_Trial3',
    'Notag_Trial1': 'Notag_Trial1',
    'Notag_Trial2': 'Notag_Trial2',
    'Notag_Trial3': 'Notag_Trial3',
    'O1_Glu_Trial1': 'Fig5A_O1/GluT1',
    'O1_Glu_Trial2': 'Fig5A_O1/GluT2',
    'O1_Glu_Trial3': 'Fig5A_O1/GluT3',
    'O1_Ace_Trial1': 'Fig5A_O1/AceT1',
    'O1_Ace_Trial2': 'Fig5A_O1/AceT2',
    'O1_Ace_Trial3': 'Fig5A_O1/AceT3',
    'O1_Gly_Trial1': 'Fig5A_O1/GlyT1',
    'O1_Gly_Trial2': 'Fig5A_O1/GlyT2',
    'O1_Gly_Trial3': 'Fig5A_O1/GlyT3',
    'O1_RDM_Trial1': 'Fig5A_O1/RDMT1',
    'O1_RDM_Trial2': 'Fig5A_O1/RDMT2',
    'O1_RDM_Trial3': 'Fig5A_O1/RDMT3',
    'O2_Glu_Trial1': 'Fig5B_O2/Glu_T1',
    'O2_Glu_Trial2': 'Fig5B_O2/Glu_T2',
    'O2_Glu_Trial3': 'Fig5B_O2/Glu_T3',
    'O2_Ace_Trial1': 'Fig5B_O2/Ace_T1',
    'O2_Ace_Trial2': 'Fig5B_O2/Ace_T2',
    'O2_Ace_Trial3': 'Fig5B_O2/Ace_T3',
    'O2_Gly_Trial1': 'Fig5B_O2/Gly_T1',
    'O2_Gly_Trial2': 'Fig5B_O2/Gly_T2',
    'O2_Gly_Trial3': 'Fig5B_O2/Gly_T3',
    'O2_RDM_Trial1': 'Fig5B_O2/RDMT1',
    'O2_RDM_Trial2': 'Fig5B_O2/RDMT2',
    'O2_RDM_Trial3': 'Fig5B_O2/RDMT3',
    'Oid_Glu_Trial1': 'Fig5C-Oid/Glu_T1',
    'Oid_Glu_Trial2': 'Fig5C-Oid/Glu_T2',
    'Oid_Glu_Trial3': 'Fig5C-Oid/Glu_T3',
    'Oid_Ace_Trial1': 'Fig5C-Oid/Ace_T1',
    'Oid_Ace_Trial2': 'Fig5C-Oid/Ace_T2',
    'Oid_Ace_Trial3': 'Fig5C-Oid/Ace_T3',
    'Oid_Gly_Trial1': 'Fig5C-Oid/Gly_T1',
    'Oid_Gly_Trial2': 'Fig5C-Oid/Gly_T2',
    'Oid_Gly_Trial3': 'Fig5C-Oid/Gly_T3',
    'Oid_RDM_Trial1': 'Fig5C-Oid/RDM_T1',
    'Oid_RDM_Trial2': 'Fig5C-Oid/RDM_T2',
    'Oid_RDM_Trial3': 'Fig5C-Oid/RDM_T3',
}
FILEPATH = "/uod/idr/filesets/idr0095-ali-asymmetry/20200831-ftp"


def process_experiment(experiment):
    annotations_file = f'{experiment}/idr0095-{experiment}-annotation.csv'
    source = pandas.read_csv(annotations_file)

    target = pandas.DataFrame(columns=('Target', 'Path', 'Name'))
    for index, row in source.iterrows():
        dataset_name = row['Dataset Name']
        target_container = (
            f"Project:name:idr0095-ali-asymmetry/{experiment}/"
            f"Dataset:name:{dataset_name}")

        folder = DATASET_MAPPINGS[f"{dataset_name}"]
        filename = row['Image File (nd2)'] + '.nd2'
        path = f"{FILEPATH}/{folder}/{filename}"
        target.loc[len(target)] = (target_container, path, row['Image Name'])
        target.to_csv(
            path_or_buf=f"{experiment}/idr0095-{experiment}-filePaths.tsv",
            sep='\t', header=False, index=False)


def main(argv):
    for experiment in ['experimentA', 'experimentB', 'experimentC']:
        process_experiment(experiment)


if __name__ == "__main__":
    main(sys.argv[1:])
