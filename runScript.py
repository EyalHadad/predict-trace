from mvnpy import Repo
from additional_functions import *
import subprocess
import sys
import ClassifiersNeural
import sfl_diagnoser
import filediff
import git
import os
import time
import timeit
# # TODO project properties

ROOT_DIR = r'C:\Users\eyalhad\Desktop\runningProjects\Math_version'
CLONE_DIR = "\\defects4j-math"
PROJECT_NAME = "math"

# TODO project properties
# ROOT_DIR = r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version'
# CLONE_DIR = "\\BugMinerResults-lang"
# PROJECT_NAME = "lang"

# TODO JAVA code path
JAVA_CODE_DIR = r'C:\Users\eyalhad\Desktop\predict-trace\javaCode'
MY_CODE_JAVA_JAR = os.path.join(JAVA_CODE_DIR, r'target\uber-Code-1.0-SNAPSHOT.jar')

# TODO project files

RESULTS_FILE = ROOT_DIR + r'\results.csv'
SUM_RESULTS_FILE = ROOT_DIR + r'\sum_results.csv'
LOG_FILE = ROOT_DIR + r'\log.txt'
TIME_FILE = ROOT_DIR + r'\times.txt'
ERRORS_FILE = ROOT_DIR + r'\errors.txt'
DEBUGGER_TESTS_DIR = ROOT_DIR + r'\DebuggerTests'

# TODO additional files

CALL_GARPH_JAR = r'C:\Users\eyalhad\Desktop\predict-trace\additional_files\java-callgraph\target\javacg-0.1-SNAPSHOT-static.jar'
CHECKSTYLE_JAR = r'C:\Users\eyalhad\Desktop\predict-trace\additional_files\checkstyle-6.8-SNAPSHOT-all.jar'
METHOD_NAME_LINES_XML = r'C:\Users\eyalhad\Desktop\predict-trace\additional_files\methodNameLines.xml'


def run_diagnoser(ADDITIONAL_FILES_PATH, bug_id):
    print("-----Bug Num: " + str(bug_id) + "-----")
    start_t = timeit.default_timer()
    sfl_diagnoser.run_dignose_eyal(bug_id, RESULTS_FILE, ADDITIONAL_FILES_PATH)
    total_t = timeit.default_timer() - start_t
    writeToLogTime("Diagnoser " + str(total_t / 60) + "\r\n")


def createMatrixTxt_code(ADDITIONAL_FILES_PATH, bug_id, func_name_list):
    print("-----Bug Num: " + str(bug_id) + "-----")
    start_t = timeit.default_timer()
    pCreateMatrixTxt = subprocess.Popen(
        ['java', '-cp', MY_CODE_JAVA_JAR, 'createMatrixTxt', str(bug_id), " ".join(func_name_list),
         ADDITIONAL_FILES_PATH])
    pCreateMatrixTxt.communicate()
    total_t = timeit.default_timer() - start_t
    writeToLogTime("Create matrix: " + str(total_t / 60) + "\r\n")


def run_classifier(ADDITIONAL_FILES_PATH, bug_id):
    prediction_input_to_NN = os.path.join(ADDITIONAL_FILES_PATH, r"predictionInputToNN.csv")
    training_input_to_NN = os.path.join(ADDITIONAL_FILES_PATH, r"trainingInputToNN.csv")
    classifier_file = os.path.join(ADDITIONAL_FILES_PATH, r"classifier.pkl")
    output_file = os.path.join(ADDITIONAL_FILES_PATH, "score_" + bug_id + ".csv")
    classifier_perform_file = os.path.join(ADDITIONAL_FILES_PATH, "classifier_score_" + bug_id + ".txt")
    print("-----Bug Num: " + str(bug_id) + "-----")
    start_t = timeit.default_timer()
    ClassifiersNeural.classifyCode(bug_id, training_input_to_NN, prediction_input_to_NN, classifier_file, output_file,
                                   classifier_perform_file, ADDITIONAL_FILES_PATH)
    total_t = timeit.default_timer() - start_t
    writeToLogTime("Classifier " + str(total_t / 60) + "\r\n")


