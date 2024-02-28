import random

from hangman.Model.Sentence import Sentence


class SentenceRepo:
    def __init__(self, nr_sentences: int, file_name: str):
        self.__sentence_list = []
        self.__nr_sentences = nr_sentences
        self.__current_sentence = 0

        self.__file_name = file_name

        self.__fill_repo()

    def __fill_repo(self):
        file = open(self.__file_name, "rt")

        lines = file.readlines()
        for index in range(self.__nr_sentences):

            line = random.choice(lines)
            while line == '\n':
                line = random.choice(lines)

            # print(line)
            self.add_sentence(Sentence(line[:-1]))

            lines.remove(line)

        file.close()

    def __getattr__(self, index: int) -> Sentence:
        """
        Returns the sentence with the given index.
        Throws runtime error: "List does not contain this many sentences".
        """
        if index > self.__nr_sentences:
            raise RuntimeError("List does not contain this many sentences")
        return self.__sentence_list[index]

    def get_current_sentence(self) -> Sentence:
        """
        Returns the current sentence.
        Throws runtime error: "List does not contain this many sentences".
        """
        return self.__getattr__(self.__current_sentence)

    def get_all_sentences(self):
        """
        Returns all sentences from the repo.
        """
        return self.__sentence_list

    def add_sentence(self, sentence: Sentence):
        """
        Adds a new sentence into repo.
        Throws runtime error: "Sentence already in repo".
        """
        for s in self.__sentence_list:
            if str(sentence) == str(s):
                raise RuntimeError("Sentence already in repo")
        self.__sentence_list.append(sentence)
        self.__nr_sentences += 1

    def __next__(self):
        """
        Increases current index.
        Throws runtime error: "Invalid next"
        """
        self.__current_sentence += 1
        if self.__current_sentence > self.__nr_sentences:
            raise RuntimeError("Invalid next")
