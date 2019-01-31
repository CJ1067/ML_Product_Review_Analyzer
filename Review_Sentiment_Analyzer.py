import re

"""Review_Sentiment_Analyzer.py: Contains three functions: one to encrypt a message using a key based on user input,
one to determine if two numbers are coprime and illustrate the Euclidean method, and one to
calculate an inverse modulo."""

__author__ = "Christopher Lehman"
__version__ = "1/25/19"


def readAndDivideBySentiment(fileName):
    """Traverses given file and separates all reviews into positive and negative based on the number at the end

        Args:
            fileName (str): path to the file to divide reviews.

        Returns:
            Tuple of lists containing reviews sorted by sentiment

        """
    try:
        infile = open(fileName, "r")
        ls = infile.readlines()
    except IOError:
        print 'Not a valid file name'
        return
    pos_list = []
    neg_list = []

    for str in ls:
        if str[len(str) - 2] == '1':  # if positive review
            pos_list.append(str[:len(str) - 3])
        elif str[len(str) - 2] == '0':  # if negative review
            neg_list.append(str[:len(str) - 3])
        else:
            print str  # any case that didn't have a number
    return pos_list, neg_list


def cleanData(myData):
    """
        Args:
            List of reviews to be cleaned

        Returns:
            Same list but all reviews cleaned grammatically

        """
    for i in range(0, len(myData)):
        myData[i] = myData[i].lower()
        myData[i] = re.sub('[^A-Za-z0-9-\']+', ' ', myData[i])  # removing special characters w/o apostrophe & hyphen
        myData[i] = re.sub('--', ' ', myData[i])  # removing double hyphen, must do first to not catch singles
        # replace with space
        myData[i] = re.sub('[-]', '', myData[i])  # removing hyphen no replacement

    for i in range(0, len(myData)):
        words = myData[i].split(' ')
        full_new_string = ''
        for str in words:
            new_str = ''
            matched = False
            match = re.match(r"([a-z']+)([0-9]+)([a-z']+)", str, re.I)
            if not match:  # do nothing for numbers in middle
                match = re.match(r"([0-9]+)([a-z']+)([0-9]+)", str, re.I)  # matching other cases as nums on both ends
                if match:
                    new_str += 'num ' + match.groups()[1] + ' num'
                    matched = True
                else:
                    match = re.match(r"([0-9]+)([a-z']+)", str, re.I)
                    if match:
                        new_str += 'num ' + match.groups()[1]
                        matched = True
                    else:
                        match = re.match(r"([a-z']+)([0-9]+)", str, re.I)
                        if match:
                            new_str += match.groups()[0] + ' num'
                            matched = True
            else:
                new_str += match.groups()[0] + match.groups()[1] + match.groups()[2]  # adding words w/ #'s in middle
                matched = True
            if matched:
                full_new_string += new_str + ' '
            else:
                full_new_string += str + ' '
        myData[i] = full_new_string.strip()

    for i in range(0, len(myData)):
        myData[i] = re.sub(r'\b\d+\b', 'num', myData[i])  # replaces lone numbers with token 'num'

    # now that all numbers are separated we can replace consecutive nums

    for i in range(0, len(myData)):  # elimination repetitive nums
        words = myData[i].split(' ')
        previous_num = False
        new_str = ''
        for word in words:
            if word == '':
                continue
            if word == 'num':
                if not previous_num:
                    new_str += 'num '
                    previous_num = True
            else:
                previous_num = False
                new_str += word + ' '
        myData[i] = new_str
        myData[i] = re.sub(r'\s[2]', '', myData[i])
    return myData


def calculateUniqueWordsFreq(trainData, cutOff):
    """Calculates frequency of each unique word in the give list of reviews

        Args:
            trainData (list): List of reviews for analysis.
            cutOff (int): Will remove the top (cutOff) frequency words from the dictionary, often includes words such
            as 'a' 'and' and 'the'.

        Returns:
            A dictionary with keys of each unique word and the value corresponding to the frequency in all reviews.

        """
    if cutOff < 0:
        print 'Invalid Cutoff'
        return
    words_freq = {}
    for i in range(len(trainData)):
        arr = trainData[i].split(' ')
        for word in arr:
            if word == '' or word == ' ' or word == '  ':
                continue
            if word in words_freq:
                words_freq[word] += 1
            else:
                words_freq[word] = 1

    for i in range(0, cutOff):
        v = list(words_freq.values())
        k = list(words_freq.keys())
        del words_freq[k[v.index(max(v))]]  # index of max value, find the key for it, and remove from dictionary
    return words_freq


