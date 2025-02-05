import csv
import os
from os.path import basename, exists, isdir, isfile
from subprocess import run
from re import sub, compile
from math import floor

from .notifications import createNotification
from .db_connection import connect, DB_NAME
from .environment import BASE_PATH_TO_IMPORT, BASE_PATH_TO_STORAGE
from .assemblies import addAssemblyTag, fetchAssemblyTagsByAssemblyID
from .files import scanFiles

import json

DIAMOND_FIELDS = fields = ['assemblyID', 'analysisID', 'qseqid', 'start', 'stop']

## ============================ IMPORT AND DELETE ============================ ##
# full import of analyses
def import_analyses(taxon, assembly_id, dataset, analyses_type, userID):
    """
    Import workflow for new analyses.
    """
    print("Start importing analyses...")
    try:
        if not taxon:
            return 0, createNotification(message="Missing taxon data!")

        if not assembly_id:
            return 0, createNotification(message="Missing assembly ID!")

        if not dataset or not dataset["main_file"] or not dataset["main_file"]["path"]:
            return 0, createNotification(message="Missing file path!")

        if not analyses_type:
            return 0, createNotification(message="Missing analyses type information!")

        if not userID:
            return 0, createNotification(message="Missing user ID!")

        connection, cursor, error = connect()
        cursor.execute(
            "SELECT assemblies.name FROM assemblies WHERE assemblies.id=%s",
            (assembly_id,),
        )
        assembly_name = cursor.fetchone()[0]

        analyses_name, analyses_id, error = __generate_analyses_name(assembly_name, analyses_type)
        if not analyses_id:
            print(error)
            return 0, error
    except Exception as err:
        print(f"An unknown error occured: {str(err)}")
        return 0, createNotification(message=f"AnalysesImportError{analyses_type}1: {str(err)}")

    try:
        if not analyses_name:
            print(error)
            return 0, error

        new_file_path, new_path_to_directory, error = __store_analyses(
            dataset, taxon, assembly_name, analyses_name, analyses_type
        )

        if not new_file_path or not exists(new_file_path):
            deleteAnalysesByAnalysesID(analyses_id)
            print(error)
            return 0, error

        if analyses_type == "busco":
            busco_content, error = parseBusco(new_file_path)
            if not busco_content:
                deleteAnalysesByAnalysesID(analyses_id)
                print(error)
                return 0, error
        elif analyses_type == "fcat":
            fcat_content, error = parseFcat(new_file_path)
            if not fcat_content:
                deleteAnalysesByAnalysesID(analyses_id)
                print(error)
                return 0, error
        elif analyses_type == "taxaminer":
            pass
        elif analyses_type == "repeatmasker":
            repeatmasker_content, error = parseRepeatmasker(new_file_path)
            if not repeatmasker_content:
                deleteAnalysesByAnalysesID(analyses_id)
                print(error)
                return 0, error
        else:
            return 0, createNotification(message=f"Invalid analyses type {analyses_type}")

        # zip
        if analyses_type != "taxaminer":
            tar_dir = new_path_to_directory[:-1] + ".tar.gz"
            run(args=["tar", "-zcf", tar_dir, new_path_to_directory])
            if not exists(tar_dir):
                deleteAnalysesByAnalysesID(analyses_id)
                return 0, createNotification(message=f"Compressing files failed")

            run(args=["rm", "-r", new_path_to_directory])
            new_file_path = tar_dir
        else:
            # unzip taxaminer data in directory
            run(["unzip", new_file_path, "-d", new_path_to_directory])

        import_status, error = __importAnalyses(
            analyses_id,
            assembly_id,
            analyses_name,
            new_file_path,
            analyses_type,
            userID,
        )
        if not import_status:
            deleteAnalysesByAnalysesID(analyses_id)
            print(error)
            return 0, error

        if analyses_type == "busco":
            import_status, error = __importBusco(assembly_id, analyses_id, busco_content)
        elif analyses_type == "fcat":
            import_status, error = __importFcat(assembly_id, analyses_id, fcat_content)
        elif analyses_type == "taxaminer":
            import_status, error = __importTaxaminer(assembly_id, analyses_id, new_path_to_directory)
        elif analyses_type == "repeatmasker":
            import_status, error = __importRepeatmasker(assembly_id, analyses_id, repeatmasker_content)
        else:
            import_status = 0
            error = createNotification(message="Unknown analyses type")

        if not import_status:
            deleteAnalysesByAnalysesID(analyses_id)
            print(error)
            return 0, error

        scanFiles()

        try:
            if "label" in dataset:
                updateAnalysisLabel(analyses_id, dataset["label"])
        except Exception as err:
            print(f"Change analysis label failed due to an error {str(err)}!")
            pass

        print(f"New analyses {analyses_name} ({analyses_type}) added!\n")
        return analyses_id, createNotification("Success", f"New annotation {analyses_name} added!", "success")
    except Exception as err:
        deleteAnalysesByAnalysesID(analyses_id)
        print(f"An unknown error occured: {str(err)}")
        return 0, createNotification(message=f"AnalysesImportError{analyses_type}2: {str(err)}")


# generate analyses name
def __generate_analyses_name(assembly_name, analyses_type):
    """
    Generates new analyses name.
    """
    try:
        connection, cursor, error = connect()
        cursor.execute(
            "SELECT MAX(id) FROM analyses"
        )
        auto_increment_counter = cursor.fetchone()[0]
        print(auto_increment_counter)

        if not auto_increment_counter:
            next_id = 1
        else:
            next_id = auto_increment_counter + 1

        # cursor.execute("ALTER TABLE analyses AUTO_INCREMENT = %s", (next_id + 1,))
        # connection.commit()
    except Exception as err:
        return 0, 0, createNotification(message=str(err))

    new_analyses_name = f"{assembly_name}_{analyses_type}_id{next_id}"

    return new_analyses_name, next_id, []


