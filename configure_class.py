import os


class Configure(object):
    def __init__(self, proj_name, commit_db, git_repo_path, start_bug_num, end_bug_num):
        self.commit_database = commit_db
        self.git_repo = git_repo_path
        self.start_bug = start_bug_num
        self.end_bug = end_bug_num
        self.proj_name = proj_name
        self.bug_ind = None
        self.fix_ind = None
        self.root_dir = None
        self.clone_name = None
        self.need_patch = None
        self.set_indexes()


    def set_indexes(self):
        if self.proj_name == "math":
            self.root_dir = r'D:\runningProjects\Math_version'
            self.clone_name = "\\defects4j-math"
            self.bug_ind = 1
            self.fix_ind = 2
            self.need_patch = False
        if self.proj_name == "lang":
            self.root_dir = r'D:\runningProjects\Lang_version'
            self.clone_name = "\\BugMinerResults-lang"
            self.need_patch = False
            self.bug_ind = 5
            self.fix_ind = 4
        if self.proj_name == "maven":
            self.root_dir = r'D:\runningProjects\Maven_version'
            self.clone_name = "\\BugMinerResults-maven"
            self.need_patch = True
            self.bug_ind = 0
            self.fix_ind = 0


class FilesAddress(object):
    def __init__(self, root_dir):
        self.java_code_dir = r'C:\Users\eyalhad\Desktop\predict-trace\javaCode'
        self.my_code_java_jar = os.path.join(self.java_code_dir, r'target\uber-Code-1.0-SNAPSHOT.jar')
        self.call_graph_jar = r'C:\Users\eyalhad\Desktop\predict-trace\additional_files\java-callgraph\target\javacg-0.1-SNAPSHOT-static.jar'
        self.checkstyle_jar = r'C:\Users\eyalhad\Desktop\predict-trace\additional_files\checkstyle-6.8-SNAPSHOT-all.jar'
        self.method_name_lines_xml = r'C:\Users\eyalhad\Desktop\predict-trace\additional_files\methodNameLines.xml'
        self.results_file = root_dir + r'\results.csv'
        self.sum_results_file = root_dir + r'\sum_results.csv'
        self.log_file = root_dir + r'\log.txt'
        self.func_record_file = root_dir + r'\func_record_file.txt'
        self.time_file = root_dir + r'\times.txt'
        self.errors_file = root_dir + r'\errors.txt'
        self.debugger_tests_dir = root_dir + r'\DebuggerTests'


class RunConfigure(object):
    def __init__(self, root_dir, project_name, clone_dir, bug_id, fix_version, bug_version):
        self.bug_id = bug_id
        self.fix_version = fix_version
        self.bug_version = bug_version
        self.project_dir = root_dir + "\\" + project_name + "_" + bug_id + "_fix"
        self.additional_files_path = self.project_dir + r'\additionalFiles'
        self.debugger_tests_path = self.additional_files_path + r'\DebuggerTests'
        self.git_repo_local_path = self.project_dir + clone_dir
        self.error_file = os.path.join(self.additional_files_path, r"errorFile.txt")
        self.trace_file = os.path.join(self.additional_files_path, r"traceFile.txt")

