#Project 2
import os
import csv

def read_file (path, file):
	file_words = []
	file_path = path + '\\' + file
	open_file = open(file_path, encoding="utf8")
	file_string = open_file.read()
	file_array = file_string.split('\n')
	for each in file_array:
		line_array = each.split('\t')
		file_words.append(line_array)
	return(file_words)

def grab_files ():
	all_words_list = []
	path = "nlp_project2_uncertainty\\nlp_project2_uncertainty\\train"
	for file in os.listdir(path):
		all_words_list += read_file(path, file)
	return all_words_list

def build_lexicon (all_words_list):
	uncertainty_list = {}
	lexicon = {}
	cue = 'CUE'
	length_of_baseline = 100
	count_for_baseline = 0

	for each_word in all_words_list:
		if (len(each_word) == 3):
			if cue in each_word[2]:
				word = each_word[0]
				uncertainty_list[word] = uncertainty_list.get(word, 0) + 1
	for w in sorted(uncertainty_list, key=uncertainty_list.get, reverse=True):
		if (count_for_baseline < length_of_baseline):
			lexicon[w] = uncertainty_list[w]
			count_for_baseline += 1
		else:
			break
	return lexicon

def grab_test_files ():
	all_words_list = []
	path = "nlp_project2_uncertainty\\nlp_project2_uncertainty\\test-private"
	for file in os.listdir(path):
		all_words_list += read_file(path, file)
	return all_words_list

if __name__ == '__main__':
	all_words_list = grab_files()
	lexicon = build_lexicon(all_words_list)

	