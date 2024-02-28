class Sentence:
    def __init__(self, sentence: str):
        self.__sentence = sentence
        self.__nr_distinct_letters = 0
        self.__letter_list = []
        self.__nr_words = 1

        self.__process_sentence()

    def __process_sentence(self):
        for letter in self.__sentence:
            if letter.lower() not in self.__letter_list and letter != ' ':
                self.__letter_list.append(letter.lower())
                self.__nr_distinct_letters += 1
            if letter == ' ':
                self.__nr_words += 1
        self.__letter_list.sort()

    @property
    def get_sentence(self):
        return self.__sentence

    @property
    def get_nr_words(self):
        return self.__nr_words

    @property
    def get_letter_list(self):
        return self.__letter_list

    @property
    def get_nr_distinct_letters(self):
        return self.__nr_distinct_letters

    def __eq__(self, other):
        return self.get_sentence == other.get_sentence

    def __str__(self):
        return self.get_sentence
