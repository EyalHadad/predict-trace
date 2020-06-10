from configure_class import Configure, FilesAddress, RunConfigure
from mvnpy import Repo,use_repo
import traceback, subprocess, sys, os
from additional_functions import *
from function_diff import *
import ClassifiersNeural, sfl_diagnoser

conf = None
file_address = None


def set_log_files():
    if os.path.isfile(file_address.log_file):
        os.remove(file_address.log_file)
    if os.path.isfile(file_address.buggy_functions):
        os.remove(file_address.buggy_functions)
    if os.path.isfile(file_address.errors_file):
        os.remove(file_address.errors_file)
    with open(file_address.log_file, 'w+') as f:
        pass
    with open(file_address.buggy_functions, 'w+') as f:
        pass
    with open(file_address.errors_file, 'w+') as f:
        pass


def write_to_log(bug_id, func_name_list):
    with open(file_address.log_file, 'a+') as f:
        f.write("Bug Num:" + str(bug_id) + ",    " + str(func_name_list) + "\r\n")


def record_buggy_functions(bug_id, func_name_list):
    with open(file_address.buggy_functions, 'a+') as f:
        f.write("Bug Num:" + str(bug_id) + ",    " + str(func_name_list) + "\r\n")


def write_to_log_error(error, bug_num):
    if hasattr(error, 'strerror'):
        msg = str(error.strerror)
    else:
        msg = str(error.message)
    error_msg = bug_num + ": " + msg + "\n"
    print(error_msg)
    with open(file_address.errors_file, 'a+') as f:
        f.write(error_msg + "\r\n")


def run_diagnosis(run_conf):
    print("-----Bug Num: " + run_conf.bug_id + "-----")
    sfl_diagnoser.run_dignose_eyal(run_conf.bug_id, file_address.results_file, run_conf.additional_files_path)


def create_java_matrix(run_conf, func_name_list):
    with open(run_conf.error_file, 'w+'):
        pass
    print("-----Bug Num: " + run_conf.bug_id + "-----")
    p_create_matrix_txt = subprocess.Popen(
        ['java', '-cp', file_address.my_code_java_jar, 'createMatrixTxt', run_conf.bug_id, " ".join(func_name_list),
         run_conf.additional_files_path])
    p_create_matrix_txt.communicate()
    with open(run_conf.error_file, 'r') as f:
        java_error = f.read()
        if java_error == '1\n':
            write_to_log(run_conf.bug_id, func_name_list)
            raise NameError('Java create NN input error')


def run_classifier(run_conf):
    additional_path = run_conf.additional_files_path
    prediction_input_to_nn = os.path.join(additional_path, r"predictionInputToNNSeq.csv")
    training_input_to_nn = os.path.join(additional_path, r"predictionInputToNNSeq.csv")
    # training_input_to_nn = os.path.join(additional_path, r"trainingInputToNNSeq.csv")
    classifier_file = os.path.join(additional_path, r"classifier.pkl")
    output_file = os.path.join(additional_path, "score_" + run_conf.bug_id + ".csv")
    classifier_perform_file = os.path.join(additional_path, "classifier_learning_results.csv")
    print("-----Bug Num: " + run_conf.bug_id + "-----")
    ClassifiersNeural.classify_code(run_conf.bug_id, training_input_to_nn, prediction_input_to_nn, classifier_file,
                                    output_file, classifier_perform_file, additional_path)


def create_input_nn(run_conf, func_name_list):
    with open(run_conf.error_file, 'w+'):
        pass

    print("-----Bug Num: " + run_conf.bug_id + "-----")
    p_create_input_to_nn = subprocess.Popen(
        ['java', '-cp', file_address.my_code_java_jar, 'createInputToNN', run_conf.additional_files_path,
         " ".join(func_name_list), file_address.log_file, run_conf.bug_id])
    p_create_input_to_nn.communicate()

    with open(run_conf.error_file, 'r') as f:
        java_error = f.read()
        if java_error == '1\n':
            write_to_log(run_conf.bug_id, func_name_list)
            raise NameError('Java create NN input error')


