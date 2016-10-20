#Project 2
import os
import csv
import copy
import operator

SOS_TAG = "<s>"

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

def grab_files (path):
	all_words_list = []
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
		print(words_in_file)
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


def is_sentence_uncertain(sentence):
	threshold = 0.3
	cue_count = 0.0
	sentence_length = float(len(sentence))
	for token in sentence:
		if token[2] == "CUE":
			cue_count += 1.0
	return (cue_count / sentence_length) >= threshold



def check_sentences(all_test_words_list):
	sentence_tags = []
	sentence_group = []
	sentence_id = 0
	for words_tags in all_test_words_list:
		if words_tags[0] == '' and len(sentence_group) != 0:
			uncertain = is_sentence_uncertain(sentence_group)
			if uncertain:
				sentence_tags.append(sentence_id)
			sentence_group = []
			sentence_id += 1
		else:
			if words_tags[0] != '':
				sentence_group.append(words_tags)

	return sentence_tags

def uncertain_sentence_detection(lexicon_keys):
	test_public_path = "nlp_project2_uncertainty\\nlp_project2_uncertainty\\test-public"
	test_private_path = "nlp_project2_uncertainty\\nlp_project2_uncertainty\\test-private"
	all_test_public_words_list = grab_test_files(lexicon_keys, test_public_path)
	all_test_private_words_list = grab_test_files(lexicon_keys, test_private_path)

	public_tags = check_sentences(all_test_public_words_list)
	private_tags = check_sentences(all_test_private_words_list)

	output_kaggle_2_csv([public_tags, private_tags])

def output_kaggle_2_csv(tags):
	#tags is an array of the public (first element) and private (second) tag arrays
	space_tags = []
	for tag_types in tags:
		space_tags.append(' '.join(str(x) for x in tag_types))

	with open("kaggle2.csv", "w") as csvfile:
		file_writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')

		file_writer.writerow(["Type", "Indices"])
		file_writer.writerow(["SENTENCE-public"] + [space_tags[0]])
		file_writer.writerow(["SENTENCE-private"] + [space_tags[1]])
	print("DONE -- output in kaggle2.csv")

def cue_to_bio_training (all_words_list):
	prev_tagged = False
	cue = "CUE"
	prev_cue = ""

	for line in all_words_list:
		if (len(line) == 3):
			if not (cue in line[2]):
				prev_cue = line[2]
				line[2] = "O"
				prev_tagged = False
			elif not (prev_tagged) and (cue in line[2]):
				prev_cue = line[2]
				line[2] = "B"
				prev_tagged = True
			elif (prev_tagged) and (line[2] in prev_cue):
				prev_cue = line[2]
				line[2] = "I"
			elif (prev_tagged) and not (line[2] in prev_cue):
				prev_cue = line[2]
				line[2] = "B"
		else:
			line.append(SOS_TAG)
			line.append(SOS_TAG)
	return all_words_list

def count_word_tag_pairs(all_words_list_BIO):
	counts = {}
	for line in all_words_list_BIO:
		if len(line) > 1:
			word = line[0]
			tag = line[2]
			if word not in counts and word != '':
				#First timer here
				bio = {"B" : 0, "I" : 0, "O" : 0}
				counts[word] = bio
			if tag != SOS_TAG:
				counts[word][tag] += 1
	return counts

def calc_probs_word_tags(bio_counts):
	bio_probs = copy.deepcopy(bio_counts)
	for word, bios in bio_probs.items():
		tag_sum = bios["B"] + bios["I"] + bios["O"]
		#Calc probs
		#B
		bios["B"] = bios["B"] / float(tag_sum)
		#I
		bios["I"] = bios["I"] / float(tag_sum)
		#O
		bios["O"] = bios["O"] / float(tag_sum)
	return bio_probs

def bio_array_from_words (all_words_list_BIO):
	all_BIO_list = []
	for line in all_words_list_BIO:
		if (len(line) == 3):
			all_BIO_list.append(line[2])
	return all_BIO_list

def calc_unigram_counts (token_array):
	vocab_size = 0
	unigram_count = {}
	for key in token_array:
		unigram_count[key] = 0
		vocab_size += 1
	for key in token_array:
		unigram_count[key] +=1
	return (unigram_count, vocab_size)

def calc_unigram_probs (unigram_count, vocab_size):
	unigram_probs = copy.deepcopy(unigram_count)
	for key in unigram_probs:
		unigram_probs[key] = unigram_probs[key] / vocab_size
	return unigram_probs

