# TODO remove this once testing has finished

import csv
import json

from flask import jsonify

def load_datasets():
    with open('./datasets/datasets.json', 'r') as f:
        data = json.load(f)
    return data

def convert_csv_to_json(path):
    """Load the main scatterplot datafile and convert it to JSON"""
    with open(path, encoding='utf-8') as csvf:
        # load csv file data using csv library's dictionary reader
        csv_reader = csv.DictReader(csvf)
        labeled_dict = dict()

        for row in csv_reader:
            if row['plot_label'] in labeled_dict.keys():
                labeled_dict[row['plot_label']].append(row)
            else:
                labeled_dict[row['plot_label']] = [row]

    traces_list = []
    for key in labeled_dict.keys():
        traces_list.append(labeled_dict[key])

    return traces_list


def fast_fasta_loader(path, fasta_id):
    """Load fasta sequence data"""
    seq = ""
    start_index = -1

    with open(path, "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            lines[i] = line.rstrip()

    for i, line in enumerate(lines):
        if line.startswith(">" + fasta_id):
            start_index = i
            break

    if start_index == -1:
        return ""

    for i in range(start_index + 1, len(lines)):
        if not lines[i].startswith(">"):
            seq += lines[i]
        else:
            break

    return seq


def diamond_to_json_str(path):
    """Convert diamond table rows to JSON strings"""
    rows = []
    # format as defined here:
    # https://github.com/fdarthen/taXaminer/blob/988f408afed4830e23a1b8b837b24bab3e8fc5b9/taxonomic_assignment.py#L718
    fields = ['qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen', 'qstart', 'qend', 'sstart', 'send',
              'evalue', 'bitscore', 'taxid', 'taxname']
    with open(path, encoding='utf-8') as csvf:
        # load csv file data using csv library's dictionary reader
        csv_reader = csv.DictReader(csvf, delimiter='\t', fieldnames=fields)
        for i, row in enumerate(csv_reader):
            json_string = json.dumps(row)
            rows.append(json_string)
    
    return rows

def taxonomic_hits_loader(fasta_id, path):
    """Load all taxonomic hits"""
    fields = ['qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen', 'qstart', 'qend', 'sstart', 'send',
              'evalue', 'bitscore', 'staxids', 'ssciname']
    match_rows = []
    start_index = -1
    with open(path, encoding='utf-8') as csvf:
        # load csv file data using csv library's dictionary reader
        csv_reader = csv.DictReader(csvf, delimiter='\t', fieldnames=fields)
        for i, row in enumerate(csv_reader):
            if row['qseqid'] == fasta_id:
                match_rows.append(row)

    for row in match_rows:
        if len(row['ssciname']) > 20:
            row['ssciname'] = row['ssciname'][0:20] + "..."
    return match_rows

def load_user_config(path):
    """Load a user config"""
    with open(f"{path}user_config.json", "r") as file:
        lines = file.readlines()
    
    return "".join(lines)

def parse_user_config(path):
    """Parse user config to JSON"""
    with open(f'{path}user_config.json', 'r') as f:
        data = json.load(f)
    return data

def write_user_config(json_data, path):
    """Write user config to disk"""
    with open(f'{path}user_config.json', 'w') as json_file:
        json.dump(json_data, json_file)

def load_pca_coords(dataset_id):
    """3D plot of variable contribution"""
    with open(f"/flask-backend/data/storage/taxa/Burkholderia_multivorans/Burkholderia_multivorans_id1/analyses/taxaminer/Burkholderia_multivorans_id1_taxaminer_id1/pca_loadings.csv", 'r') as file:
        lines = file.readlines()
    
    final_lines = []
    for line in lines[1:-1]:
        fields = line.split(",")
        new_dict = dict()
        new_dict['label'] = fields[0]
        new_dict['x'] = [fields[1]]
        new_dict['y'] = [fields[2]]
        new_dict['z'] = [fields[3]]
        final_lines.append(new_dict)
    
    return final_lines

def indexed_data(path):
    """Load the main scatterplot datafile and convert it to JSON"""
    with open(path, encoding='utf-8') as csvf:
        # load csv file data using csv library's dictionary reader
        csv_reader = csv.DictReader(csvf)
        labeled_dict = dict()

        for row in csv_reader:
            labeled_dict[row['g_name']] = row


    return labeled_dict