# moves .gff3 into storage
def __store_analyses(dataset, taxon, assembly_name, analyses_name, analyses_type, forceIdentical=False):
    """
    Moves analyses data to storage directory.
    """
    try:
        # check if path exists
        old_file_path = BASE_PATH_TO_IMPORT + dataset["main_file"]["path"]
        if not exists(old_file_path):
            return "", "", createNotification(message="Import path not found!")

        if old_file_path.lower().endswith(".gz"):
            run(["gunzip", "-q", old_file_path])

            if exists(old_file_path[:-3]):
                old_file_path = old_file_path[:-3]
            else:
                return "", "", createNotification(message="Unzipping of gff failed!")

        # # check if file exists already in db
        # if not forceIdentical:
        #     connection, cursor, error = connect()
        #     cursor.execute(f"SELECT id, name, path FROM genomicAnnotations WHERE assemblyID={assembly_id}")
        #     row_headers = [x[0] for x in cursor.description]
        #     annotation_paths = cursor.fetchall()
        #     annotation_paths = [dict(zip(row_headers, x)) for x in annotation_paths]

        # for file in annotation_paths:
        #     if cmp(old_file_path, file["path"]):
        #         same_annotation = file["name"]
        #         return 0, createNotification(message=f"New assembly seems to be identical to {same_annotation}")

        # move to storage
        scientificName = sub("[^a-zA-Z0-9_]", "_", taxon["scientificName"])
        new_file_path = (
            f"{BASE_PATH_TO_STORAGE}taxa/{scientificName}/{assembly_name}/analyses/{analyses_type}/{analyses_name}/"
        )
        run(["mkdir", "-p", new_file_path])
        if not isdir(new_file_path):
            return (
                "",
                "",
                createNotification(message="Creation of new directory failed!"),
            )

        if isfile(old_file_path):
            new_file_name = basename(old_file_path)
            new_file_path_main_file = f"{new_file_path}{new_file_name}"
            run(["cp", old_file_path, new_file_path_main_file])
        else:
            return "", "", createNotification(message="Invalid path to analyses file!")

        # check if main file was moved
        if not exists(new_file_path_main_file):
            return (
                "",
                "",
                createNotification(message="Moving analyses to storage failed!"),
            )
        # add remove?
        # handle additional files
        if "additional_files" in dataset:
            for additional_file in dataset["additional_files"]:
                old_additional_file_path = BASE_PATH_TO_IMPORT + additional_file["path"]
                if exists(old_additional_file_path):
                    run(["cp", "-r", old_additional_file_path, new_file_path])

        print(f"Analyses ({analyses_type}; {basename(new_file_path_main_file)}) moved to storage!")
        return new_file_path_main_file, new_file_path, []

    except Exception as err:
        return "", "", createNotification(message=f"AnalysesStorageError: {str(err)}")


# import Analyses
def __importAnalyses(analyses_id, assembly_id, analyses_name, analyses_path, analyses_type, userID):
    try:
        connection, cursor, error = connect()
        cursor.execute(
            "INSERT INTO analyses (id, assemblyID, name, type, path, addedBy, addedOn) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
            (
                analyses_id,
                assembly_id,
                analyses_name,
                analyses_type,
                analyses_path,
                userID,
            ),
        )
        connection.commit()
        return 1, []
    except Exception as err:
        return 0, createNotification(message=f"ImportAnalysesError: {str(err)}")


# update analysis label
def updateAnalysisLabel(analysis_id: int, label: str):
    """
    Set label for analyses.
    """
    try:
        connection, cursor, error = connect()

        LABEL_PATTERN = compile(r"^\w+$")

        if label and not LABEL_PATTERN.match(label):
            return 0, createNotification(message="Invalid label. Use only [a-zA-Z0-9_]!")
        elif not label:
            label = None

        cursor.execute(
            "UPDATE analyses SET label=%s WHERE id=%s",
            (label, analysis_id),
        )
        connection.commit()
        if label:
            return 1, createNotification("Success", f"Successfully added label: {label}", "success")
        else:
            return 1, createNotification("Info", f"Default name restored", "info")
    except Exception as err:
        return 0, createNotification(message=f"AnalysesLabelUpdateError: {str(err)}")


# import Busco
def __importBusco(assemblyID, analysisID, buscoData):
    """
    Imports Busco analysis results
    """
    try:
        notifications = []
        completeSingle = buscoData["completeSingle"]
        completeSinglePercent = buscoData["completeSinglePercent"]
        completeDuplicated = buscoData["completeDuplicated"]
        completeDuplicatedPercent = buscoData["completeDuplicatedPercent"]
        fragmented = buscoData["fragmented"]
        fragmentedPercent = buscoData["fragmentedPercent"]
        missing = buscoData["missing"]
        missingPercent = buscoData["missingPercent"]
        total = buscoData["total"]
        dataset = buscoData["dataset"]
        buscoMode = buscoData["buscoMode"]
        targetFile = buscoData["targetFile"]

        if total != completeSingle + completeDuplicated + fragmented + missing:
            return 0, createNotification(message="Busco total number does not match sum of all categories!")

        tags, fetchTagsNotifications = fetchAssemblyTagsByAssemblyID(assemblyID)
        tags = [x["tag"] for x in tags]

        if completeSinglePercent >= 50 and "BUSCO_COMPLETE_50" not in tags:
            tagAddedStatus, notification = addAssemblyTag(assemblyID, "BUSCO_COMPLETE_50")
            if not tagAddedStatus:
                notifications += notification
        if completeSinglePercent >= 75 and "BUSCO_COMPLETE_75" not in tags:
            tagAddedStatus, notification = addAssemblyTag(assemblyID, "BUSCO_COMPLETE_75")
            if not tagAddedStatus:
                notifications += notification
        if completeSinglePercent >= 90 and "BUSCO_COMPLETE_90" not in tags:
            tagAddedStatus, notification = addAssemblyTag(assemblyID, "BUSCO_COMPLETE_90")
            if not tagAddedStatus:
                notifications += notification

        connection, cursor, error = connect()
        cursor.execute(
            "INSERT INTO analysesBusco (analysisID, completeSingle, completeSinglePercent, completeDuplicated, completeDuplicatedPercent, fragmented, fragmentedPercent, missing, missingPercent, total, dataset, buscoMode, targetFile) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                analysisID,
                completeSingle,
                completeSinglePercent,
                completeDuplicated,
                completeDuplicatedPercent,
                fragmented,
                fragmentedPercent,
                missing,
                missingPercent,
                total,
                dataset,
                buscoMode,
                targetFile,
            ),
        )
        connection.commit()
        return 1, notifications

    except Exception as err:
        return 0, createNotification(message=f"BuscoImportDBError: {str(err)}")