def calc_bigram_counts (token_array):
    #dictonary to hold counts
    d = {}
    for i in range(len(token_array)):
        #w_n
        wordn = token_array[i]
        if i == 0:
            wordn1 = "O"
        else:
            wordn1 = token_array[i-1]

        if wordn1 in d:
            wd = d[wordn1]
            if wordn in wd:
                wd[wordn] += 1
            else:
                wd[wordn] = 1
        else:
            wd = {}
            wd[wordn] = 1
            d[wordn1] = wd

    return d

def calc_bigram_probs (bigram_counts, token_array):
    # need unigram counts for division later
    unigram_counts, vocab_size = calc_unigram_counts(token_array)
    # copy of bigram_counts dictionary
    bigram_probs = copy.deepcopy(bigram_counts)
    # first for loop goes through outer layer of bigram counts
    for key, value in bigram_counts.items():
        # second for loop goes through the inner layer of each outer layer
        for following_word, word_count in value.items():
            bigram_prob = float(word_count) / float(unigram_counts[key])
            bigram_probs[key][following_word] = bigram_prob
    return bigram_probs


PROB_PRIOR = 0.5

def viterbi(bio_bigram_probs, bio_probs, words):
	tags = ["B", "I", "O"]
	c = 3
	score = {}
	bptr = {}
	#Init
	for i in range(c):
		try:
			bio_prob = bio_probs[words[0]][tags[i]]
		except KeyError:
			bio_prob = 0.5
		score[i] = {0 : (bio_bigram_probs[SOS_TAG][tags[i]] * bio_prob)}
		bptr[i] = {0 : 0}
	# print("AFTER INIT:")
	# print(score)
	# print(bptr)
	#Iteration
	for t in range(1,len(words)):
		# print(words[t])
		for i in range(c):
			values = []
			# print(score)
			for j in range(c):
				# print(bio_bigram_probs[tags[j]][tags[i]])
				values.append(score[j][(t-1)] * bio_bigram_probs[tags[j]][tags[i]])
			idx, value = max(enumerate(values), key=operator.itemgetter(1))
			# print("VALUE: " + str(value))
			try:
				word_bio_prob = bio_probs[words[t]][tags[i]]
			except KeyError:
				word_bio_prob = 0.333
			# print(word_bio_prob)
			score[i][t] = value * word_bio_prob
			bptr[i][t] = idx
			# print(score)
	#Identify
	T = {}
	n = len(words)
	max_i_n = -1
	max_i = -1
	for i in range(c):
		if score[i][n-1] > max_i_n:
			max_i_n = score[i][n-1]
			max_i = i

	T[n-1] = max_i
	for i in reversed(range(0, n-1)):
		T[i] = bptr[T[i+1]][i+1]
	return T

def run_viterbi(path, bigram_probs, bio_probs, kaggle2):
	all_words_list = grab_files(path)
	words = []
	for line in all_words_list:
		words.append(line[0])
	#For testing, get first sentence only
	sentences = []
	sentence = []
	for w in words:
		if w == '':
			sentences.append(sentence)
			sentence = []
		else:
			sentence.append(w)
	result = []
	tags = ["B", "I", "O"]
	uncertain_sentences = []
	s_index = 0
	for s in sentences:
		added = False
		if len(s) > 0:
			T = viterbi(bigram_probs, bio_probs, s)
			for word_idx, tag_idx in T.items():
				if tag_idx == 0 and not added:
					added = True
					uncertain_sentences.append(s_index)
				tag_pair = [s[word_idx], tags[tag_idx]]
				result.append(tag_pair)
			s_index += 1
	if kaggle2:
		return result, uncertain_sentences
	else:
		return result

def kaggle1_str(tagged_words, public):
	#tagged_words is an array where each element is of the form:
	#[word, tag] where tag is either B, I, O
	ranges = []
	prev_tagged = False
	curr_range = []
	was_B = False
	for i, pair in enumerate(tagged_words):
		if pair[1] == "O":
			if prev_tagged:
				#close it off
				if was_B:
					ranges.append(curr_range)
					curr_range = []
				else:
					curr_range.append(i-1)
					ranges.append(curr_range)
					curr_range = []
			prev_tagged = False
			was_B = False
		elif pair[1] == "B":
			#Start of a cue span
			if prev_tagged:
				#Previous was a B tag, this is a new cue
				if was_B:
					ranges.append(curr_range)
					curr_range = []
				else:
					curr_range.append(i-1)
					ranges.append(curr_range)
					curr_range = []
			else:
				prev_tagged = True
			was_B = True
			curr_range.append(i)
		elif pair[1] == "I":
			was_B = False
		else:
			#TODO: REMOVE
			raise ValueError('how the fuck did you do this')
	#ranges now hold the index ranges for the kaggle 1 submission
	#[[1,2], [4], [13, 15]]
	result_string = ""
	for r in ranges:
		if len(r) == 1:
			add = str(r[0]) + "-" + str(r[0])
		else:
			#2 numbers
			add = str(r[0]) + "-" + str(r[1])
		result_string += add + " "

	return result_string