def call_graph_creation(run_conf):
    call_graph_path = run_conf.project_dir + r'\additionalFiles\callGraph.txt'
    java_jar_ant = get_project_jar_path(run_conf)
    tests_jar = run_conf.project_dir + conf.clone_name + r'\tests.jar'
    # java_jar_ant.append(tests_jar)
    with open(call_graph_path, "w+") as f:
        for elem in java_jar_ant:
            p_create_cg = subprocess.Popen(['java', '-jar', file_address.call_graph_jar, elem], stdout=f)
            p_create_cg.communicate()


def tracer_and_parse(run_conf):
    # todo run Amir tracer
    repo = Repo.Repo(run_conf.project_dir + conf.clone_name)
    if not os.path.exists(file_address.debugger_tests_dir):
        os.makedirs(file_address.debugger_tests_dir)
    traces = repo.run_under_jcov(file_address.debugger_tests_dir, False)
    writeTraceFile(traces, run_conf.trace_file)


def mvn_dir_commands(run_conf):
    # if os.path.exists(run_conf.project_dir):
    #     os.system('rmdir /S /Q "{}"'.format(run_conf.project_dir))
    # os.makedirs(run_conf.additional_files_path)

    # todo clone and checkout
    # os.chdir(run_conf.project_dir)
    # os.system('git clone {0}'.format(conf.git_repo))
    # for folder_name in os.listdir(run_conf.project_dir):
    #     if "additionalFiles" not in folder_name:
    #         os.rename(folder_name, conf.clone_name[1:])
    os.chdir(run_conf.project_dir + conf.clone_name)
    # os.system('git checkout {0}'.format(run_conf.fix_version))
    # todo create project jar
    subprocess.Popen(['cmd', '/C', 'mvn clean']).wait()
    use_repo.add_jar_plugin(run_conf.pom_file)
    subprocess.Popen(['cmd', '/C', 'mvn install -fn']).wait()
    # subprocess.Popen(['cmd', '/C', 'mvn test']).communicate()
    # subprocess.Popen(
    #     ['jar', 'cvf', 'tests.jar', '-c', run_conf.project_dir + conf.clone_name + "\\target\\test-classes\\org"])


def run_prediction(bug_id, fix_version, bug_version,run_conf):
    if not os.path.exists(conf.root_dir):
        os.makedirs(conf.root_dir)
    print ("----------Bug num " + str(bug_id) + "---------------")
    # os.makedirs(run_conf.additional_files_path)
    # todo MVN and folders
    mvn_dir_commands(run_conf)
    # todo call graph
    # call_graph_creation(run_conf)

    # todo get function names
    # if not conf.need_patch:
    #     func_name_list = get_func_names(run_conf, file_address)
    # else:
    #     func_name_list = extract_buggy_functions(run_conf, conf)
    # if len(func_name_list) == 0:
    #     raise NameError('No buggy functions')
    # record_buggy_functions(bug_id, func_name_list)
    # # todo tracer_parsing
    # tracer_and_parse(run_conf)
    # # todo input_to_NN
    # create_input_nn(run_conf, func_name_list)
    #
    # # todo run the classifier code
    # run_classifier(run_conf)
    #
    # # todo run createMatrixTxt code
    # create_java_matrix(run_conf, func_name_list)
    #
    # # todo run_diagnosis
    # run_diagnosis(run_conf)


def read_commit_file():
    with open(conf.commit_database) as f:
        content = f.readlines()

    set_log_files()
    content = [x.strip() for x in content]
    for line_number, line in enumerate(content, start=conf.start_bug):
        split_content = line.split(',')
        bug_version = split_content[conf.bug_ind]
        fix_version = split_content[conf.fix_ind]
        if conf.start_bug <= line_number <= conf.end_bug:
            try:
                run_conf = RunConfigure(conf.root_dir, conf.project_name, conf.clone_name, line_number, fix_version,
                                        bug_version)
                if exists(run_conf.trace_file):
                    run_prediction(line_number, fix_version, bug_version,run_conf)
            except Exception as e:
                traceback.print_exc()
                write_to_log_error(e, str(line_number))


if __name__ == '__main__':
    if len(sys.argv) == 4:
        conf = Configure(sys.argv[1], sys.argv[2], sys.argv[3])
        file_address = FilesAddress(conf.root_dir)
        read_commit_file()