# import fCat
def __importFcat(assemblyID, analysisID, fcatData):
    """
    Imports fCat analysis results
    """
    try:
        notifications = []

        tags, fetchTagsNotifications = fetchAssemblyTagsByAssemblyID(assemblyID)
        tags = [x["tag"] for x in tags]

        for mode in fcatData:
            if mode == "mode_1":
                m1_similar = fcatData[mode]["similar"]
                m1_similarPercent = fcatData[mode]["similarPercent"]
                m1_dissimilar = fcatData[mode]["dissimilar"]
                m1_dissimilarPercent = fcatData[mode]["dissimilarPercent"]
                m1_duplicated = fcatData[mode]["duplicated"]
                m1_duplicatedPercent = fcatData[mode]["duplicatedPercent"]
                m1_missing = fcatData[mode]["missing"]
                m1_missingPercent = fcatData[mode]["missingPercent"]
                m1_ignored = fcatData[mode]["ignored"]
                m1_ignoredPercent = fcatData[mode]["ignoredPercent"]
                m1_total = fcatData[mode]["total"]
                m1_genomeID = fcatData[mode]["genomeID"]

                if m1_similarPercent >= 50 and "FCAT_M1_SIMILAR_50" not in tags:
                    tagAddedStatus, notification = addAssemblyTag(assemblyID, "FCAT_M1_SIMILAR_50")
                    if not tagAddedStatus:
                        notifications += notification
                if m1_similarPercent >= 75 and "FCAT_M1_SIMILAR_75" not in tags:
                    tagAddedStatus, notification = addAssemblyTag(assemblyID, "FCAT_M1_SIMILAR_75")
                    if not tagAddedStatus:
                        notifications += notification
                if m1_similarPercent >= 90 and "FCAT_M1_SIMILAR_90" not in tags:
                    tagAddedStatus, notification = addAssemblyTag(assemblyID, "FCAT_M1_SIMILAR_90")
                    if not tagAddedStatus:
                        notifications += notification
            elif mode == "mode_2":
                m2_similar = fcatData[mode]["similar"]
                m2_similarPercent = fcatData[mode]["similarPercent"]
                m2_dissimilar = fcatData[mode]["dissimilar"]
                m2_dissimilarPercent = fcatData[mode]["dissimilarPercent"]
                m2_duplicated = fcatData[mode]["duplicated"]
                m2_duplicatedPercent = fcatData[mode]["duplicatedPercent"]
                m2_missing = fcatData[mode]["missing"]
                m2_missingPercent = fcatData[mode]["missingPercent"]
                m2_ignored = fcatData[mode]["ignored"]
                m2_ignoredPercent = fcatData[mode]["ignoredPercent"]
                m2_total = fcatData[mode]["total"]
                m2_genomeID = fcatData[mode]["genomeID"]

                if m2_similarPercent >= 50 and "FCAT_M2_SIMILAR_50" not in tags:
                    tagAddedStatus, notification = addAssemblyTag(assemblyID, f"FCAT_M2_SIMILAR_50")
                    if not tagAddedStatus:
                        notifications += notification
                if m2_similarPercent >= 75 and "FCAT_M2_SIMILAR_75" not in tags:
                    tagAddedStatus, notification = addAssemblyTag(assemblyID, f"FCAT_M2_SIMILAR_75")
                    if not tagAddedStatus:
                        notifications += notification
                if m2_similarPercent >= 90 and "FCAT_M2_SIMILAR_90" not in tags:
                    tagAddedStatus, notification = addAssemblyTag(assemblyID, f"FCAT_M2_SIMILAR_90")
                    if not tagAddedStatus:
                        notifications += notification
            elif mode == "mode_3":
                m3_similar = fcatData[mode]["similar"]
                m3_similarPercent = fcatData[mode]["similarPercent"]
                m3_dissimilar = fcatData[mode]["dissimilar"]
                m3_dissimilarPercent = fcatData[mode]["dissimilarPercent"]
                m3_duplicated = fcatData[mode]["duplicated"]
                m3_duplicatedPercent = fcatData[mode]["duplicatedPercent"]
                m3_missing = fcatData[mode]["missing"]
                m3_missingPercent = fcatData[mode]["missingPercent"]
                m3_ignored = fcatData[mode]["ignored"]
                m3_ignoredPercent = fcatData[mode]["ignoredPercent"]
                m3_total = fcatData[mode]["total"]
                m3_genomeID = fcatData[mode]["genomeID"]

                if m3_similarPercent >= 50 and "FCAT_M3_SIMILAR_50" not in tags:
                    tagAddedStatus, notification = addAssemblyTag(assemblyID, f"FCAT_M3_SIMILAR_50")
                    if not tagAddedStatus:
                        notifications += notification
                if m3_similarPercent >= 75 and "FCAT_M3_SIMILAR_75" not in tags:
                    tagAddedStatus, notification = addAssemblyTag(assemblyID, f"FCAT_M3_SIMILAR_75")
                    if not tagAddedStatus:
                        notifications += notification
                if m3_similarPercent >= 90 and "FCAT_M3_SIMILAR_90" not in tags:
                    tagAddedStatus, notification = addAssemblyTag(assemblyID, f"FCAT_M3_SIMILAR_90")
                    if not tagAddedStatus:
                        notifications += notification
            elif mode == "mode_4":
                m4_similar = fcatData[mode]["similar"]
                m4_similarPercent = fcatData[mode]["similarPercent"]
                m4_dissimilar = fcatData[mode]["dissimilar"]
                m4_dissimilarPercent = fcatData[mode]["dissimilarPercent"]
                m4_duplicated = fcatData[mode]["duplicated"]
                m4_duplicatedPercent = fcatData[mode]["duplicatedPercent"]
                m4_missing = fcatData[mode]["missing"]
                m4_missingPercent = fcatData[mode]["missingPercent"]
                m4_ignored = fcatData[mode]["ignored"]
                m4_ignoredPercent = fcatData[mode]["ignoredPercent"]
                m4_total = fcatData[mode]["total"]
                m4_genomeID = fcatData[mode]["genomeID"]

                if m4_similarPercent >= 50 and "FCAT_M4_SIMILAR_50" not in tags:
                    tagAddedStatus, notification = addAssemblyTag(assemblyID, f"FCAT_M4_SIMILAR_50")
                    if not tagAddedStatus:
                        notifications += notification
                if m4_similarPercent >= 75 and "FCAT_M4_SIMILAR_75" not in tags:
                    tagAddedStatus, notification = addAssemblyTag(assemblyID, f"FCAT_M4_SIMILAR_75")
                    if not tagAddedStatus:
                        notifications += notification
                if m4_similarPercent >= 90 and "FCAT_M4_SIMILAR_90" not in tags:
                    tagAddedStatus, notification = addAssemblyTag(assemblyID, f"FCAT_M4_SIMILAR_90")
                    if not tagAddedStatus:
                        notifications += notification

        connection, cursor, error = connect()
        cursor.execute(
            "INSERT INTO analysesFcat (analysisID, m1_similar, m1_similarPercent, m1_dissimilar, m1_dissimilarPercent, m1_duplicated, m1_duplicatedPercent, m1_missing, m1_missingPercent, m1_ignored, m1_ignoredPercent, m2_similar, m2_similarPercent, m2_dissimilar, m2_dissimilarPercent, m2_duplicated, m2_duplicatedPercent, m2_missing, m2_missingPercent, m2_ignored, m2_ignoredPercent, m3_similar, m3_similarPercent, m3_dissimilar, m3_dissimilarPercent, m3_duplicated, m3_duplicatedPercent, m3_missing, m3_missingPercent, m3_ignored, m3_ignoredPercent, m4_similar, m4_similarPercent, m4_dissimilar, m4_dissimilarPercent, m4_duplicated, m4_duplicatedPercent, m4_missing, m4_missingPercent, m4_ignored, m4_ignoredPercent, total, genomeID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                analysisID,
                m1_similar,
                m1_similarPercent,
                m1_dissimilar,
                m1_dissimilarPercent,
                m1_duplicated,
                m1_duplicatedPercent,
                m1_missing,
                m1_missingPercent,
                m1_ignored,
                m1_ignoredPercent,
                m2_similar,
                m2_similarPercent,
                m2_dissimilar,
                m2_dissimilarPercent,
                m2_duplicated,
                m2_duplicatedPercent,
                m2_missing,
                m2_missingPercent,
                m2_ignored,
                m2_ignoredPercent,
                m3_similar,
                m3_similarPercent,
                m3_dissimilar,
                m3_dissimilarPercent,
                m3_duplicated,
                m3_duplicatedPercent,
                m3_missing,
                m3_missingPercent,
                m3_ignored,
                m3_ignoredPercent,
                m4_similar,
                m4_similarPercent,
                m4_dissimilar,
                m4_dissimilarPercent,
                m4_duplicated,
                m4_duplicatedPercent,
                m4_missing,
                m4_missingPercent,
                m4_ignored,
                m4_ignoredPercent,
                m1_total,
                m1_genomeID,
            ),
        )
        connection.commit()
        return 1, notifications

    except Exception as err:
        return 0, createNotification(message=f"FcatImportDBError; {str(err)}")


