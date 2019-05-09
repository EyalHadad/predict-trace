import csv
import os


def scan_csv(path):
    with open(path) as csv_file:
        content = list(csv.reader(csv_file, delimiter=','))
        amir_length_count = 0
        amir_last_score_sum = 0
        eyal_length_count = 0
        eyal_last_score_sum = 0
        random_length_count = 0
        random_last_score_sum = 0
        divide = 0
        for i in range(len(content)):
            # content[i] = list(filter(None, content[i]))
            if len(content[i]) > 0 and 'Bug' in content[i][0] and 'Eyal' in content[i + 6][0] and 'Random' in \
                    content[i + 11][0]:
                content[i + 3] = list(filter(None, content[i + 3]))
                content[i + 8] = list(filter(None, content[i + 8]))
                content[i + 13] = list(filter(None, content[i + 13]))
                if len(content[i + 3]) > 0:
                    amir_length_count = amir_length_count + len(content[i + 3])
                    amir_last_score_sum = amir_last_score_sum + float(content[i + 3][-1])
                    eyal_length_count = eyal_length_count + len(content[i + 8])
                    eyal_last_score_sum = eyal_last_score_sum + float(content[i + 8][-1])
                    random_length_count = random_length_count + len(content[i + 13])
                    random_last_score_sum = random_last_score_sum + float(content[i + 13][-1])
                    divide = divide + 1

        average_number_of_steps = ["Amir:", amir_length_count / divide, "Eyal:", eyal_length_count / divide, "Random:",
                                   random_length_count / divide]
        average_last_core = ["Amir:", amir_last_score_sum / divide, "Eyal:", eyal_last_score_sum / divide, "Random:",
                             random_last_score_sum / divide]

    return average_number_of_steps, average_last_core


def print_results():
    print("----------------------" + csv_file_path.split("\\")[-1] + "----------------------")
    print("lengths: " + str(avg_len))
    print("last score: " + str(avg_last_score))


def save_results_in_new_file(new_results_file, project_name, bug_num, actual_precision, actual_recall,
                             predicted_precision, predicted_recall, random_precision, random_recall):
    f = open(new_results_file, 'a+')
    f.write("project , Bug Num, Alg, step, precision, recall \n")
    for i in xrange(len(actual_precision)):
        f.write(project_name + "," + str(bug_num) + "," + "Actual" + "," + str(i) + "," + actual_precision[i] + "," + actual_recall[i] + "\n")

    for i in xrange(len(predicted_precision)):
        f.write(project_name + "," + str(bug_num) + "," + "Predicted" + "," + str(i) + "," + predicted_precision[i] + "," + predicted_recall[i] + "\n")

    for i in xrange(len(random_precision)):
        f.write(project_name + "," + str(bug_num) + "," + "Random" + "," + str(i) + "," + random_precision[i] + "," + random_recall[i] + "\n")

    f.close()


def create_roni_file(path, new_results_file):
    if os.path.isfile(new_results_file):
        os.remove(new_results_file)
    with open(path) as csv_file:
        content = list(csv.reader(csv_file, delimiter=','))

        for i in range(len(content)):
            # content[i] = list(filter(None, content[i]))
            if len(content[i]) > 0 and 'Bug' in content[i][0] and 'Eyal' in content[i + 6][0] and 'Random' in \
                    content[i + 11][0]:
                project_name = path.split("\\")[5].split("_")[0]
                bug_num= content[i][0].replace("Bug num", "")
                actual_precision = list(filter(None, content[i + 3]))
                actual_recall = list(filter(None, content[i + 5]))
                predicted_precision = list(filter(None, content[i + 8]))
                predicted_recall = list(filter(None, content[i + 10]))
                random_precision = list(filter(None, content[i + 13]))
                random_recall = list(filter(None, content[i + 15]))
                save_results_in_new_file(new_results_file, project_name, bug_num, actual_precision, actual_recall,
                                         predicted_precision, predicted_recall, random_precision, random_recall)

                i=6



if __name__ == '__main__':
    csv_file_path = r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\results.csv'
    new_result = r'C:\Users\eyalhad\Desktop\runningProjects\Lang_version\results_roni.csv'
    create_roni_file(csv_file_path,new_result)
    avg_len, avg_last_score = scan_csv(csv_file_path)
    print_results()
    # csv_file_path = r'C:\Users\Eyal-TLV\Desktop\results\mathResults.csv'
    # avg_len, avg_last_score = scan_csv(csv_file_path)
    # print_results()