def kaggle1_csv(bio_bigram_probs, bio_probs):

	public_path = "nlp_project2_uncertainty\\nlp_project2_uncertainty\\test-public"
	private_path = "nlp_project2_uncertainty\\nlp_project2_uncertainty\\test-private"

	public_tags = run_viterbi(public_path, bio_bigram_probs, bio_probs, False)
	private_tags = run_viterbi(private_path, bio_bigram_probs, bio_probs, False)

	public_string = kaggle1_str(public_tags, True)
	private_string = kaggle1_str(private_tags, False)

	with open('kaggle1-hmm.csv', 'w', newline='') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
		csvwriter.writerow(['Type', 'Spans'])
		csvwriter.writerow(['CUE-public', public_string])
		csvwriter.writerow(['CUE-private', private_string])

def kaggle2_str(ranges):
	result_string = ""
	for i in ranges:
		result_string += str(i) + " "
	return result_string

def kaggle2_csv(bio_bigram_probs, bio_probs):

	public_path = "nlp_project2_uncertainty\\nlp_project2_uncertainty\\test-public"
	private_path = "nlp_project2_uncertainty\\nlp_project2_uncertainty\\test-private"

	public_tags, public_ranges = run_viterbi(public_path, bio_bigram_probs, bio_probs, True)
	private_tags, private_ranges = run_viterbi(private_path, bio_bigram_probs, bio_probs, True)

	public_string = kaggle2_str(public_ranges)
	private_string = kaggle2_str(private_ranges)

	with open('kaggle2-hmm.csv', 'w', newline='') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
		csvwriter.writerow(['Type', 'Indices'])
		csvwriter.writerow(['SENTENCE-public', public_string])
		csvwriter.writerow(['SENTENCE-private', private_string])

def add_zeroes_to_bigram_prob (bigram_probs):
	possible_keys = []
	for key in bigram_probs:
		if not (key in possible_keys):
			possible_keys.append(key)
	for key in bigram_probs:
		possible_keys_disposable = possible_keys[:]
		for following_tag, prob in bigram_probs[key].items():
			possible_keys_disposable.remove(following_tag)
		for possible_left in possible_keys_disposable:
			bigram_probs[key][possible_left] = 0
	return bigram_probs

if __name__ == '__main__':
	train_path = "nlp_project2_uncertainty\\nlp_project2_uncertainty\\train"
	public_path = "nlp_project2_uncertainty\\nlp_project2_uncertainty\\test-public"
	private_path = "nlp_project2_uncertainty\\nlp_project2_uncertainty\\test-private"

	all_words_list = grab_files(train_path)
	lexicon, lexicon_keys = build_lexicon(all_words_list)
	all_words_list_BIO = cue_to_bio_training(all_words_list)
	bio_counts = count_word_tag_pairs(all_words_list_BIO)
	bio_probs = calc_probs_word_tags(bio_counts)
	all_BIO_list = bio_array_from_words(all_words_list_BIO)
	BIO_unigram_counts, vocab_size = calc_unigram_counts(all_BIO_list)
	BIO_unigram_probs = calc_unigram_probs(BIO_unigram_counts, vocab_size)
	BIO_bigram_counts = calc_bigram_counts(all_BIO_list)
	BIO_bigram_probs = calc_bigram_probs(BIO_bigram_counts, all_BIO_list)
	BIO_bigram_probs = add_zeroes_to_bigram_prob(BIO_bigram_probs)

	words = [
		["A", "O"],
		["B", "B"],
		["C", "I"],
		["D", "O"],
		["E", "B"],
		["F", "B"],
		["G", "I"],
		["H", "B"],
		["I", "O"],
		["J", "O"],
		["K", "B"],
		["L", "I"],
		["M", "I"],
		["N", "O"]
	]


	kaggle1_csv(BIO_bigram_probs, bio_probs)
	kaggle2_csv(BIO_bigram_probs, bio_probs)
	# print(BIO_bigram_probs)

	#for key in BIO_bigram_probs:
	#	_sum = 0
	#	for _key, value in BIO_bigram_probs[key].items():
	#		_sum += value
	#	print(_sum)

	#grab_files(public_path)


	# uncertain_phrase_detection(lexicon_keys)
	# uncertain_sentence_detection(lexicon_keys)