# import taXaminer
def __importTaxaminer(assemblyID, analysisID, base_path):
    try:
        connection, cursor, error = connect()
        cursor.execute("INSERT INTO analysesTaxaminer (analysisID) VALUES (%s)", (analysisID,))
        connection.commit()

        # Load taxonomic hits
        diamond_path = base_path + "taxonomic_hits.txt"
        print(diamond_path)
        if not os.path.isfile(diamond_path):
            return 0, createNotification(message=f"taXaminerImportDBError: Diamond data is missing!")

        # build data rows
        # => save assemblyID, analysisID, qseqID together with the row number to index file
        sql_rows = []
        with open(diamond_path) as file:
            start_index = 0
            curr_id = ""
            outer_index = 0
            for i, line in enumerate(file.readlines()):
                # primer
                if i == 0:
                    curr_id = line.split("\t")[0]
                
                # determine new id
                next_id = line.split("\t")[0]
                if next_id != curr_id:
                    # start -> stop
                    sql_rows.append((assemblyID, analysisID, curr_id, start_index, i-1))
                    curr_id = next_id
                    start_index = i
                outer_index = i
            
            # final row
            sql_rows.append((assemblyID, analysisID, curr_id, start_index, outer_index))
        
        connection, cursor, error = connect()
        cursor.executemany("INSERT INTO taxaminerDiamond (assemblyID, analysisID, qseqID, start, stop) VALUES (%s, %s, %s, %s, %s)", sql_rows)
        connection.commit()

        return 1, []
    except Exception as err:
        return 0, createNotification(message=f"taXaminerImportDBError: {str(err)}")


