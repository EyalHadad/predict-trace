import csv
import os
from itertools import izip


def write_diagnosis_result_file(results_dict, plot_file_path, bar_file_path):
    with open(plot_file_path, "w") as f:
        for key, value in results_dict.items():
            str_list = ','.join([str(x) for x in value])
            f.write(key + "," + str_list + "\n")



def calculate_diagnosis_results(path):
    with open(path) as csv_file:
        content = list(csv.reader(csv_file, delimiter=','))
    results_dict = {'oracle': [], 'prediction': [], 'baseline': [], 'random': [], }
    for line in content:
        details = line[0].split(":")
        if details[1] == 'precision':
            results_dict[details[0]].append(len(line) - 1)
    return results_dict


if __name__ == '__main__':
    diagnosis_result_file_path = r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\results_tmp.csv'
    num_steps_plot_file_path = r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\steps_plot.csv'
    steps_bar_file_path = r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\steps_bar.csv'
    res_dict = calculate_diagnosis_results(diagnosis_result_file_path)
    write_diagnosis_result_file(res_dict, num_steps_plot_file_path, steps_bar_file_path)