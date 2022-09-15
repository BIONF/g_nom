# general imports
from email.mime import base
import json
from urllib import response
from flask import Blueprint, jsonify, request, abort
from . import file_io
from modules.analyses import fetchTaXaminerPathByAssemblyID_AnalysisID
 
# local imports
from modules.notifications import createNotification
from modules.users import ACCESS_LVL_1, ACCESS_LVL_2, validateActiveToken

# setup blueprint name
taxaminer_bp = Blueprint("taxaminer_data", __name__)

# CONST
REQUESTMETHODERROR = {
    "payload": 0,
    "notification": createNotification(message="Wrong request method. Please contact support!"),
}


def get_basepath(assembly_id, analysis_id):
    """Fetch the basepath for a specific taXaminer analysis from the database"""
    db_data = fetchTaXaminerPathByAssemblyID_AnalysisID(assembly_id, analysis_id)
    if db_data[0] == []:
        return False
    else:
        return db_data[0][0]['path'].replace("3D_plot.html", "")

@taxaminer_bp.route('/test', methods=['GET'])
def home():
    return '''<h1>taXaminer API</h1>
<p>A prototype API for accessing taXaminer results</p>'''


@taxaminer_bp.route('/basepath', methods=['GET'])
def basepath():
    query_parameters = request.args
    assembly_id = query_parameters.get("assemblyID")
    analysis_id = query_parameters.get("analysisID")

    db_data = get_basepath(assembly_id=assembly_id, analysis_id=analysis_id)
    if db_data:
        return jsonify({'path': db_data})
    else:
        return abort(404)
    

@taxaminer_bp.route('/datasets', methods=['GET'])
def datasets():
    query_parameters = request.args
    my_id = query_parameters.get("id")

    json_data = file_io.load_datasets()

    # return as json
    return jsonify(json_data)


@taxaminer_bp.route('/scatterplot', methods=['GET'])
def api_filter():
    """
    Filtered scatterplot data
    :return: requested data as JSON string
    """
    query_parameters = request.args
    assembly_id = query_parameters.get("assemblyID")
    analysis_id = query_parameters.get("analysisID")

    basepath = get_basepath(assembly_id=assembly_id, analysis_id=analysis_id)

    if basepath:
        basepath = basepath.replace("3D_plot.html", "")
        json_data = file_io.convert_csv_to_json(basepath + "gene_table_taxon_assignment.csv")
        return jsonify(json_data)
    else:
        return abort(404)

@taxaminer_bp.route('/main', methods=['GET'])
def main_data():
    """
    Filtered main data
    :return: requested data as JSON string
    """
    query_parameters = request.args
    assembly_id = query_parameters.get("assemblyID")
    analysis_id = query_parameters.get("analysisID")

    path = get_basepath(assembly_id=assembly_id, analysis_id=analysis_id)


    json_data = file_io.indexed_data(f"{path}gene_table_taxon_assignment.csv")

    # return as json
    return jsonify(json_data)


@taxaminer_bp.route('/diamond', methods=['GET'])
def diamond_data():
    """
    Diamond date for a certain data point
    :return:
    """
    query_parameters = request.args
    assembly_id = query_parameters.get("assemblyID")
    analysis_id = query_parameters.get("analysisID")
    fasta_id = query_parameters.get("fastaID")

    path = get_basepath(assembly_id=assembly_id, analysis_id=analysis_id)

    if path:
        json_data = file_io.taxonomic_hits_loader(fasta_id, f"{path}taxonomic_hits.txt")
        return jsonify(json_data)
    else:
        return abort(404)


@taxaminer_bp.route('/seq', methods=['GET'])
def amino_acid_seq():
    """
    Amino acid sequence for a specific data point
    :return:
    """
    query_parameters = request.args

    query_parameters = request.args
    assembly_id = query_parameters.get("assemblyID")
    analysis_id = query_parameters.get("analysisID")
    fasta_id = query_parameters.get("fastaID")

    path = get_basepath(assembly_id=assembly_id, analysis_id=analysis_id)
    seq = file_io.fast_fasta_loader(f"{path}proteins.faa", fasta_id)

    # add newlines for formatting, this should be replaced by React code later
    every = 40
    seq = '\n'.join(seq[i:i + every] for i in range(0, len(seq), every))

    # return as json
    return jsonify(seq)

@taxaminer_bp.route('/summary', methods=['GET'])
def summary():
    """
    Amino acid sequence for a specific data point
    :return:
    """
    query_parameters = request.args
    my_id = query_parameters.get("id")

    data = file_io.load_summary(dataset_id=my_id)

    # return as json
    return response(data, mimetype="text")


@taxaminer_bp.route('/userconfig', methods=['GET', 'PUT'])
def get_config():
    """
    User config data
    :return:
    """
    query_parameters = request.args

    # get user settings
    if request.method == "GET":
        data = file_io.load_user_config()
        # return as json
        return data
    
    # set user settings
    elif request.method == "PUT":
        settings = file_io.parse_user_config()
        # apply changes
        for key in request.json.keys():
            settings[key] = request.json[key]
        file_io.write_user_config(settings)
        return "OK"


@taxaminer_bp.route('/pca_contribution', methods=['GET'])
def pca_contributions():
    """
    PCA data
    :return:
    """
    query_parameters = request.args

    my_id = query_parameters.get("id")

    data = file_io.load_pca_coords(my_id)

    # return as json
    return jsonify(data)

@taxaminer_bp.route("/download/fasta", methods=['POST'])
def download_fasta():
    """Download a .fasta of the user selection."""
    # genes to include
    genes = request.json['genes']
    sequences = []

    query_parameters = request.args
    assembly_id = query_parameters.get("assemblyID")
    analysis_id = query_parameters.get("analysisID")
    fasta_id = query_parameters.get("fasta_id")

    path = get_basepath(assembly_id=assembly_id, analysis_id=analysis_id)

    # load requested sequences
    for gene in genes:
        sequences.append(">" + gene + '\n' + file_io.fast_fasta_loader(f"{path}proteins.faa", gene))

    response_text = "\n".join(sequences)

    # API answer
    return Response(response_text, mimetype="text", headers={"Content-disposition": "attachment; filename=myplot.csv"})