# import Repeatmasker
def __importRepeatmasker(assemblyID, analysisID, repeatmaskerData):
    """
    Imports Repeatmasker analysis results
    """
    notifications = []

    if "sines" in repeatmaskerData:
        sines = repeatmaskerData["sines"]
    if "sines_length" in repeatmaskerData:
        sines_length = repeatmaskerData["sines_length"]
    if "lines" in repeatmaskerData:
        lines = repeatmaskerData["lines"]
    if "lines_length" in repeatmaskerData:
        lines_length = repeatmaskerData["lines_length"]
    if "ltr_elements" in repeatmaskerData:
        ltr_elements = repeatmaskerData["ltr_elements"]
    if "ltr_elements_length" in repeatmaskerData:
        ltr_elements_length = repeatmaskerData["ltr_elements_length"]
    if "dna_elements" in repeatmaskerData:
        dna_elements = repeatmaskerData["dna_elements"]
    if "dna_elements_length" in repeatmaskerData:
        dna_elements_length = repeatmaskerData["dna_elements_length"]
    if "rolling_circles" in repeatmaskerData:
        rolling_circles = repeatmaskerData["rolling_circles"]
    if "rolling_circles_length" in repeatmaskerData:
        rolling_circles_length = repeatmaskerData["rolling_circles_length"]
    if "unclassified" in repeatmaskerData:
        unclassified = repeatmaskerData["unclassified"]
    if "unclassified_length" in repeatmaskerData:
        unclassified_length = repeatmaskerData["unclassified_length"]
    if "small_rna" in repeatmaskerData:
        small_rna = repeatmaskerData["small_rna"]
    if "small_rna_length" in repeatmaskerData:
        small_rna_length = repeatmaskerData["small_rna_length"]
    if "satellites" in repeatmaskerData:
        satellites = repeatmaskerData["satellites"]
    if "satellites_length" in repeatmaskerData:
        satellites_length = repeatmaskerData["satellites_length"]
    if "simple_repeats" in repeatmaskerData:
        simple_repeats = repeatmaskerData["simple_repeats"]
    if "simple_repeats_length" in repeatmaskerData:
        simple_repeats_length = repeatmaskerData["simple_repeats_length"]
    if "low_complexity" in repeatmaskerData:
        low_complexity = repeatmaskerData["low_complexity"]
    if "low_complexity_length" in repeatmaskerData:
        low_complexity_length = repeatmaskerData["low_complexity_length"]
    if "total_non_repetitive_length" in repeatmaskerData:
        total_non_repetitive_length = repeatmaskerData["total_non_repetitive_length"]
    if "total_repetitive_length" in repeatmaskerData:
        total_repetitive_length = repeatmaskerData["total_repetitive_length"]
    if "numberN" in repeatmaskerData:
        numberN = repeatmaskerData["numberN"]
    if "percentN" in repeatmaskerData:
        percentN = repeatmaskerData["percentN"]

    try:
        repetitiveness = total_repetitive_length * 100 / (total_non_repetitive_length + total_repetitive_length)

        tags, fetchTagsNotifications = fetchAssemblyTagsByAssemblyID(assemblyID)
        tags = [x["tag"] for x in tags]

        if repetitiveness >= 50 and "REPETITIVENESS_50" not in tags:
            tagAddedStatus, notification = addAssemblyTag(assemblyID, "REPETITIVENESS_50")
            if not tagAddedStatus:
                notifications += notification
        if repetitiveness >= 75 and "REPETITIVENESS_75" not in tags:
            tagAddedStatus, notification = addAssemblyTag(assemblyID, "REPETITIVENESS_75")
            if not tagAddedStatus:
                notifications += notification
        if repetitiveness >= 90 and "REPETITIVENESS_90" not in tags:
            tagAddedStatus, notification = addAssemblyTag(assemblyID, "REPETITIVENESS_90")
            if not tagAddedStatus:
                notifications += notification

        connection, cursor, error = connect()
        cursor.execute(
            "INSERT INTO analysesRepeatmasker (analysisID, sines, sines_length, `lines`, lines_length, ltr_elements, ltr_elements_length, dna_elements, dna_elements_length, unclassified, unclassified_length, rolling_circles, rolling_circles_length, small_rna, small_rna_length, satellites, satellites_length, simple_repeats, simple_repeats_length, low_complexity, low_complexity_length, total_non_repetitive_length_percent, total_non_repetitive_length, total_repetitive_length_percent, total_repetitive_length, numberN, percentN) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                analysisID,
                sines,
                sines_length,
                lines,
                lines_length,
                ltr_elements,
                ltr_elements_length,
                dna_elements,
                dna_elements_length,
                rolling_circles,
                rolling_circles_length,
                unclassified,
                unclassified_length,
                small_rna,
                small_rna_length,
                satellites,
                satellites_length,
                simple_repeats,
                simple_repeats_length,
                low_complexity,
                low_complexity_length,
                100 - repetitiveness,
                total_non_repetitive_length,
                repetitiveness,
                total_repetitive_length,
                numberN,
                percentN,
            ),
        )
        connection.commit()
        return 1, []
    except Exception as err:
        return 0, createNotification(message=f"RepeatmaskerImportDBError: {str(err)}")