def create_input_NN(additional_files_path, bug_id, error_file, func_name_list):
    file = open(error_file, 'w+')
    file.close()
    print("-----Bug Num: " + str(bug_id) + "-----")
    start_t = timeit.default_timer()
    pCreateInputToNN = subprocess.Popen(
        ['java', '-cp', MY_CODE_JAVA_JAR, 'createInputToNN', additional_files_path,
         " ".join(func_name_list), LOG_FILE, str(bug_id)])
    pCreateInputToNN.communicate()
    total_t = timeit.default_timer() - start_t
    writeToLogTime("Input to NN: " + str(total_t / 60) + "\r\n")


def address_error_file(bug_id):
    PROJECT_VERSION = ROOT_DIR + "\\" + PROJECT_NAME + "_" + str(bug_id) + "_fix"
    ADDITIONAL_FILES_PATH = PROJECT_VERSION + r'\additionalFiles'
    DEBUGGER_TESTS_PATH = ADDITIONAL_FILES_PATH + r'\DebuggerTests'
    git_repo_local_path = PROJECT_VERSION + CLONE_DIR
    error_file = os.path.join(ADDITIONAL_FILES_PATH, r"errorFile.txt")
    trace_file = os.path.join(ADDITIONAL_FILES_PATH, r"traceFile.txt")
    return ADDITIONAL_FILES_PATH, DEBUGGER_TESTS_PATH, PROJECT_VERSION, error_file, git_repo_local_path, trace_file


def call_graph_creation(PROJECT_VERSION):
    CALL_GRAPH_PATH = PROJECT_VERSION + r'\additionalFiles\callGraph.txt'
    JAVA_JAR_ANT = get_project_jar_path(PROJECT_VERSION + CLONE_DIR + r'\target')
    TESTS_JAR = PROJECT_VERSION + CLONE_DIR + r'\tests.jar'

    with open(CALL_GRAPH_PATH, "w+") as f:
        pCreateCallGraph = subprocess.Popen(['java', '-jar', CALL_GARPH_JAR, JAVA_JAR_ANT, TESTS_JAR], stdout=f)
    pCreateCallGraph.communicate()
    return CALL_GRAPH_PATH


def tracer_and_parse(DEBUGGER_TESTS_PATH, PROJECT_VERSION, bug_id, bug_version, fix_version, git_repo_local_path,
                     trace_file):
    # todo run Amir tracer
    print("-----Bug Num: " + str(bug_id) + "-----")
    print("-----Start Tracer-----")
    # /////////////////////
    start_t = timeit.default_timer()
    repo = Repo.Repo(PROJECT_VERSION + CLONE_DIR)
    if not os.path.exists(DEBUGGER_TESTS_PATH):
        os.makedirs(DEBUGGER_TESTS_PATH)
    traces = repo.run_under_jcov(DEBUGGER_TESTS_PATH, False)
    writeTraceFile(traces, trace_file)
    total_t = timeit.default_timer() - start_t
    writeToLogTime("Tracer: " + str(total_t / 60) + "\r\n")


def mvn_dir_commands(PROJECT_VERSION, fix_version, git_repo_path):
    if os.path.exists(PROJECT_VERSION):
        os.system('rmdir /S /Q "{}"'.format(PROJECT_VERSION))
    os.makedirs(PROJECT_VERSION + "\\additionalFiles")

    # todo clone and checkout
    os.chdir(PROJECT_VERSION)
    os.system('git clone {0}'.format(git_repo_path))
    for folder_name in os.listdir(PROJECT_VERSION):
        if "additionalFiles" not in folder_name:
            os.rename(folder_name, CLONE_DIR[1:])
    os.chdir(PROJECT_VERSION + CLONE_DIR)
    os.system('git checkout {0}'.format(fix_version))
    # todo create project jar
    subprocess.Popen(['cmd', '/C', 'mvn clean']).communicate()
    subprocess.Popen(['cmd', '/C', 'mvn install -Dmaven.test.skip=true']).communicate()
    subprocess.Popen(['cmd', '/C', 'mvn test']).communicate()
    subprocess.Popen(
        ['jar', 'cvf', 'tests.jar', '-c', PROJECT_VERSION + CLONE_DIR + "\\target\\test-classes\\org"])


