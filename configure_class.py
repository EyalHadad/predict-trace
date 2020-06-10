import os


class Configure(object):
    def __init__(self, proj_name, start_bug_num, end_bug_num):
        self.project_name = proj_name
        self.start_bug = int(start_bug_num)
        self.end_bug = int(end_bug_num)
        self.commit_database =None
        self.git_repo = None
        self.bug_ind = None
        self.fix_ind = None
        self.root_dir = None
        self.clone_name = None
        self.need_patch = None
        self.set_indexes()


    def set_indexes(self):
        if self.project_name == "math":
            self.commit_database = "C:\Users\eyalhad\Desktop\projects_db\defects4j\projects\Math\commit-db.txt"
            self.git_repo = "https://github.com/haidaros/defects4j-math.git"
            self.root_dir = r'D:\runningProjects\Math_version'
            self.clone_name = "\\defects4j-math"
            self.bug_ind = 1
            self.fix_ind = 2
            self.need_patch = False
        if self.project_name == "lang":
            self.commit_database = "C:\Users\eyalhad\Desktop\projects_db\BugMinerResults\commons-lang.csv"
            self.git_repo = "https://github.com/apache/commons-lang.git"
            self.root_dir = r'D:\runningProjects\Lang_version'
            self.clone_name = "\\BugMinerResults-lang"
            self.need_patch = False
            self.bug_ind = 5
            self.fix_ind = 4
        if self.project_name == "maven":
            self.commit_database = r"C:\Users\eyalhad\Desktop\projects_db\bugs_dot_jar\maven\maven_commits.csv"
            self.git_repo = "https://github.com/bugs-dot-jar/maven.git"
            self.root_dir = r'D:\runningProjects\Maven_version'
            self.clone_name = "\\BugMinerResults-maven"
            self.need_patch = True
            self.bug_ind = 0
            self.fix_ind = 0
        if self.project_name == "wicket":
            self.commit_database = r"C:\Users\eyalhad\Desktop\projects_db\bugs_dot_jar\wicket\wicket_commit.csv"
            self.git_repo = "https://github.com/bugs-dot-jar/wicket.git"
            self.root_dir = r'D:\runningProjects\Wicket_version'
            self.clone_name = "\\BugMinerResults-wicket"
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
        self.buggy_functions = root_dir + r'\buggy_function.txt'
        self.debugger_tests_dir = root_dir + r'\DebuggerTests'


class RunConfigure(object):
    def __init__(self, root_dir, project_name, clone_dir, bug_id, fix_version, bug_version):
        self.bug_id = str(bug_id)
        self.fix_version = fix_version
        self.bug_version = bug_version
        self.project_dir = root_dir + "\\" + project_name + "_" + self.bug_id + "_fix"
        self.additional_files_path = self.project_dir + r'\additionalFiles'
        self.debugger_tests_path = self.additional_files_path + r'\DebuggerTests'
        self.git_repo_local_path = self.project_dir + clone_dir
        self.error_file = os.path.join(self.additional_files_path, r"errorFile.txt")
        self.trace_file = os.path.join(self.additional_files_path, r"traceFile.txt")
        self.pom_file = os.path.join(self.git_repo_local_path, r'pom.xml')