# fully deletes annotation by its ID
def deleteAnalysesByAnalysesID(analyses_id):
    """
    Deletes files and datatbase entry for specific analyses by analyses ID.
    """
    try:
        connection, cursor, error = connect()
        cursor.execute(
            "SELECT assemblies.id, assemblies.name, analyses.path, analyses.type FROM assemblies, analyses WHERE analyses.id=%s AND analyses.assemblyID=assemblies.id",
            (analyses_id,),
        )
        assembly_id, assembly_name, analyses_path, analysis_type = cursor.fetchone()

        cursor.execute(
            "SELECT taxa.* FROM assemblies, taxa WHERE assemblies.id=%s AND assemblies.taxonID=taxa.id",
            (assembly_id,),
        )

        row_headers = [x[0] for x in cursor.description]
        taxon = cursor.fetchone()
        taxon = dict(zip(row_headers, taxon))

        if analyses_id:
            status, error = __deleteAnalysesEntryByAnalysesID(analyses_id)

        if status and taxon and assembly_name and analyses_path:
            status, error = __deleteAnalysesFile(taxon, assembly_name, analyses_path, type=analysis_type)
        else:
            return 0, error

        if not status:
            return 0, error

        scanFiles()

        return 1, createNotification("Success", f"Successfully deleted anaylsis", "success")
    except Exception as err:
        return 0, createNotification(message=f"AnalysesDeletionError1: {str(err)}")


# deletes files for annotation
def __deleteAnalysesFile(taxon, assembly_name, analyses_path, type=""):
    """
    Deletes data for specific annotation.
    """
    try:
        scientificName = sub("[^a-zA-Z0-9_]", "_", taxon["scientificName"])
        path = f"{BASE_PATH_TO_STORAGE}taxa/{scientificName}"

        run(args=["rm", "-r", analyses_path])
        if type == "taxaminer":
            print("Analysis is taXaminer, deleting parent directory as well")
            # go one folder up
            taxaminer_folder = "/".join(analyses_path.split("/")[0:-1])
            run(args=["rm", "-r", taxaminer_folder])

        return 1, createNotification("Success", "Successfully deleted analyses", "success")
    except Exception as err:
        return 0, createNotification(message=f"AnalysesDeletionError2: {str(err)}")


def __deleteAnalysesEntryByAnalysesID(id):
    try:
        connection, cursor, error = connect()
        cursor.execute("DELETE FROM analyses WHERE id=%s", (id,))
        cursor.execute("DELETE FROM taxaminerDiamond WHERE analysisID=%s", (id,))
        connection.commit()
        return 1, []
    except Exception as err:
        return 0, createNotification(message=f"AnalysesDeletionError3: {str(err)}")


## ============================ PARSERS ============================ ##
# busco
def parseBusco(pathToBusco):
    """
    Extract data of busco analysis (short_summary.txt)
    """
    try:
        with open(pathToBusco, "r") as f:
            summaryData = f.readlines()
            f.close()

        FILE_PATTERN = compile(r"^.+\.\w+$")

        data = {}
        data["dataset"] = None
        data["targetFile"] = None
        data["buscoMode"] = None

        for line in summaryData:
            split = line.split()
            line = line.lower()
            if "(c)" in line:
                pass
            elif "(s)" in line:
                data["completeSingle"] = int(split[0])
            elif "(d)" in line:
                data["completeDuplicated"] = int(split[0])
            elif "(f)" in line:
                data["fragmented"] = int(split[0])
            elif "(m)" in line:
                data["missing"] = int(split[0])
            elif "total" in line:
                data["total"] = int(split[0])
            elif "_odb10" in line or "lineage dataset" in line:
                if "_odb10" in line:
                    for word in split:
                        if "_odb10" in word:
                            data["dataset"] = word
                            break
                elif ":" in line:
                    data["dataset"] = line.split(":")[1].split()[0]
            elif "notation for file" in line:
                for word in split:
                    if FILE_PATTERN.match(word):
                        data["targetFile"] = word.strip()
                        break
            elif "mode" in line:
                if ":" in line:
                    data["buscoMode"] = line.split(":")[1].split()[0]
                elif "genome" in line:
                    data["buscoMode"] = "genome"
                elif "protein" in line:
                    data["buscoMode"] = "proteins"
                elif "transcriptome" in line:
                    data["buscoMode"] = "transcriptome"

        data["completeSinglePercent"] = (data["completeSingle"] * 100) / data["total"]
        data["completeDuplicatedPercent"] = (data["completeDuplicated"] * 100) / data["total"]
        data["fragmentedPercent"] = (data["fragmented"] * 100) / data["total"]
        data["missingPercent"] = (data["missing"] * 100) / data["total"]

        if len(data.keys()):
            return data, []
        else:
            return 0, createNotification(message=f"{basename(pathToBusco)}: No data found!")

    except Exception as err:
        return 0, createNotification(message=f"BuscoParsingError: {str(err)}")


# fCat
def parseFcat(pathToFcat):
    """
    Extract data of fCat analysis (report_summary.txt)
    """
    try:
        with open(pathToFcat, "r") as f:
            summaryData = f.readlines()
            f.close()

        data = {}
        columns = [x.strip().replace("\n", "") for x in summaryData[0].split("\t")]

        for line in summaryData[1:]:
            values = line.split("\t")
            data[values[0]] = {}

            for index, value in enumerate(values[1:]):
                try:
                    data[values[0]][columns[index + 1]] = int(value)
                    data[values[0]][columns[index + 1] + "Percent"] = (int(value) * 100) / int(values[-1])
                except:
                    data[values[0]][columns[index + 1]] = str(value)

        if len(data.keys()):
            return data, []
        else:
            return 0, createNotification(message=f"{basename(pathToFcat)}: No data found!")
    except Exception as err:
        return 0, createNotification(message=f"FcatParsingError: {str(err)}")


