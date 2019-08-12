import csv
import io
import os
import copy
import random
import time
import pandas as pd


def writeTraceFile(traces, TRACE_FILE):
    if os.path.exists(TRACE_FILE):
        trace_file = open(TRACE_FILE, 'a+')
    else:
        trace_file = open(TRACE_FILE, 'w+')

    for test in traces:
        trace_file.write("#test#" + test.test_name + "\r\n")
        test_trace = test.trace
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


def insert_values_to_dict(dict_results, value_list):
    for value in value_list:
        key_value_pair = value.split(":")
        dict_results[key_value_pair[0]] += float(key_value_pair[1])
    dict_results['Version_count'] += float(1)


def get_string_from_dict(dict_result):
    auc = dict_result['auc']/dict_result['Version_count']
    acc = dict_result['acc']/dict_result['Version_count']
    tn = (dict_result['Tn']/dict_result['Total'])*100
    fn = (dict_result['Fn']/dict_result['Total'])*100
    tp = (dict_result['Tp']/dict_result['Total'])*100
    fp = (dict_result['Fp']/dict_result['Total'])*100
    return str(auc) + "," + str(acc) + "," + str(tn) + "%," + str(fp) + "%," + str(fn) + "%," + str(tp)+"%\n"


def calculate_prediction_results(version_path):
    learning_results_file_list = get_learning_results_files(version_path)
    nn_dict_results = {'acc':0,'auc':0,'Tn':0,'Fn':0,'Tp':0,'Fp':0,'Total':0,'Version_count':0}
    dnn_dict_results= {'acc':0,'auc':0,'Tn':0,'Fn':0,'Tp':0,'Fp':0,'Total':0,'Version_count':0}
    xgb_dict_results= {'acc':0,'auc':0,'Tn':0,'Fn':0,'Tp':0,'Fp':0,'Total':0,'Version_count':0}
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
    with open(os.path.join(version_path,"sum_learning_res.csv"), "w") as f:
        f.write("Algorithm,AUC,Acc,TN,FP,FN,TP\n")
        f.write("NN," + nn_s)
        f.write("DNN," + dnn_s)
        f.write("XGB," + xgb_s)


def get_learning_results_files(version_path):
    result = []
    proj_folders = [os.path.join(version_path, folder) for folder in os.listdir(version_path) if "fix" in folder]
    additional_folders = [os.path.join(proj_folder, "additionalFiles") for proj_folder in proj_folders
                          if r'additionalFiles' in os.listdir(proj_folder)]
    for add_folder in additional_folders:
        tmp_path = os.path.join(add_folder, "classifier_learning_results.csv")
        if os.path.exists(tmp_path):
            result.append(tmp_path)

    return result


def find_prev_classifier_version(ADDITIONAL_FILES_PATH, bug_id):
    tmp_add_file = ADDITIONAL_FILES_PATH
    for num in range((int(bug_id) - 1), 0, -1):
        tmp_add_file = tmp_add_file.replace(bug_id, str(num))
        if os.path.isfile(os.path.join(tmp_add_file, r"classifier_0.5.pkl")):
            return [os.path.join(tmp_add_file, f) for f in os.listdir(tmp_add_file) if f.endswith('.pkl')]
        else:
            tmp_add_file = tmp_add_file.replace(str(num), bug_id)

    return [os.path.join(ADDITIONAL_FILES_PATH, f) for f in os.listdir(tmp_add_file) if f.endswith('.pkl')]


if __name__ == '__main__':
    # prediction_input_file = r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_2_fix\additionalFiles\predictionInputToNN.csv'
    # partial_predicted_data(prediction_input_file)
    calculate_prediction_results(r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version')
    # diagnose_summary_results(r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\results.csv', r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\results_sum.csv')
    # print(find_prev_classifier_version(r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_6_fix
    # \additionalFiles', '6'))
    i = 9
