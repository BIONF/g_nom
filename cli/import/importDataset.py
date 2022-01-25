from subprocess import run
from sys import argv
from os.path import exists
from uuid import uuid1
from jsonschema import validate
from json import dumps, load
from os.path import basename, join, dirname, realpath
from os import getcwd

DB_NAME = "gnom_db"
HELP_STRING = "Example call: python3 importDataset.py PATH/TO/JSON"
BASE_PATH_TO_IMPORT = "/flask-backend/data/import/"

__location__ = realpath(join(getcwd(), dirname(__file__)))


def loadDataset(datasets_path):
    # import validation schema
    print("Start validating json file inputs...")
    try:
        with open(join(__location__, "importValidationTemplate.json"), "r") as datasetValidationJson:
            schema = load(datasetValidationJson)
            datasetValidationJson.close()
    except Exception as err:
        print(f"Error loading json schema for validation:\n{err}")
        return 0

    # open dataset file
    try:
        with open(datasets_path, "r") as datasets_json:
            datasets = load(datasets_json)
            datasets_json.close()
    except Exception as err:
        print(f"Error opening dataset file:\n{err}")
        return 0

    # validate dataset file
    try:
        validate(datasets, schema)
    except Exception as err:
        print(f"ValidationError:\n{err}")
        return 0

    print("Valid inputs...")

    try:
        with open(join(__location__, "../../local.config")) as config_file:
            config_params = config_file.readlines()
            config_file.close()

        config = {}
        for line in config_params:
            if "IMPORT_DIR" in line:
                config["IMPORT_DIR"] = line.split("=")[1].replace("\n", "")
            elif "API_CONTAINER_NAME" in line:
                config["API_CONTAINER_NAME"] = line.split("=")[1].replace("\n", "")
        status = importDatasets(datasets, config)
        return 1

    except Exception as err:
        print(f"Error loading config file:\n{err}")
        return 0