# Repeatmasker
def parseRepeatmasker(pathToRepeatmasker):
    """
    Extract data of Repeatmasker analysis
    """
    try:
        with open(pathToRepeatmasker, "r") as f:
            summaryData = f.readlines()
            f.close()

        data = {}
        value_pattern = compile(r"[\d.]+ ")

        number_of_sequences = 0
        total_sequence_length = 0
        sequence_length = 0
        gc_level = 0.0
        data["numberN"] = 0
        data["percentN"] = 0.0

        data["sines"] = 0
        data["sines_length"] = 0
        data["lines"] = 0
        data["lines_length"] = 0
        data["ltr_elements"] = 0
        data["ltr_elements_length"] = 0
        data["dna_elements"] = 0
        data["dna_elements_length"] = 0
        data["unclassified"] = 0
        data["unclassified_length"] = 0
        total_interspersed_repeats = 0
        data["rolling_circles"] = 0
        data["rolling_circles_length"] = 0
        data["small_rna"] = 0
        data["small_rna_length"] = 0
        data["satellites"] = 0
        data["satellites_length"] = 0
        data["simple_repeats"] = 0
        data["simple_repeats_length"] = 0
        data["low_complexity"] = 0
        data["low_complexity_length"] = 0
        for line in summaryData:
            if line[0] == "=" or line[0] == "-":
                continue

            values = value_pattern.findall(line)
            values = [value.strip() for value in values]

            # header
            if len(values) == 0:
                continue
            elif "sequences" in line.lower():
                number_of_sequences = int(values[0])
                continue

            elif "total length" in line.lower():
                total_sequence_length = int(values[0])
                sequence_length = int(values[0])
                continue

            elif "gc level" in line.lower():
                gc_level = float(values[0])
                continue

            elif "bases masked" in line.lower():
                data["numberN"] = int(values[0])
                data["percentN"] = float(values[1])
                continue

            # body
            if "sines" in line.lower():
                length_occupied = int(values[1])
                data["sines"] = int(values[0])
                data["sines_length"] = length_occupied
                sequence_length -= length_occupied

            elif "lines" in line.lower():
                length_occupied = int(values[1])
                data["lines"] = int(values[0])
                data["lines_length"] = length_occupied
                sequence_length -= length_occupied

            elif "ltr elements" in line.lower():
                length_occupied = int(values[1])
                data["ltr_elements"] = int(values[0])
                data["ltr_elements_length"] = length_occupied
                sequence_length -= length_occupied

            elif "dna transposons" in line.lower() or "dna elements" in line.lower():
                length_occupied = int(values[1])
                data["dna_elements"] = int(values[0])
                data["dna_elements_length"] = length_occupied
                sequence_length -= length_occupied

            elif "unclassified" in line.lower():
                length_occupied = int(values[1])
                data["unclassified"] = int(values[0])
                data["unclassified_length"] = length_occupied
                sequence_length -= length_occupied

            elif "total interspersed repeats" in line.lower():
                total_interspersed_repeats = int(values[0])

            elif "rolling-circles" in line.lower():
                length_occupied = int(values[1])
                data["rolling_circles"] = int(values[0])
                data["rolling_circles_length"] = length_occupied
                sequence_length -= length_occupied

            elif "small rna" in line.lower():
                length_occupied = int(values[1])
                data["small_rna"] = int(values[0])
                data["small_rna_length"] = length_occupied
                sequence_length -= length_occupied

            elif "satellites" in line.lower():
                length_occupied = int(values[1])
                data["satellites"] = int(values[0])
                data["satellites_length"] = length_occupied
                sequence_length -= length_occupied

            elif "simple repeats" in line.lower():
                length_occupied = int(values[1])
                data["simple_repeats"] = int(values[0])
                data["simple_repeats_length"] = length_occupied
                sequence_length -= length_occupied

            elif "low complexity" in line.lower():
                length_occupied = int(values[1])
                data["low_complexity"] = int(values[0])
                data["low_complexity_length"] = length_occupied
                sequence_length -= length_occupied

        data["total_non_repetitive_length"] = sequence_length
        data["total_repetitive_length"] = total_sequence_length - sequence_length

        if len(data.keys()):
            return data, []
        else:
            return 0, createNotification(message=f"{basename(pathToRepeatmasker)}: No data found!")
    except Exception as err:
        return 0, createNotification(message=f"RepeatmaskerParsingError: {str(err)}")


## ============================ FETCH ============================ ##
# fetches all analyses for specific assembly
def fetchAnalysesByAssemblyID(assemblyID):
    """
    Fetches all analyses for specific assembly.
    """
    try:
        connection, cursor, error = connect()
        if error and error["message"]:
            return error

        analyses = {}

        # busco analyses
        cursor.execute(
            "SELECT analyses.*, analysesBusco.* FROM analyses, analysesBusco WHERE analyses.assemblyID=%s AND analyses.id=analysesBusco.analysisID",
            (assemblyID,),
        )
        row_headers = [x[0] for x in cursor.description]
        analyses["busco"] = [dict(zip(row_headers, x)) for x in cursor.fetchall()]

        # fcat analyses
        cursor.execute(
            "SELECT analyses.*, analysesFcat.* FROM analyses, analysesFcat WHERE analyses.assemblyID=%s AND analyses.id=analysesFcat.analysisID",
            (assemblyID,),
        )
        row_headers = [x[0] for x in cursor.description]
        analyses["fcat"] = [dict(zip(row_headers, x)) for x in cursor.fetchall()]

        # taXaminer analyses
        cursor.execute(
            "SELECT analyses.*, analysesTaxaminer.* FROM analyses, analysesTaxaminer WHERE analyses.assemblyID=%s AND analyses.id=analysesTaxaminer.analysisID",
            (assemblyID,),
        )
        row_headers = [x[0] for x in cursor.description]
        analyses["taxaminer"] = [dict(zip(row_headers, x)) for x in cursor.fetchall()]

        # repeatmasker analyses
        cursor.execute(
            "SELECT analyses.*, analysesRepeatmasker.* FROM analyses, analysesRepeatmasker WHERE analyses.assemblyID=%s AND analyses.id=analysesRepeatmasker.analysisID",
            (assemblyID,),
        )
        row_headers = [x[0] for x in cursor.description]
        analyses["repeatmasker"] = [dict(zip(row_headers, x)) for x in cursor.fetchall()]

        return analyses, []
    except Exception as err:
        return {}, createNotification(message=f"FetchAnalysesError: {str(err)}")