def get_class_from_line(line):
    tmp_line = line.split(" ")[0]
    tmp_line = tmp_line[tmp_line.find("src"):tmp_line.find(".java") + 5]
    tmp_line = tmp_line.replace("\\", "/")
    return tmp_line


def index_to_names(index_list, java_class, project_path, func_list):
    METHOD_LINES = os.path.join(project_path, r"method_lines.txt")
    with open(METHOD_LINES) as f:
        content = f.readlines()
    for line in content:
        str_class = get_class_from_line(line)
        if str_class.encode('UTF-8') == java_class:
            func_name = line.split(" ")[1].split("@")[0]
            first_num = int(line.split(" ")[1].split("@")[1])
            second_num = int(line.split(" ")[1].split("@")[2])
            for index in index_list:
                if first_num <= index <= second_num:
                    full_func_name = str_class[str_class.find("org"):str_class.find(".java")].replace("/",
                                                                                                      ".") + ":" + func_name
                    if full_func_name not in func_list:
                        func_list.append(full_func_name)
    return func_list


def method_name_xml(CHECKSTYLE_JAR, METHOD_NAME_LINES_XML, project_path):
    METHOD_LINES = os.path.join(project_path, r"method_lines.txt")
    with open(METHOD_LINES, "w+") as f:
        pCreateCallGarph = subprocess.Popen(
            ['java', '-jar', CHECKSTYLE_JAR, '-c', METHOD_NAME_LINES_XML, 'javaFile', project_path], stdout=f)
    pCreateCallGarph.communicate()


def fix_constuctor_names(func_names):
    new_func_names = []
    for tmp_name in func_names:
        if tmp_name.split(":")[0].split(".")[-1] == tmp_name.split(":")[1]:
            split_string = tmp_name.split(":")
            split_string[1] = "<init>"
            tmp_name = ":".join(split_string)
            # tmp_name = string.replace(tmp_name[0][::-1], tmp_name[0].split("@")[1][::-1], "<init>"[::-1], 1)[::-1]

        new_func_names.append(tmp_name)
    return new_func_names


def get_func_names(git_repo_local_path, bug_commit_number, fix_commit_number):
    repo = git.Repo(git_repo_local_path)
    commit_a = repo.commit(bug_commit_number)
    commit_b = repo.commit(fix_commit_number)
    diffs = map(filediff.FileDiff, commit_a.tree.diff(commit_b.tree))
    method_name_xml(CHECKSTYLE_JAR, METHOD_NAME_LINES_XML, git_repo_local_path)
    func_names = []
    for x in diffs:
        if x.file_name.endswith('.java') and "Test" not in x.file_name:
            if len(x.before_indices) > 0:
                index_to_names(x.before_indices, x.file_name, git_repo_local_path, func_names)

    return fix_constuctor_names(func_names)


def clear_log_files():
    if os.path.isfile(TIME_FILE):
        os.remove(TIME_FILE)
    if os.path.isfile(LOG_FILE):
        os.remove(LOG_FILE)
    if os.path.isfile(ERRORS_FILE):
        os.remove(ERRORS_FILE)


def writeToLog(bug_id, func_name_list):
    if os.path.exists(LOG_FILE):
        log_file = open(LOG_FILE, 'a+')
    else:
        log_file = open(LOG_FILE, 'w+')
    log_file.write("Bug Num:" + bug_id + ",    " + str(func_name_list) + "\r\n");
    log_file.close()


def writeToLogTime(msg):
    if os.path.exists(TIME_FILE):
        time_file = open(TIME_FILE, 'a+')
    else:
        time_file = open(TIME_FILE, 'w+')

    time_file.write(msg + "\r\n");
    time_file.close()