def importDatasets(datasets, config):
    uuid = str(uuid1())
    try:
        for idx, dataset in enumerate(datasets):
            print(f"Starting {idx+1}/{len(datasets)}")
            if "assemblyID" in dataset["assembly"] and dataset["assembly"]["assemblyID"] > 0:
                pass
            elif "mainFile" in dataset["assembly"] and exists(dataset["assembly"]["mainFile"]):
                pass
            else:
                print("Missing existing assembly ID or path to new assembly.fasta")
                return 0

            try:
                print("Gathering files in temporary folder...")

                tmp_dir = config["IMPORT_DIR"] + uuid + "/"

                run(args=["mkdir", "-p", tmp_dir])

                taxon = dumps(dataset["taxon"])

                # format assembly
                assemblyID = 0
                assembly_dataset = {}
                if "assemblyID" in dataset["assembly"]:
                    assemblyID = dataset["assembly"]["assemblyID"]
                elif "mainFile" in dataset["assembly"]:
                    if exists(dataset["assembly"]["mainFile"]):
                        run(args=["cp", "-r", dataset["assembly"]["mainFile"], tmp_dir])
                        assembly_dataset = {"main_file": {"path": f"{uuid}/" + basename(dataset["assembly"]["mainFile"])}}
                        if "label" in dataset["assembly"]:
                            assembly_dataset.update({"label": dataset["assembly"]["label"]})

                assembly = dumps([assembly_dataset])
                assemblyID = str(assemblyID)
            except Exception as err:
                print(f"Error identifying assembly! {str(err)}")
                continue

            # format annotations
            annotation_datasets = []
            if "annotations" in dataset:
                for idx_annotations, annotation in enumerate(dataset["annotations"]):
                    try:
                        if "mainFile" in annotation:
                            if exists(annotation["mainFile"]):
                                annotation_dataset = {}
                                tmp_dir_annotation = tmp_dir + f"annotation{idx_annotations+1}/"
                                run(args=["mkdir", "-p", tmp_dir_annotation])
                                run(args=["cp", "-r", annotation["mainFile"], tmp_dir_annotation])
                                annotation_dataset = {
                                    "main_file": {"path": f"{uuid}/annotation{idx_annotations+1}/" + basename(annotation["mainFile"])}
                                }
                                if "label" in annotation:
                                    annotation_dataset.update({"label": annotation["label"]})
                                annotation_datasets.append(annotation_dataset)
                            else:
                                print("Error: " + annotation["mainFile"] + " does not exist!")
                    except Exception as err:
                        number_annotations = len(dataset["annotations"])
                        print(f"Assembly {idx+1}/{len(datasets)}: Failed importing annotation {idx_annotations+1}/{len(number_annotations)}")
                        print(err)
            annotations = dumps(annotation_datasets)

            # format mappings
            mapping_datasets = []
            if "mappings" in dataset:
                for idx_mappings, mapping in enumerate(dataset["mappings"]):
                    try:
                        if "mainFile" in mapping:
                            if exists(mapping["mainFile"]):
                                mapping_dataset = {}
                                tmp_dir_mapping = tmp_dir + f"mapping{idx_mappings+1}/"
                                run(args=["mkdir", "-p", tmp_dir_mapping])
                                run(args=["cp", "-r", mapping["mainFile"], tmp_dir_mapping])
                                mapping_dataset = {"main_file": {"path": f"{uuid}/mapping{idx_mappings+1}/" + basename(mapping["mainFile"])}}
                                if "label" in mapping:
                                    mapping_dataset.update({"label": mapping["label"]})
                                mapping_datasets.append(mapping_dataset)
                            else:
                                print("Error: " + mapping["mainFile"] + " does not exist!")
                    except Exception as err:
                        number_mappings = len(dataset["mappings"])
                        print(f"Assembly {idx+1}/{len(datasets)}: Failed importing mapping {idx_mappings+1}/{len(number_mappings)}")
                        print(err)
            mappings = dumps(mapping_datasets)

            # format buscos
            busco_datasets = []
            if "buscos" in dataset:
                for idx_buscos, busco in enumerate(dataset["buscos"]):
                    try:
                        busco_dataset = {}
                        if "mainFile" in busco:
                            if exists(busco["mainFile"]):
                                tmp_dir_busco = tmp_dir + f"busco{idx_buscos+1}/"
                                run(args=["mkdir", "-p", tmp_dir_busco])
                                run(args=["cp", "-r", busco["mainFile"], tmp_dir_busco])
                                busco_dataset = {"main_file": {"path": f"{uuid}/busco{idx_buscos+1}/" + basename(busco["mainFile"])}}

                                if "additionalFiles" in busco:
                                    busco_additional_files = []
                                    for additional_file in busco["additionalFiles"]:
                                        run(args=["cp", "-r", additional_file, tmp_dir_busco])
                                        busco_additional_files.append(
                                            {"path": f"{uuid}/busco{idx_buscos+1}/" + basename(additional_file)}
                                        )
                                    busco_dataset.update({"additional_files": busco_additional_files})

                                if "label" in busco:
                                    busco_dataset.update({"label": busco["label"]})
                                busco_datasets.append(busco_dataset)
                            else:
                                print("Error: " + busco["mainFile"] + " does not exist!")
                    except Exception as err:
                        number_buscos = len(dataset["buscos"])
                        print(f"Assembly {idx+1}/{len(datasets)}: Failed importing busco {idx_buscos+1}/{len(number_buscos)}")
                        print(err)
            buscos = dumps(busco_datasets)

            # format fcats
            fcat_datasets = []
            if "fcats" in dataset:
                for idx_fcats, fcat in enumerate(dataset["fcats"]):
                    try:
                        fcat_dataset = {}
                        if "mainFile" in fcat:
                            if exists(fcat["mainFile"]):
                                tmp_dir_fcat = tmp_dir + f"fcat{idx_fcats+1}/"
                                run(args=["mkdir", "-p", tmp_dir_fcat])
                                run(args=["cp", "-r", fcat["mainFile"], tmp_dir_fcat])
                                fcat_dataset = {"main_file": {"path": f"{uuid}/fcat{idx_fcats+1}/" + basename(fcat["mainFile"])}}

                                if "additionalFiles" in fcat:
                                    fcat_additional_files = []
                                    for additional_file in fcat["additionalFiles"]:
                                        run(args=["cp", "-r", additional_file, tmp_dir_fcat])
                                        fcat_additional_files.append(
                                            {"path": f"{uuid}/fcat{idx_fcats+1}/" + basename(additional_file)}
                                        )
                                    fcat_dataset.update({"additional_files": fcat_additional_files})

                                    if "label" in fcat:
                                        fcat_dataset.update({"label": fcat["label"]})
                                fcat_datasets.append(fcat_dataset)
                            else:
                                print("Error: " + fcat["mainFile"] + " does not exist!")
                    except Exception as err:
                        number_fcats = len(dataset["fcats"])
                        print(f"Assembly {idx+1}/{len(datasets)}: Failed importing busco {idx_fcats+1}/{len(number_fcats)}")
                        print(err)
            fcats = dumps(fcat_datasets)

            # format milts
            milts_datasets = []
            if "milts" in dataset:
                for idx_milts, milt in enumerate(dataset["milts"]):
                    try:
                        milts_dataset = {}
                        if "mainFile" in milt:
                            if exists(milt["mainFile"]):
                                tmp_dir_milts = tmp_dir + f"milt{idx_milts+1}/"
                                run(args=["mkdir", "-p", tmp_dir_milts])
                                run(args=["cp", "-r", milt["mainFile"], tmp_dir_milts])
                                milts_dataset = {"main_file": {"path": f"{uuid}/milt{idx_milts+1}/" + basename(milt["mainFile"])}}

                                if "additionalFiles" in milt:
                                    milts_additional_files = []
                                    for additional_file in milt["additionalFiles"]:
                                        run(args=["cp", "-r", additional_file, tmp_dir_milts])
                                        milts_additional_files.append(
                                            {"path": f"{uuid}/milt{idx_milts+1}/" + basename(additional_file)}
                                        )
                                    milts_dataset.update({"additional_files": milts_additional_files})
                                    if "label" in milt:
                                        milts_dataset.update({"label": milt["label"]})
                                milts_datasets.append(milts_dataset)
                            else:
                                print("Error: " + milt["mainFile"] + " does not exist!")
                    except Exception as err:
                        number_milts = len(dataset["milts"])
                        print(f"Assembly {idx+1}/{len(datasets)}: Failed importing busco {idx_milts+1}/{len(number_milts)}")
                        print(err)
            milts = dumps(milts_datasets)

            # format repeatmaskers
            repeatmasker_datasets = []
            if "repeatmaskers" in dataset:
                for idx_repeatmaskers, repeatmasker in enumerate(dataset["repeatmaskers"]):
                    try:
                        repeatmasker_dataset = {}
                        if "mainFile" in repeatmasker:
                            if exists(repeatmasker["mainFile"]):
                                tmp_dir_repeatmasker = tmp_dir + f"repeatmasker{idx_repeatmaskers+1}/"
                                run(args=["mkdir", "-p", tmp_dir_repeatmasker])
                                run(args=["cp", "-r", repeatmasker["mainFile"], tmp_dir_repeatmasker])
                                repeatmasker_dataset = {
                                    "main_file": {"path": f"{uuid}/repeatmasker{idx_repeatmaskers+1}/" + basename(repeatmasker["mainFile"])}
                                }

                                if "additionalFiles" in repeatmasker:
                                    repeatmasker_additional_files = []
                                    for additional_file in repeatmasker["additionalFiles"]:
                                        run(args=["cp", "-r", additional_file, tmp_dir_repeatmasker])
                                        repeatmasker_additional_files.append(
                                            {"path": f"{uuid}/repeatmasker{idx_repeatmaskers+1}/" + basename(additional_file)}
                                        )
                                    repeatmasker_dataset.update({"additional_files": repeatmasker_additional_files})
                                if "label" in repeatmasker:
                                    repeatmasker_dataset.update({"label": repeatmasker["label"]})
                                repeatmasker_datasets.append(repeatmasker_dataset)
                            else:
                                print("Error: " + repeatmasker["mainFile"] + " does not exist!")
                    except Exception as err:
                        number_repeatmaskers = len(dataset["repeatmaskers"])
                        print(f"Assembly {idx+1}/{len(datasets)}: Failed importing busco {idx_repeatmaskers+1}/{len(number_repeatmaskers)}")
                        print(err)
            repeatmaskers = dumps(repeatmasker_datasets)

            run(
                args=[
                    "docker",
                    "exec",
                    "-w",
                    "/flask-backend/src",
                    "-it",
                    config["API_CONTAINER_NAME"],
                    "python3",
                    "-m",
                    "modules.combined_imports",
                    taxon,
                    assembly,
                    annotations,
                    mappings,
                    buscos,
                    fcats,
                    milts,
                    repeatmaskers,
                    assemblyID,
                ]
            )

            print("Removing tmp files...")
            run(args=["rm", "-r", tmp_dir])
            print(f"{idx+1}/{len(datasets)} imported!\n")
        return 1

    except Exception as err:
        print(f"Error copying files into import directory:\n{err}")
        print("Removing tmp files...")
        run(args=["rm", "-r", tmp_dir])
        return 0


if __name__ == "__main__":
    if len(argv) <= 1:
        print(HELP_STRING)
        exit(0)
    elif len(argv) > 2:
        print(HELP_STRING)
        exit(0)
    elif "-h" in argv or "--help" in argv:
        print(HELP_STRING)
        exit(0)

    path_to_dataset_json = str(argv[1])

    if not exists(path_to_dataset_json):
        raise FileNotFoundError("Invalid Filepath!")

    import_summary = loadDataset(path_to_dataset_json)

    exit(0)
