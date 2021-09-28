#!/usr/bin/python3
# v0.6c 28.09.2021
import datetime
import sys
from statistics import mean
import argparse
import os
import re
import string

# import resource

DICT1_NAME = "dic.words.en.txt"
DICT2_NAME = "dic.words.pl-sjp-20210731.txt"

# print (resource.getrusage(resource.RUSAGE_SELF).ru_ixrss)


# Sentences
PROBLEM_WITH_THE_FILE_COMM = "There is a problem with the file:"
LOADING_DICT_COMM = "Loading wordlist:"
LOADING_DICT_COMM_ANALYZE = "Loading wordlist for order:"
SAVING_DICT_COMM = "Saving wordlist:"
STRIPPING_DICT_COMM = "Stripping wordlist:"
COMMON_WORDS_COMM = "Looking for common words in both wordlists:"
WORDS_COMM = "words"
FOUND_COMM = "found"
END_COMM = "end"
REMAINING_COMM = "remaining"
NO_PAR_COMM = "No parameters. Default wordlists have been loaded."
TWO_DICT_COMM = "Names of two wordlists."
STRIP_WORD_COMM = "Strip all from second directory except words."
ANALYZE_ORIGIN_COMM = (
    "Resulting file will not be in the same order as in the first wordlist."
)
SET_WORD_ORDER_COMM = "Setting the word order:"
QUIET_MODE_COMM = "Quiet mode"
WRONG_COMM = "Something wrong"
COMMON_COM = "common_"
FILE_SAVE_NAME_COMM = "Output filename"

result_wordlist = ""
# ---parameters flag
strip_flag = False
origin_flag = True
quiet_flag = False
file_save_name_flag = False

dict1_set = set()
dict2_set = set()

average_words_per_seconds = []
start = 0
found = 0
columns = 0
number_of_lines_per_second = 0
number_of_lines_per_second_max = 1
number_of_lines_per_second_average = 1
result_wordlist_tmp = []


def read_wordlist_4_analyze(DIC_NAME, len_dict, analyze_wd):
    print()
    print(
        LOADING_DICT_COMM_ANALYZE,
        DIC_NAME,
        "(" + str(len_dict),
        WORDS_COMM + ")",
        end="\r",
    )
    result_wordlist_tmp = []
    count = 0
    print()
    try:
        with open(DIC_NAME, "r") as fin:
            for line in fin:
                line = line.strip().lower()
                count += 1
                word_to_sort_len_percent = int((count * 100) / (len_dict))
                print(
                    SET_WORD_ORDER_COMM,
                    word_to_sort_len_percent,
                    "% -",
                    count,
                    WORDS_COMM,
                    end="\r",
                )
                if line in analyze_wd:
                    result_wordlist_tmp.append(line)
    except Exception as error:
        print(PROBLEM_WITH_THE_FILE_COMM, DIC_NAME)
        print(error)
        exit()
    return result_wordlist_tmp


def read_wordlist(dict_sl, DIC_NAME):
    print(LOADING_DICT_COMM, DIC_NAME, end="\r")
    try:
        with open(DIC_NAME, "r") as fin:
            for line in fin:
                dict_sl.add(line.strip().lower())

    except Exception as error:
        print(PROBLEM_WITH_THE_FILE_COMM, DIC_NAME)
        print(error)
        exit()

    print(LOADING_DICT_COMM, DIC_NAME, "(" + str(len(dict_sl)), WORDS_COMM + ")")
    return dict_sl


def searching_for_common_words(dict1_set, dict2_set):
    result_wordlist_list = set()
    now = datetime.datetime.now()

    print(COMMON_WORDS_COMM + "\n")
    last_word = ""
    line_counter = len(dict1_set)
    sec_now = int(datetime.datetime.now().second)
    sec_plus_one = int(sec_now) + 1
    sec_to_end = 0
    global found, number_of_lines_per_second, number_of_lines_per_second_max, columns

    for counter, i in enumerate(dict1_set, start=1):
        print(
            str(counter) + "|" + str(line_counter) + "|" + str(found),
            FOUND_COMM + "|" + str(number_of_lines_per_second_max),
            WORDS_COMM + "/s|" + REMAINING_COMM,
            str(datetime.timedelta(seconds=sec_to_end))
            + " s"
            + "|"
            + str(i)
            + "    " * 10,
            end="\r",
            flush=True,
        )
        sec_now = int(datetime.datetime.now().second)
        try:
            sec_to_end = round(
                (line_counter - counter) / number_of_lines_per_second_max
            )
        except:
            sec_to_end = 0

        if sec_now < sec_plus_one:
            number_of_lines_per_second += 1
        else:
            number_of_lines_per_second_max = number_of_lines_per_second
            sec_plus_one = sec_now + 1
            number_of_lines_per_second = 0
            average_words_per_seconds.append(number_of_lines_per_second_max)

        if i in dict2_set:
            found += 1
            result_wordlist_list.add(i)
            make_space = columns - len(i) - 2
            if not quiet_flag:
                print("\r" + i + " " * make_space)
    return result_wordlist_list


