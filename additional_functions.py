import csv
import io
import os
import copy
import random
import time
import pandas as pd
import shutil


def writeTraceFile(traces_dicionary, TRACE_FILE):
    if os.path.exists(TRACE_FILE):
        trace_file = open(TRACE_FILE, 'a+')
    else:
        trace_file = open(TRACE_FILE, 'w+')

    all_tests = traces_dicionary.keys()
    for test in all_tests:
        trace_file.write("#test#" + test + "\r\n")
        test_trace = traces_dicionary.get(test).trace
        trace_file.write("#trace#")
        for func in test_trace:
            trace_file.write(func + "@")
        trace_file.write("\r\n")

    trace_file.close()


def get_project_jar_path(PROJECT_VERSION):
    dd = PROJECT_VERSION
    from os import listdir
    from os.path import isfile, join
    only_files = [f for f in listdir(dd) if isfile(join(dd, f))]
    if len(only_files) > 0:
        for file in only_files:
            if file.endswith('.jar'):
                return os.path.join(PROJECT_VERSION, file)


def add_vectors(vector_to_add, sum_vector):
    if len(vector_to_add) == 0:
        return sum_vector
    float_vector_to_add = [float(i) for i in vector_to_add]
    tmp_vector = [x + y for x, y in zip(float_vector_to_add, sum_vector)]
    return tmp_vector


# don't use right now
def diagnose_summary_results(RESULTS_FILE, SUM_RESULTS_FILE):
    number_of_bugs = 0
    amir_precision = [0] * 150
    amir_recall = [0] * 150
    eyal_precision = [0] * 150
    eyal_recall = [0] * 150
    random_precision = [0] * 150
    random_recall = [0] * 150
    amir_precision = [float(i) for i in amir_precision]
    amir_recall = [float(i) for i in amir_recall]
    eyal_precision = [float(i) for i in eyal_precision]
    eyal_recall = [float(i) for i in eyal_recall]
    random_precision = [float(i) for i in random_precision]
    random_recall = [float(i) for i in random_recall]

    with open(RESULTS_FILE, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, quotechar='|')
        csv_list = list(spamreader)
    for i in range(1, len(csv_list), 1):
        if len(csv_list[i]) > 0 and "Bug" in csv_list[i][0]:
            number_of_bugs = number_of_bugs + 1
            amir_precision = add_vectors(csv_list[i + 3], amir_precision)
            amir_recall = add_vectors(csv_list[i + 5], amir_recall)
            eyal_precision = add_vectors(csv_list[i + 8], eyal_precision)
            eyal_recall = add_vectors(csv_list[i + 10], eyal_recall)
            random_precision = add_vectors(csv_list[i + 13], random_precision)
            random_recall = add_vectors(csv_list[i + 15], random_recall)
            i = i + 15
        # print csv_list[i]

    amir_precision = [x / number_of_bugs for x in amir_precision]
    amir_recall = [x / number_of_bugs for x in amir_recall]
    eyal_precision = [x / number_of_bugs for x in eyal_precision]
    eyal_recall = [x / number_of_bugs for x in eyal_recall]
    random_precision = [x / number_of_bugs for x in random_precision]
    random_recall = [x / number_of_bugs for x in random_recall]
    with open(SUM_RESULTS_FILE, 'wb') as f:
        f.write("amir_precision\n")
        f.write(str(amir_precision))
        f.write("\neyal_precision\n")
        f.write(str(eyal_precision))
        f.write("\nrandom_precision\n")
        f.write(str(random_precision))

        f.write("\namir_recall\n")
        f.write(str(amir_recall))
        f.write("\neyal_recall\n")
        f.write(str(eyal_recall))
        f.write("\nrandom_recall\n")
        f.write(str(random_recall))


def calculate_prediction_results(PATH):
    result = []
    proj_folders = [os.path.join(PATH, folder) for folder in os.listdir(PATH) if "fix" in folder]
    additional_folders = [os.path.join(proj_folder, "additionalFiles") for proj_folder in proj_folders
                          if r'additionalFiles' in os.listdir(proj_folder)]
    for add_folder in additional_folders:
        tmp_res = [os.path.join(add_folder, file) for file in os.listdir(add_folder)
                   if "classifier_score" in file]
        if len(tmp_res) > 0:
            result.append(tmp_res)
    res_file_name = os.path.join(PATH, r'classifier_sum_res_lang_deep.csv')
    res_file = open(res_file_name, 'w+')
    res_file.write("Bug Num,AUC,Acc,Tn,Fp,Fn,Tp\n")
    result_summary = old_sum_results(result, res_file)
    res_file.close()


def update_dict(res_dic, classifier, key):
    splited_lines = classifier[classifier.index("accuracy"):classifier.index("]]") + 2].split("\\r\\n")
    splited_lines[1] = splited_lines[1][splited_lines[1].index("auc"):]
    splited_lines[2] = splited_lines[2][splited_lines[2].index("confusion_matrix:"):]
    acc = float(splited_lines[0].split(":")[1])
    auc = float(splited_lines[1].split(":")[1])
    conf_mat = splited_lines[2].split("\\n")
    tn, fp = map(float, filter(None, conf_mat[0].split("[[")[1].split("]")[0].split(" ")))
    fn, tp = map(float, filter(None, conf_mat[1].split("[")[1].split("]]")[0].split(" ")))
    res_dic[key][1] = res_dic[key][1] + acc
    res_dic[key][3] = res_dic[key][3] + auc
    res_dic[key][5] = res_dic[key][5] + (tn / (tn + fp + fn + tp) * 100)
    res_dic[key][7] = res_dic[key][7] + (fp / (tn + fp + fn + tp) * 100)
    res_dic[key][9] = res_dic[key][9] + (fn / (tn + fp + fn + tp) * 100)
    res_dic[key][11] = res_dic[key][11] + (tp / (tn + fp + fn + tp) * 100)
    res_dic[key][13] = res_dic[key][13] + 1

    i = 8