def writeToLogError(msg, bug_num):
    if os.path.exists(ERRORS_FILE):
        error_file = open(ERRORS_FILE, 'a+')
    else:
        error_file = open(ERRORS_FILE, 'w+')
    error_msg = bug_num + ": " + msg + "\n"
    error_file.write(error_msg + "\r\n")
    error_file.close()


def myFunc(bug_id, fix_version, bug_version, git_repo_path):
    if not os.path.exists(ROOT_DIR):
        os.makedirs(ROOT_DIR)
    total_start_time = timeit.default_timer()
    writeToLogTime("Bug" + str(bug_id) + ":" + "\r\n")
    print("-----Bug Num: " + str(bug_id) + "-----")

    # todo address_error_file
    ADDITIONAL_FILES_PATH, DEBUGGER_TESTS_PATH, PROJECT_VERSION, error_file, git_repo_local_path, trace_file = address_error_file(
        bug_id)

    # todo MVN and folders
    # mvn_dir_commands(PROJECT_VERSION, fix_version, git_repo_path)
    # todo call graph
    CALL_GARPH_PATH = call_graph_creation(PROJECT_VERSION)

    # todo get function names
    func_name_list = get_func_names(git_repo_local_path, bug_version, fix_version)
    if len(func_name_list) == 0:
        raise NameError('No buggy functions')
    # todo tracer_parsing
    # tracer_and_parse(DEBUGGER_TESTS_PATH, PROJECT_VERSION, bug_id, bug_version, fix_version,git_repo_local_path, trace_file)
    # todo input_to_NN
    create_input_NN(ADDITIONAL_FILES_PATH, bug_id, error_file, func_name_list)

    # todo check if error during create_input_NN
    file = open(error_file, 'r')
    res = file.read()
    file.close()
    if res == '1\n':
        writeToLog(bug_id, func_name_list)
        return 7

    # todo run the classifier code
    run_classifier(ADDITIONAL_FILES_PATH, bug_id)

    # todo run createMatrixTxt code

    # createMatrixTxt_code(ADDITIONAL_FILES_PATH, bug_id, func_name_list)

    # todo check if error during createMatrixTxt
    file = open(error_file, 'r')
    res = file.read()
    file.close()
    if res == '1\n':
        writeToLog(bug_id, func_name_list)
        return 7
    # todo run_ diagnoser
    # run_diagnoser(ADDITIONAL_FILES_PATH, bug_id)

    total_elapsed = timeit.default_timer() - total_start_time
    # writeToLogTime("Total Bug" + str(bug_id) + " time: " + str(total_elapsed / 60) + "\r\n")


def read_commit_file(commit_db, GIT_REPO_PATH, start_bug_num):
    black_list = [304]

    with open(commit_db) as f:
        content = f.readlines()

    if "BugMinerResults" in commit_db:
        content.pop(0)
    clear_log_files()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    line_number = 1
    content = [x.strip() for x in content]
    for line in content:
        split_content = line.split(',')
        old_bug_num = split_content[0]
        bug_num = str(line_number)
        line_number = line_number + 1
        if "BugMinerResults" in commit_db:
            bug_version = split_content[5]
            fix_version = split_content[4]
        else:
            bug_version = split_content[1]
            fix_version = split_content[2]
        if int(bug_num) not in black_list:
            if int(bug_num) >= int(start_bug_num):
                if int(bug_num) > 0 :
                    try:
                        myFunc(bug_num, fix_version, bug_version, GIT_REPO_PATH)
                    except Exception as e:
                        if hasattr(e, 'strerror'):
                            writeToLogError((str(e.strerror)), bug_num)
                            print(str(e.strerror))
                        else:
                            writeToLogError((str(e.message)), bug_num)
                            str(e.message)
                        pass


if __name__ == '__main__':
    if len(sys.argv) == 4:
        read_commit_file(sys.argv[1], sys.argv[2], sys.argv[3])