def save_wordlist(result_wordlist_list, filename):
    print("\n{:<45s}{:s}".format(SAVING_DICT_COMM, filename))
    try:
        with open(filename, "w") as f:
            for element in result_wordlist_list:
                f.write("%s\n" % element)
    except Exception as error:
        print(PROBLEM_WITH_THE_FILE_COMM, filename)
        print(error)
        exit()


def check_strip_par(DICT_NAME, dict):
    assemblage = set()
    len_dict = len(dict)
    count_all = 0
    count_strip = 0

    for i in dict:
        count_all += 1
        word_to_sort_len_percent = int((count_all * 100) / (len_dict))
        print(
            STRIPPING_DICT_COMM,
            DICT_NAME + " (" + str(word_to_sort_len_percent),
            "% -",
            str(count_strip) + "/" + str(count_all),
            WORDS_COMM + ")",
            end="\r",
        )
        assemblage.add(re.sub("[!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~0123456789]", "", i))
        count_strip = len(assemblage)
    print()
    return assemblage


def summary():
    global start, finish
    try:
        av_per_sec = mean(average_words_per_seconds)
    except:
        av_per_sec = 0
    print("")
    print("{:<45s}{:s}".format("Start:", str(start)))
    print("{:<45s}{:s}".format("End:", str(finish)))
    print("{:<45s}{:s}".format("Total time:", str(finish - start)))
    print("{:<45s}{:d}".format("Common words:", found))
    if round(av_per_sec) == 0:
        print("{:<45s}{:s}".format("Checked words/second:", "not counted"))
    else:
        print("{:<45s}{:d}".format("Checked words/second:", round(av_per_sec)))


parser = argparse.ArgumentParser(
    description="""The program is used to find identical words in two large wordlists.
Program parameters are: -s wordlist1 wordlist2
If parameters are not specified, the program uses the default wordlists.
""",
    formatter_class=argparse.RawTextHelpFormatter,
)


parser.add_argument(
    "-w",
    "--wordlist",
    type=str,
    help=TWO_DICT_COMM,
    required=False,
    nargs=2,
    metavar=("wordlist1", "wordlist2"),
)
parser.add_argument("-f", "--file", type=str, help=FILE_SAVE_NAME_COMM)
parser.add_argument("-s", "--strip", help=STRIP_WORD_COMM, action="store_true")
parser.add_argument("-ng", "--no-origin", help=ANALYZE_ORIGIN_COMM, action="store_true")
parser.add_argument("-q", "--quiet", help=QUIET_MODE_COMM, action="store_true")


args = parser.parse_args()
if args.wordlist:
    DICT1_NAME = args.wordlist[0]
    DICT2_NAME = args.wordlist[1]
else:
    parser.print_help()
    print("\n" + NO_PAR_COMM + "\n")

if args.strip:
    strip_flag = True

if args.no_origin:
    origin_flag = False

if args.quiet:
    quiet_flag = True

if args.file:
    file_save_name_flag = True


def init():
    global columns, start
    start = datetime.datetime.now().replace(microsecond=0)
    columns, rows = os.get_terminal_size()


init()

dict1_set = read_wordlist(dict1_set, DICT1_NAME)
dict1_set_len = len(dict1_set)
dict2_set = read_wordlist(dict2_set, DICT2_NAME)


if strip_flag:
    # dict1_set = check_strip_par(DICT1_NAME,dict1_set)
    dict2_set = check_strip_par(DICT2_NAME, dict2_set)

result_wordlist_list = searching_for_common_words(dict1_set, dict2_set)


if origin_flag:

    result_wordlist_list = read_wordlist_4_analyze(
        DICT1_NAME, dict1_set_len, result_wordlist_list
    )

else:
    print(ANALYZE_ORIGIN_COMM)

if file_save_name_flag:
    filename = args.file
    save_wordlist(result_wordlist_list, filename)
else:
    filename = COMMON_COM + DICT1_NAME + "_" + DICT2_NAME
    save_wordlist(result_wordlist_list, filename)

finish = datetime.datetime.now().replace(microsecond=0)
summary()
