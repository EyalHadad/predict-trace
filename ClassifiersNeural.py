import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import warnings
from sklearn.metrics import accuracy_score  # works
from sklearn.metrics import roc_auc_score
import sys
import cPickle
from sklearn.neural_network import MLPClassifier
import os
from additional_functions import *


def evaluate_classifier(classifier, x_test, y_test, classifier_perform_file, percentage, classifier_type_name, num_of_positive_in_train):
    y_pred = pd.DataFrame(classifier.predict(x_test))
    y_pred_proba = pd.DataFrame(np.delete(classifier.predict_proba(x_test), 0, 1))

    accuracy = accuracy_score(y_test, y_pred)
    auc_score = roc_auc_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    f = open(classifier_perform_file, 'a+')
    f.write("\r\n\r\n" + "----------------" + "\r\n\r\n" +"Test percentage: " + percentage + "\r\n" +
            classifier_type_name + "\r\n" + "accuracy:" + str(accuracy) + "\r\n" + "auc_score:" + str(auc_score) +
            "\r\n" + "confusion_matrix:" + str(cm) + "\r\n" + "Num of positive: " + num_of_positive_in_train + "\r\n")
    f.close()

    return y_pred_proba


def train_and_evaluate_classifier(x_train, y_train, x_test, y_test, prec, classifier_perform_file):
    clf_slim = MLPClassifier(solver='adam', alpha=1e-5, activation='relu', max_iter=3000,
                             hidden_layer_sizes=30, random_state=13)

    clf_deep = MLPClassifier(solver='adam', alpha=1e-5, activation='relu', max_iter=3000,
                             hidden_layer_sizes=(30, 30, 30, 30, 30), random_state=13)

    clf_slim.fit(x_train, y_train)
    clf_deep.fit(x_train, y_train)
    evaluate_classifier(clf_slim, x_test, y_test, classifier_perform_file, prec, "Slim classifier", str(y_train.values.sum()))
    evaluate_classifier(clf_deep, x_test, y_test, classifier_perform_file, prec, "Deep classifier", str(y_train.values.sum()))
    return clf_deep


def split_data_and_get_best_classifier(x, y, classifier_perform_file):
    loop_list = [("0.9999%", 0.9999), ("0.999%", 0.999), ("0.99%", 0.99), ("0.9", 0.9)]
    res = []
    tmp_clf = 0
    loop_list_test = [("0.99", 0.99)]
    for percentage, test_size_split in reversed(loop_list):
        x_train, tmp_x_test, y_train, tmp_y_test = train_test_split(x, y, test_size=test_size_split)
        res.append((percentage,len(y_train),y_train.values.sum()))
        tmp_clf = train_and_evaluate_classifier(x_train, y_train, tmp_x_test, tmp_y_test, percentage, classifier_perform_file)

    return tmp_clf



def esstimate_features(x, y, classifier_perform_file):
    for feature_num in range(0, 8):
        new_x = x.drop(x.columns[feature_num], axis=1)
        x_train, tmp_x_test, y_train, tmp_y_test = train_test_split(new_x, y, test_size=0.99)
        tmp_clf = train_and_evaluate_classifier(x_train, y_train, tmp_x_test, tmp_y_test, str(feature_num), classifier_perform_file)

    return tmp_clf


def classifyCode(bugID, input_file, classifier_path_to_save, output_file, classifier_perform_file,
                 ADDITIONAL_FILES_PATH):
    reload(sys)
    # sys.setdefaultencoding('utf8')
    print "----------Start Classifier Code--------------"
    warnings.filterwarnings("ignore")

    func_name, test_name, x, y = get_and_split_data_initial_data(input_file)

    # # just for testing
    # x_train, tmp_x_test, y_train, tmp_y_test = train_test_split(x, y, test_size=0.2)
    # clf_deep = MLPClassifier(solver='adam', alpha=1e-5, activation='relu', max_iter=3000,
    #                          hidden_layer_sizes=(30, 30, 30, 30, 30), random_state=13)
    # clf_deep.fit(x_train, y_train)
    # # y_prediction, y_prediction_probability = use_classifier(classifier_path_to_save, func_name, test_name, x, y)
    # evaluate_classifier(clf_deep, tmp_x_test, tmp_y_test, classifier_perform_file, 80%, "Deep classifier")

    # clf_to_save = esstimate_features(x, y, classifier_perform_file)
    clf_to_save = split_data_and_get_best_classifier(x, y, classifier_perform_file)

    with open(classifier_path_to_save, 'wb') as fid:
        print "----------Save Classifier--------------"
        cPickle.dump(clf_to_save, fid)

    # open the classifier of previous
    classifier_to_use = find_prev_classifier_version(ADDITIONAL_FILES_PATH, bugID)
    y_prediction, y_prediction_probability = use_classifier(classifier_to_use, func_name, test_name, x, y)
    result = pd.concat([test_name, func_name, y_prediction_probability, y]).sort_index(kind='merge')
    print "----------Create File Input_Diagnoser CSV--------------"
    save_results_and_print_score(output_file, result)


def use_classifier(previous_version_classifier, funcName, testName, x, y):
    with open(previous_version_classifier, 'rb') as fid:
        gnb_loaded = cPickle.load(fid)

    y_pred = pd.DataFrame(gnb_loaded.predict(x))
    y_pred_proba = pd.DataFrame(np.delete(gnb_loaded.predict_proba(x), 0, 1))

    y_pred_proba_csv = y_pred_proba

    testName.reset_index(drop=True, inplace=True)
    funcName.reset_index(drop=True, inplace=True)
    y_pred_proba_csv.reset_index(drop=True, inplace=True)
    y.reset_index(drop=True, inplace=True)
    testName.columns = ['value']
    funcName.columns = ['value']
    y_pred_proba_csv.columns = ['value']
    y.columns = ['value']
    return y_pred, y_pred_proba


def get_and_split_data_initial_data(input_file):
    dataset = pd.read_csv(input_file)
    # ********************create classifier******************
    data_length = len(dataset.columns)
    x_col = str(data_length - 2)
    # y_col = str(data_length-2)
    x = dataset.loc[:, '3':x_col]
    y = dataset.loc[:, '2':'2']
    testName = dataset.loc[:, '1':'1']
    funcName = dataset.loc[:, '0':'0']
    return funcName, testName, x, y


def save_results_and_print_score(output_file, result):
    if os.path.isfile(output_file):
        os.remove(output_file)
    result.to_csv(output_file, sep=' ', encoding='utf-8', index=False)

    i = 6


if __name__ == '__main__':
    # C:\Users\eyalhad\Desktop\runningProjects\Lang_version\lang_33_fix\additionalFiles
    bug_id = '33'
    input_file = r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\lang_33_fix\additionalFiles\inputToNNB.csv'
    classifier_file = r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\lang_33_fix\additionalFiles\classifier.pkl'
    output_file = r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\lang_33_fix\additionalFiles\score_33.csv'
    preform_f = r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\lang_33_fix\additionalFiles\classifier_score_33.txt'
    add_file = r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\lang_33_fix\additionalFiles'
    classifyCode(bug_id, input_file, classifier_file, output_file, preform_f, add_file)
    arr = sys.argv

    if len(arr) == 2:
        argsEyal = arr[1]
        classifyCode(argsEyal)
