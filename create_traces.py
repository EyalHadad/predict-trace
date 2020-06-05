import json
from os import listdir, mkdir, path, remove
from os.path import join


def get_content(dir_path):
    content = []
    file_names = [f for f in listdir(dir_path)]
    for trace_file in file_names:
        path = join(dir_path, trace_file)
        with open(path, "r") as f:
            try:
                cont = json.load(f)
                if len(cont) > 0:
                    content.append([trace_file.split('_')[1], cont])
            except Exception as e:
                print(str(trace_file) + " : " + e.message)

    return content


def write_trace_to_txt(dir_path, commit_number, commit_trace, proj_name):
    folder_name = proj_name + "_" + str(commit_number) + "_fix"
    full_folder_name = join(dir_path, folder_name)

    if path.exists(full_folder_name):
        remove(full_folder_name)
    mkdir(join(dir_path, folder_name))
    with open(join(dir_path, folder_name, "traceFile.txt"), mode="w") as f:
        for test, trace in commit_trace.items():
            f.write("#test#" + str(test))
            f.write("\n\n")
            f.write("#trace#" + str("".join(trace)))
            f.write("\n\n")
    i = 8


def write_content(dir_path, traces_list, commit_dict, proj_name):
    for commit, trace in traces_list:
        commit_number = commit_dict[commit]
        write_trace_to_txt(dir_path, commit_number, trace, proj_name)


def get_commit_numbers(path):
    with open(path, "r") as f:
        content = f.readlines()

    commit_n = {}
    for num, val in enumerate(content):
        commit_n[val.split('_')[-1].strip()] = num
    return commit_n


if __name__ == '__main__':
    source_path = r'C:\Users\eyalhad\Desktop\newTraces'
    dest_path = r'C:\Users\eyalhad\Desktop\dest_tarce'
    commit_numbers = get_commit_numbers(r'C:\Users\eyalhad\Desktop\wicket_commit.csv')
    traces = get_content(source_path)
    write_content(dest_path, traces, commit_numbers, "wicket")
    i = 6
