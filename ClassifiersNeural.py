import collections
import csv
import io
import sys
import time
import os
import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import warnings
from sklearn.metrics import accuracy_score  # works
from sklearn.metrics import roc_auc_score
import cPickle
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
from additional_functions import find_prev_classifier_version


def get_and_split_data_initial_data(input_file):
    start_time = time.time()
    dataset = pd.read_csv(input_file, usecols=list(range(2, 11)))
    dataset = dataset.dropna()
    elapsed_time = time.time() - start_time
    print("Total reading pandas time:" + str(elapsed_time))

    # ********************create classifier******************
    x = dataset.loc[:, 'PathLength':'FuncSim']
    y = dataset.loc[:, 'y']
    if len([ind for ind in dataset.index[dataset['PathExistence'] == 1]]) < 100:
        raise Exception('Not enough paths')

    return x, y


def split_data_and_get_best_classifier(x, y, classifier_perform_file):
    if os.path.isfile(classifier_perform_file):
        os.remove(classifier_perform_file)
    x_train, tmp_x_test, y_train, tmp_y_test = train_test_split(x, y, test_size=0.5)
    tmp_clf = train_classifier(x_train, y_train, tmp_x_test, tmp_y_test, classifier_perform_file)
    return tmp_clf


def train_classifier(x_train, y_train, x_test, y_test, classifier_perform_file):
    clf_slim = MLPClassifier(solver='adam', alpha=1e-5, activation='relu', max_iter=3000,
                             hidden_layer_sizes=30, random_state=13)
    clf_deep = MLPClassifier(solver='adam', alpha=1e-5, activation='relu', max_iter=3000,
                             hidden_layer_sizes=(30, 30, 30, 30, 30), random_state=13)
    xg_cls = xgb.XGBClassifier(objective='reg:linear', colsample_bytree=0.3, learning_rate=0.1,
                               max_depth=5, alpha=10, n_estimators=10)

    clf_slim.fit(x_train, y_train)
    xg_cls.fit(x_train, y_train)
    clf_deep.fit(x_train, y_train)

    save_classifier_results(clf_slim, x_test, y_test, classifier_perform_file, "NN")
    save_classifier_results(clf_deep, x_test, y_test, classifier_perform_file, "DNN")
    save_classifier_results(xg_cls, x_test, y_test, classifier_perform_file, "XGBoost")
    return clf_slim


def save_classifier_results(classifier, x_test, y_test, classifier_perform_file, classifier_type_name):
    y_pred = pd.DataFrame(classifier.predict(x_test))
    y_pred_proba = pd.DataFrame(np.delete(classifier.predict_proba(x_test), 0, 1))
    accuracy = accuracy_score(y_test, y_pred)
    auc_score = roc_auc_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    with open(classifier_perform_file, 'a+') as f:
        f.write(classifier_type_name + "," + "acc:" + str(accuracy) + "," + "auc:" + str(auc_score) + ","
                + "Tn:" + str(cm[0][0]) + "," + "Fn:" + str(cm[1][0]) + "," + "Tp:" + str(cm[1][1]) + "," + "Fp:" + str(
            cm[0][1]) + "," + "Total:" + str(cm[0][0]+cm[1][0]+cm[0][1]+cm[1][1]) + "\n")
    return y_pred_proba


def save_trained_classifiers_in_files(classifier_path_to_save, clf_to_save):
    # remove old classifiers
    additional_path = classifier_path_to_save[0:classifier_path_to_save.rindex("\\")]
    old_clf_to_remove = [os.path.join(additional_path, x) for x in os.listdir(additional_path) if ".pkl" in x]
    for clf_to_delete in old_clf_to_remove:
        os.remove(clf_to_delete)
    # save new classifiers
    with open(classifier_path_to_save, 'wb') as fid:
        print "----------Save Classifier--------------"
        cPickle.dump(clf_to_save, fid)


