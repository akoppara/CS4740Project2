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
	return (all_words_list)

def build_lexicon (all_words_list):
	uncertainty_list = {}
	lexicon = {}
	lexicon_keys = []
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
			lexicon_keys.append(w)
			count_for_baseline += 1
		else:
			break
	return (lexicon, lexicon_keys)

def grab_test_files (lexicon_keys, path):
	all_words_list = []
	for file in os.listdir(path):
		all_words_list += read_file(path, file)
	tagged_word_list = tag_uncertainty(all_words_list, lexicon_keys)
	return(tagged_word_list)

#note all_words_list here is an array with a nested array for each file
def tag_uncertainty (all_words_list, lexicon_keys):
	for words_in_file in all_words_list:
		if (len(words_in_file) > 1):
			if(words_in_file[0] in lexicon_keys):
				words_in_file.append('CUE')
			else:
				words_in_file.append('_')
	return (all_words_list)

def tagged_indexes (all_test_words_list):
	cue = 'CUE'
	token_array = []
	indexes = []
	count = 0
	for words_in_file in all_test_words_list:
		if (len(words_in_file) > 1):
			if (cue in words_in_file[2]):
				token_array.append(True)
			else:
				token_array.append(False)
	for tagged in token_array:
		if tagged:
			indexes.append(count)
		else:
			indexes.append(0)
		count += 1
	return (indexes)

def array_to_range(index_range):
	range_string = str(index_range[0]) + "-" + str(index_range[len(index_range) - 1])
	return (range_string)

def index_ranges (index_array):
	prev_tagged = False
	index_string = ""
	for index in index_array:
		if (not prev_tagged) and (index > 0):
			index_range = []
			index_range.append(index)
			prev_tagged = True
		elif (prev_tagged) and (index > 0):
			index_range.append(index)
		elif (prev_tagged) and (index == 0):
			index_string += array_to_range(index_range) + " "
			prev_tagged = False
	return (index_string)

def uncertain_phrase_detection(lexicon_keys):
	test_public_path = "nlp_project2_uncertainty\\nlp_project2_uncertainty\\test-public"
	test_private_path = "nlp_project2_uncertainty\\nlp_project2_uncertainty\\test-private"
	all_test_public_words_list = grab_test_files(lexicon_keys, test_public_path)
	all_test_private_words_list = grab_test_files(lexicon_keys, test_private_path)
	test_public_index_array = tagged_indexes(all_test_public_words_list)
	test_private_index_array = tagged_indexes(all_test_private_words_list)
	test_public_index_ranges = index_ranges(test_public_index_array)
	test_private_index_ranges = index_ranges(test_private_index_array)
	write_to_csv(test_public_index_ranges, test_private_index_ranges)

def write_to_csv(test_public_index_ranges, test_private_index_ranges):
	with open('kaggle1.csv', 'w', newline='') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
		csvwriter.writerow(['Type', 'Spans'])
		csvwriter.writerow(['CUE-public', test_public_index_ranges])
		csvwriter.writerow(['CUE-private', test_private_index_ranges])

if __name__ == '__main__':
	all_words_list = grab_files()
	lexicon, lexicon_keys = build_lexicon(all_words_list)
	uncertain_phrase_detection(lexicon_keys)