# fetches busco analyses for specific assembly
def fetchBuscoAnalysesByAssemblyID(assemblyID):
    """
    Fetches all busco analyses for specific assembly.
    """
    try:
        connection, cursor, error = connect()
        if error and error["message"]:
            return error

        # busco analyses
        cursor.execute(
            "SELECT analyses.*, analysesBusco.*, users.username FROM analyses, analysesBusco, users WHERE analyses.assemblyID=%s AND analyses.id=analysesBusco.analysisID AND analyses.addedBy=users.id",
            (assemblyID,),
        )
        row_headers = [x[0] for x in cursor.description]
        buscoList = [dict(zip(row_headers, x)) for x in cursor.fetchall()]

        # if not len(buscoList):
        #     return [], createNotification("Info", "No Busco analyses for this assembly", "info")

        return (
            buscoList,
            [],
        )
    except Exception as err:
        return [], createNotification(message=f"FetchBuscoAnalysesError: {str(err)}")


# fetches all analyses for specific assembly
def fetchFcatAnalysesByAssemblyID(assemblyID):
    """
    Fetches fCat analyses for specific assembly.
    """
    try:
        connection, cursor, error = connect()
        if error and error["message"]:
            return error

        # fcat analyses
        cursor.execute(
            "SELECT analyses.*, analysesFcat.*, users.username FROM analyses, analysesFcat, users WHERE analyses.assemblyID=%s AND analyses.id=analysesFcat.analysisID AND analyses.addedBy=users.id",
            (assemblyID,),
        )
        row_headers = [x[0] for x in cursor.description]
        fcatList = [dict(zip(row_headers, x)) for x in cursor.fetchall()]

        # if not len(fcatList):
        #     return [], createNotification("Info", "No fCat analyses for this assembly", "info")

        return (
            fcatList,
            [],
        )
    except Exception as err:
        return [], createNotification(message=f"FetchFcatAnalysesError: {str(err)}")


# fetches all analyses for specific assembly
def fetchTaXaminerAnalysesByAssemblyID(assemblyID):
    """
    Fetches all analyses for specific assembly.
    """
    try:
        connection, cursor, error = connect()
        if error and error["message"]:
            return error

        # taxaminer analyses
        cursor.execute(
            "SELECT analyses.*, analysesTaxaminer.*, users.username FROM analyses, analysesTaxaminer, users WHERE analyses.assemblyID=%s AND analyses.id=analysesTaxaminer.analysisID AND analyses.addedBy=users.id",
            (assemblyID,),
        )
        row_headers = [x[0] for x in cursor.description]
        taxaminerList = [dict(zip(row_headers, x)) for x in cursor.fetchall()]

        # if not len(taxaminerList):
        #     return [], createNotification("Info", "No taXaminer analyses for this assembly", "info")

        return (
            taxaminerList,
            [],
        )
    except Exception as err:
        return [], createNotification(message=f"FetchTaXaminerAnalysesError: {str(err)}")


# fetches all analyses for specific assembly
def fetchTaXaminerPathByAssemblyID_AnalysisID(assemblyID, taxaminerID):
    """
    Fetch the base path of a taxaminer analysis based on assembly and analysis ID
    """
    try:
        connection, cursor, error = connect()
        if error and error["message"]:
            return error

        # taxaminer analyses
        cursor.execute(
            "SELECT analyses.*, analysesTaxaminer.* FROM analyses, analysesTaxaminer WHERE analyses.assemblyID=%s AND analyses.id=analysesTaxaminer.analysisID AND analysesTaxaminer.id=%s;",
            (assemblyID, taxaminerID),
        )
        row_headers = [x[0] for x in cursor.description]
        taxaminerList = [dict(zip(row_headers, x)) for x in cursor.fetchall()]

        # if not len(taxaminerList):
        #     return [], createNotification("Info", "No taXaminer analyses for this assembly", "info")

        return (
            taxaminerList,
            [],
        )
    except Exception as err:
        return [], createNotification(message=f"FetchTaXaminerAnalysesError: {str(err)}")


# fetches all analyses for specific assembly
def fetchRepeatmaskerAnalysesByAssemblyID(assemblyID):
    """
    Fetches Repeatmasker analyses for specific assembly.
    """
    try:
        connection, cursor, error = connect()
        if error and error["message"]:
            return error

        # repeatmasker analyses
        cursor.execute(
            "SELECT analyses.*, analysesRepeatmasker.*, users.username FROM analyses, analysesRepeatmasker, users WHERE analyses.assemblyID=%s AND analyses.id=analysesRepeatmasker.analysisID AND analyses.addedBy=users.id",
            (assemblyID,),
        )
        row_headers = [x[0] for x in cursor.description]
        repeatmaskerList = [dict(zip(row_headers, x)) for x in cursor.fetchall()]

        # if not len(repeatmaskerList):
        #     return [], createNotification("Info", "No Repeatmasker analyses for this assembly", "info")

        return (
            repeatmaskerList,
            [],
        )
    except Exception as err:
        return [], createNotification(message=f"FetchRepeatmaskerAnalysesError: {str(err)}")


## ======================== FETCH ANALYSIS SPECIFIC ========================= ##
def fetchTaxaminerDiamond(assemblyID, analysisID, qseqid):
    try:
        connection, cursor, error = connect()
        cursor.execute("SELECT * FROM taxaminerDiamond, analysesTaxaminer WHERE taxaminerDiamond.analysisID=analysesTaxaminer.analysisID AND taxaminerDiamond.assemblyID=%s AND analysesTaxaminer.id=%s AND qseqID=%s",
        (assemblyID, analysisID, qseqid)
        )
        row = cursor.fetchone()

        # catch no entries
        if not row:
            return []
        
        temp_dict = dict()
        for i in range(0, 5):
            temp_dict[DIAMOND_FIELDS[i]] = row[i]

        return temp_dict
    except Exception as err:
        return 0, createNotification(message=str(err))