def partial_predicted_data(input_file, classifier_to_use, prediction_result_file):
    f = open(input_file)
    header = f.readline()
    data_to_predict = [header]
    cnt = 0
    end_of_test = 1
    old_test_name = 'tmp'
    for line in f:
        if line.split(",")[1] != old_test_name and end_of_test == 0:
            dataset = pd.read_csv(io.StringIO(u'\n'.join(data_to_predict)), delimiter=",")
            x = dataset.loc[:, 'PathLength':'FuncSim']
            y_prediction_probability = use_classifier(classifier_to_use, x)
            save_prediction_results(dataset['TestName'], dataset['FuncName'], dataset['y'], dataset['PathExistence'],
                                    y_prediction_probability, prediction_result_file)
            data_to_predict = [header]
            cnt = 0
        data_to_predict.append(line)
        old_test_name = line.split(",")[1]
        end_of_test = 0
        cnt = cnt + 1
    f.close()

def use_classifier(classifier_to_use, x):
    with open(classifier_to_use, 'rb') as fid:
        gnb_loaded = cPickle.load(fid)
    y_pred_proba = pd.DataFrame(np.delete(gnb_loaded.predict_proba(x), 0, 1), columns=["y_pred"])
    return y_pred_proba


def save_prediction_results(test_name, func_name, y, path_existence, y_prediction, prediction_result_file):
    y_prediction.index = test_name.index
    concat_data = pd.concat([test_name, func_name, y_prediction, y, path_existence], axis=1)
    largest_predicted_values = concat_data.nlargest(40, 'y_pred')
    function_in_the_trace = concat_data.loc[concat_data['y'] == 1]
    result_to_insert = pd.concat([largest_predicted_values, function_in_the_trace]).drop_duplicates().reset_index(
        drop=True)
    save_results_and_print_score(prediction_result_file, result_to_insert)


def save_results_and_print_score(output_result_file, result):
    with open(output_result_file, 'a') as f:
        result.to_csv(f, header=False, sep=',', encoding='utf-8', index=False)

def classify_code(bugID, training_input_file, prediction_input_file, classifier_path_to_save, prediction_result_file,
                  classifier_perform_file,
                  ADDITIONAL_FILES_PATH):
    print "----------Start Classifier Code--------------"
    # print "----------Training--------------"
    # warnings.filterwarnings("ignore")
    # start = time.time()
    # x, y = get_and_split_data_initial_data(training_input_file)
    # clf_to_save = split_data_and_get_best_classifier(x, y, classifier_perform_file)
    # save_trained_classifiers_in_files(classifier_path_to_save, clf_to_save)
    # elapsed = time.time() - start
    # print("Total training time: " + str(elapsed))

    # open the classifier of previous
    classifier_to_use = find_prev_classifier_version(ADDITIONAL_FILES_PATH, bugID)
    additional_path = classifier_path_to_save[0:classifier_path_to_save.rindex("\\")]
    old_score_to_remove = [os.path.join(additional_path, x) for x in os.listdir(additional_path) if "classifier_predictions.csv" in x]
    for clf_to_delete in old_score_to_remove:
        os.remove(clf_to_delete)
    partial_predicted_data(prediction_input_file, classifier_to_use, prediction_result_file)


if __name__ == '__main__':
    bug_id = '2'
    # r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_2_fix\additionalFiles\predictionInputToNN.csv'
    training_input_file = r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_2_fix\additionalFiles\predictionInputToNN.csv'
    prediction_input_file = r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_2_fix\additionalFiles\predictionInputToNN.csv'
    classifier_file = r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_2_fix\additionalFiles\classifier.pkl'
    output_file = r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_2_fix\additionalFiles\score_2.csv'
    preform_f = r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_2_fix\additionalFiles\classifier_score_2.txt'
    add_file = r'C:\Users\eyalhad\Desktop\runningProjects\Math_version\math_2_fix\additionalFiles'

    classify_code(bug_id, training_input_file, prediction_input_file, classifier_file, output_file, preform_f, add_file)
    arr = sys.argv

    if len(arr) == 2:
        argsEyal = arr[1]
        classify_code(argsEyal)
