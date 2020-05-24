import filediff
import git
import os


def get_class_from_line(line):
    tmp_line = line.split(" ")[0]
    tmp_line = tmp_line[tmp_line.find("src"):tmp_line.find(".java") + 5]
    tmp_line = tmp_line.replace("\\", "/")
    return tmp_line


def index_to_names(index_list, java_class, project_path, func_list):
    method_lines = os.path.join(project_path, r"method_lines.txt")
    with open(method_lines) as f:
        content = f.readlines()
    for line in content:
        str_class = get_class_from_line(line)
        if str_class.encode('UTF-8') == java_class:
            func_name = line.split(" ")[1].split("@")[0]
            first_num = int(line.split(" ")[1].split("@")[1])
            second_num = int(line.split(" ")[1].split("@")[2])
            for index in index_list:
                if first_num <= index <= second_num:
                    full_func_name = str_class[str_class.find("org"):str_class.find(".java")].\
                                         replace("/",".") + ":" + func_name
                    if full_func_name not in func_list:
                        func_list.append(full_func_name)
    return func_list


def method_name_xml(run_conf):
    method_lines = os.path.join(run_conf.git_repo_local_path, r"method_lines.txt")
    with open(method_lines, "w+") as f:
        p_create_call_graph = subprocess.Popen(
            ['java', '-jar', file_address.checkstyle_jar, '-c', file_address.method_name_lines_xml, 'javaFile',
             run_conf.git_repo_local_path], stdout=f)
    p_create_call_graph.communicate()


def fix_constructor_names(func_names):
    new_func_names = []
    for tmp_name in func_names:
        if tmp_name.split(":")[0].split(".")[-1] == tmp_name.split(":")[1]:
            split_string = tmp_name.split(":")
            split_string[1] = "<init>"
            tmp_name = ":".join(split_string)

        new_func_names.append(tmp_name)
    return new_func_names


def get_func_names(run_conf):
    repo = git.Repo(run_conf.git_repo_local_path)
    commit_a = repo.commit(run_conf.bug_version)
    commit_b = repo.commit(run_conf.fix_version)
    diffs = map(filediff.FileDiff, commit_a.tree.diff(commit_b.tree))
    method_name_xml(run_conf)
    func_names = []
    for x in diffs:
        if x.file_name.endswith('.java') and "Test" not in x.file_name:
            if len(x.before_indices) > 0:
                index_to_names(x.before_indices, x.file_name, run_conf.git_repo_local_path, func_names)

    return fix_constructor_names(func_names)


def extract_buggy_functions(run_conf):
    repo_path = run_conf.project_dir + conf.clone_name
    repo = git.Repo(repo_path)
    repo.git.checkout('-f', '--', '.', )
    repo.git.apply("--whitespace=nowarn", os.path.join(repo_path, ".bugs-dot-jar", "developer-patch.diff"))
    buggy = map(lambda x: x.id.split("@")[1].replace(',', ';'),
                diff.get_modified_functions(repo_path))
    repo.git.checkout('-f', '--', '.', )
    cut_str = [str(x).split("(")[0] for x in buggy]
    cut_str[0] = cut_str[0][::-1].replace(".", ":", 1)[::-1]
    to_return = [x[::-1].replace(".", ":", 1)[::-1] for x in cut_str]
    return to_return
