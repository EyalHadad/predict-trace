import csv
import io
import os
import copy
import random
import shutil
import time
import pandas as pd


def write_trace_file(traces, trace_file):
    if os.path.exists(trace_file):
        trace_file = open(trace_file, 'a+')
    else:
        trace_file = open(trace_file, 'w+')

    for test in traces:
        trace_file.write("#test#" + test.test_name + "\r\n")
        test_trace = test.trace
        trace_file.write("#trace#")
        for func in test_trace:
            trace_file.write(func + "@")
        trace_file.write("\r\n")

    trace_file.close()


def get_project_jar_path(project_version):
    dd = project_version
    from os import listdir
    from os.path import isfile, join
    only_files = [f for f in listdir(dd) if isfile(join(dd, f))]
    if len(only_files) > 0:
        for file in only_files:
            if file.endswith('.jar'):
                return os.path.join(project_version, file)


def insert_values_to_dict(dict_results, value_list):
    for value in value_list:
        key_value_pair = value.split(":")
        dict_results[key_value_pair[0]] += float(key_value_pair[1])
    dict_results['Version_count'] += float(1)


def get_string_from_dict(dict_result):
    auc = dict_result['auc'] / dict_result['Version_count']
    acc = dict_result['acc'] / dict_result['Version_count']
    tn = (dict_result['Tn'] / dict_result['Total']) * 100
    fn = (dict_result['Fn'] / dict_result['Total']) * 100
    tp = (dict_result['Tp'] / dict_result['Total']) * 100
    fp = (dict_result['Fp'] / dict_result['Total']) * 100
    return str(auc) + "," + str(acc) + "," + str(tn) + "%," + str(fp) + "%," + str(fn) + "%," + str(tp) + "%\n"


def calculate_prediction_results(version_path):
    learning_results_file_list = get_learning_results_files(version_path)
    nn_dict_results = {'acc': 0, 'auc': 0, 'Tn': 0, 'Fn': 0, 'Tp': 0, 'Fp': 0, 'Total': 0, 'Version_count': 0}
    dnn_dict_results = {'acc': 0, 'auc': 0, 'Tn': 0, 'Fn': 0, 'Tp': 0, 'Fp': 0, 'Total': 0, 'Version_count': 0}
    xgb_dict_results = {'acc': 0, 'auc': 0, 'Tn': 0, 'Fn': 0, 'Tp': 0, 'Fp': 0, 'Total': 0, 'Version_count': 0}
    # result_summary = old_sum_results(result)
    for res_file in learning_results_file_list:
        with open(res_file, "r") as f:
            file_content = f.readlines()
            for line in file_content:
                line = line.rstrip()
                algo_res_list = line.split(",")
                if algo_res_list[0] == 'NN':
                    insert_values_to_dict(nn_dict_results, algo_res_list[1:])
                elif algo_res_list[0] == 'DNN':
                    insert_values_to_dict(dnn_dict_results, algo_res_list[1:])
                else:
                    insert_values_to_dict(xgb_dict_results, algo_res_list[1:])
    nn_s = get_string_from_dict(nn_dict_results)
    dnn_s = get_string_from_dict(dnn_dict_results)
    xgb_s = get_string_from_dict(xgb_dict_results)
    with open(os.path.join(version_path, "sum_learning_res.csv"), "w") as f:
        f.write("Algorithm,AUC,Acc,TN,FP,FN,TP\n")
        f.write("NN," + nn_s)
        f.write("DNN," + dnn_s)
        f.write("XGB," + xgb_s)


def get_learning_results_files(version_path):
    result = []
    project_folders = [os.path.join(version_path, folder) for folder in os.listdir(version_path) if "fix" in folder]
    additional_folders = [os.path.join(proj_folder, "additionalFiles") for proj_folder in project_folders
                          if r'additionalFiles' in os.listdir(proj_folder)]
    for add_folder in additional_folders:
        tmp_path = os.path.join(add_folder, "classifier_learning_results.csv")
        if os.path.exists(tmp_path):
            result.append(tmp_path)

    return result


def find_prev_classifier_version(additional_files_path, bug_id):
    tmp_add_file = additional_files_path
    for num in range((int(bug_id) - 1), 0, -1):
        tmp_add_file = tmp_add_file.replace(bug_id, str(num))
        if os.path.isfile(os.path.join(tmp_add_file, r"classifier.pkl")):
            return os.path.join(tmp_add_file, r"classifier.pkl")
        else:
            tmp_add_file = tmp_add_file.replace(str(num), bug_id)
    if os.path.isfile(os.path.join(additional_files_path, r"classifier.pkl")):
        return os.path.join(additional_files_path, r"classifier.pkl")
    return ""


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
    # prediction_input_file = r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_2_fix\additionalFiles
    # \predictionInputToNN.csv' calculate_prediction_results(r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version')
    copy_traces(r'C:\Users\eyalhad\Desktop\copyTrace\Lang\lang_@_fix',
                r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\lang_@_fix\additionalFiles')
    # print(find_prev_classifier_version(r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_6_fix