def calculateClassProbability(posTrain, negTrain):
    """Calculates probability scores to be used in the next method

        """
    return float(len(posTrain))/(len(posTrain) + len(negTrain)), float(len(negTrain))/(len(posTrain) + len(negTrain))


def calculateScores(classProb, uniqueVocab, testData):
    """Calculates probability scores based on a give formula to design positive and negative models

        Args:
            classProb (float): Calculated in previous method.
            uniqueVocab (dict): Unique words frequency dictionary.
            testData (list): List of reviews for scores to be calculated from

        Returns:
            list: list of scores for each review.

        """
    review_scores = []
    values = uniqueVocab.values()
    division_factor = len(uniqueVocab) + sum(values)  # denominator of formula
    for review in testData:
        word_score_list = []
        arr = review.split(' ')  # access each word
        for str in arr:
            if str in uniqueVocab:
                word_freq = uniqueVocab[str]
            else:
                word_freq = 0
            word_score_list.append(float(word_freq + 1)/division_factor)
        review_score = classProb
        for i in word_score_list:
            review_score *= i
        review_scores.append(review_score)
    return review_scores


def calculateAccuracy(positiveTestDataPositiveScores, positiveTestDataNegativeScores,
                      negativeTestDataPositiveScores, negativeTestDataNegativeScores):
    """Designed to be used for the testing data given for determining how well the models performed. Takes in positive
    and negative reviews run against the positive and negative models and determines which score was higher. Also
    reports the correctness of the results. (Implemented in main method)

        """
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    for i in range(len(positiveTestDataNegativeScores)):
        if positiveTestDataPositiveScores[i] >= positiveTestDataNegativeScores[i]:
            tp += 1
        else:
            fp += 1
    for i in range(len(negativeTestDataNegativeScores)):
        if negativeTestDataNegativeScores[i] > negativeTestDataPositiveScores[i]:
            tn += 1
        else:
            fn += 1
    return tp, fp, tn, fn


def demo(review):
    """Determines the sentiment of any given review.

        Args:
            review (str): review given for analysis

        Returns:
            int: Represents the sentiment determined by testing the review against positive and negative models

        .. _PEP 484:
            https://www.python.org/dev/peps/pep-0484/

        """
    tup = readAndDivideBySentiment("TRAINING.txt")
    cleanData(tup[0])
    cleanData(tup[1])
    pos_train_unique = calculateUniqueWordsFreq(tup[0], 3)
    neg_train_unique = calculateUniqueWordsFreq(tup[1], 3)
    class_prob = calculateClassProbability(tup[0], tup[1])
    review_list = [review]
    cleanData(review_list)
    pos_scores = calculateScores(class_prob[0], pos_train_unique, review_list)
    neg_scores = calculateScores(class_prob[1], neg_train_unique, review_list)
    if pos_scores[0] > neg_scores[0]:
        return 1
    return -1


def main():
    tup = readAndDivideBySentiment("TRAINING.txt")
    tup_test = readAndDivideBySentiment("TESTING.txt")
    cleanData(tup[0])
    cleanData(tup[1])
    cleanData(tup_test[0])
    cleanData(tup_test[1])
    # for i in tup[1]:
    #     print i
    review = ' '
    print 'To exit, press enter at any time'
    review = raw_input('Enter a sample review: \n')
    while len(review) > 0:
        if demo(review) == 1:
            print 'Positive'
        if demo(review) == -1:
            print 'Negative'
        review = raw_input('Enter a sample review: \n')

    pos_train_unique = calculateUniqueWordsFreq(tup[0], 10)
    neg_train_unique = calculateUniqueWordsFreq(tup[1], 10)

    class_prob = calculateClassProbability(tup[0], tup[1])

    pos_pos = calculateScores(class_prob[0], pos_train_unique, tup_test[0])  # positive data positive model
    pos_neg = calculateScores(class_prob[1], neg_train_unique, tup_test[0])  # positive data negative model
    neg_neg = calculateScores(class_prob[1], neg_train_unique, tup_test[1])
    neg_pos = calculateScores(class_prob[0], pos_train_unique, tup_test[1])

    print 'Accuracy calculated for TESTING.txt data: (In the form true positive, false positive, true negative, ' \
          'false negative)'
    print calculateAccuracy(pos_pos, pos_neg, neg_pos, neg_neg)


main()