def summarize_classifier_results(classification_score_files):
    sum_vector = ["acc:", 0, "auc:", 0, "tn:", 0, "fp:", 0, "fn:", 0, "tp:", 0, "count:", 0]
    # dict_keys = ['0.9_s', '0.9_d', '0.99_s', '0.99_d', '0.999_s', '0.999_d', '0.9999_s', '0.9999_d']
    res_dic = {"0.9_s": copy.copy(sum_vector), "0.9_d": copy.copy(sum_vector), "0.99_s": copy.copy(sum_vector),
               "0.99_d": copy.copy(sum_vector), "0.999_s": copy.copy(sum_vector), "0.999_d": copy.copy(sum_vector),
               "0.9999_s": copy.copy(sum_vector), "0.9999_d": copy.copy(sum_vector)}
    for classification_file in classification_score_files:
        with open(classification_file[0]) as f:
            content = f.readlines()
            content = str(content).split("----------------")[1:]
            for classifier, key in zip(content, res_dic.keys()):
                update_dict(res_dic, classifier[classifier.index("accuracy"):classifier.index("]]") + 2], key)
    for key in res_dic.keys():
        for i in range(1, 12, 2):
            res_dic[key][i] /= 114

    return res_dic


def old_sum_results(classification_score_files, res_file):
    sum_vector = ["acc:", 0, "auc:", 0, "tn:", 0, "fp:", 0, "fn:", 0, "tp:", 0, "count:", 0]
    for classification_file in classification_score_files:
        with open(classification_file[0]) as f:
            content = f.readlines()
            # content = content[11:]
            acc = float(content[17].split(":")[1])
            auc = float(content[18].split(":")[1])
            tn, fp = map(float, filter(None, content[19].split("[[")[1].split("]")[0].split(" ")))
            fn, tp = map(float, filter(None, content[20].split("[")[1].split("]]")[0].split(" ")))
            sum_vector[1] = sum_vector[1] + acc
            sum_vector[3] = sum_vector[3] + auc
            bug_num = classification_file[0].split("\\")[-1].split(".")[0].split("_")[-1]
            sum_vector[5] = sum_vector[5] + (tn / (tn + fp + fn + tp) * 100)
            sum_vector[7] = sum_vector[7] + (fp / (tn + fp + fn + tp) * 100)
            sum_vector[9] = sum_vector[9] + (fn / (tn + fp + fn + tp) * 100)
            sum_vector[11] = sum_vector[11] + (tp / (tn + fp + fn + tp) * 100)
            sum_vector[13] = sum_vector[13] + 1
            # with open(res_file) as rf:
            res_file.write(bug_num + "," + str(auc) + "," + str(acc) + "," + str(tn / (tn + fp + fn + tp) * 100)
                           + "%," + str(fp / (tn + fp + fn + tp) * 100) + "%," + str(fn / (tn + fp + fn + tp) * 100)
                           + "%," + str(tp / (tn + fp + fn + tp) * 100) + "%\n")

    return sum_vector


def find_prev_classifier_version(ADDITIONAL_FILES_PATH, bug_id):
    tmp_add_file = ADDITIONAL_FILES_PATH
    for num in range((int(bug_id) - 1), 0, -1):
        tmp_add_file = tmp_add_file.replace(bug_id, str(num))
        if os.path.isfile(os.path.join(tmp_add_file, r"classifier_0.5.pkl")):
            return [os.path.join(tmp_add_file, f) for f in os.listdir(tmp_add_file) if f.endswith('.pkl')]
        else:
            tmp_add_file = tmp_add_file.replace(str(num), bug_id)

    return [os.path.join(ADDITIONAL_FILES_PATH, f) for f in os.listdir(tmp_add_file) if f.endswith('.pkl')]

def copy_traces(source_path, dest_path):
    copy_conter = 0
    for num in range(141):
        new_source_path = source_path.replace("@", str(num))
        new_dest_path = dest_path.replace("@", str(num))
        if os.path.isdir(new_source_path) and os.path.isdir(new_dest_path):
            file_to_move = os.path.join(new_source_path, 'traceFile.txt')
            if os.path.exists(file_to_move):
                shutil.copy(file_to_move, new_dest_path)
                print(new_dest_path)
                copy_conter = copy_conter + 1

    print(str(copy_conter) + " file were copied")

if __name__ == '__main__':
    # prediction_input_file = r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_2_fix\additionalFiles\predictionInputToNN.csv'
    # partial_predicted_data(prediction_input_file)
    calculate_prediction_results(r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version')
    # copy_traces(r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\lang_@_fix\additionalFiles',
    #             r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version_2\lang_@_fix\additionalFiles')
    # diagnose_summary_results(r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\results.csv', r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\results_sum.csv')
    # print(find_prev_classifier_version(r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_6_fix
    # \additionalFiles', '6'))
    i = 9
