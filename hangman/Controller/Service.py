from hangman.Repo.Sentence_Repo import SentenceRepo


class Service:
    def __init__(self, nr_sentences: int, nr_attempts: int, file_name: str = "sentences.txt"):
        self.__r = SentenceRepo(nr_sentences, file_name)
        self.__nr_attempts = nr_attempts
        self.__nr_tries = 0
        self.__letters_guessed = []
        self.__correct_letters = []
        self.__rounds = nr_sentences
        self.__current_round = 1

    @property
    def current_round(self):
        return self.__current_round

    @current_round.setter
    def current_round(self, value: int):
        if value > self.__rounds or value < 1:
            raise RuntimeError("Invalid round")
        self.__current_round = value

    @property
    def letters(self):
        return self.__letters_guessed

    @property
    def rounds(self):
        return self.__rounds

    @property
    def attempts(self):
        return self.__nr_attempts

    @property
    def tries(self):
        return self.__nr_tries

    @property
    def sentence(self):
        return self.__get_current_string()

    def __get_current_string_insensitive(self) -> str:
        return str(self.__r.get_current_sentence()).lower()

    def __get_current_string(self) -> str:
        return str(self.__r.get_current_sentence())

    def __get_current_letters(self) -> [str]:
        return self.__r.get_current_sentence().get_letter_list

    def get_codded_sentence(self) -> str:
        result = ""
        for letter in self.sentence:
            if letter.lower() in self.__letters_guessed or letter == ' ':
                result += letter
            else:
                result += '_'
        return result

    def attempt_guess_sentence(self, guess: str) -> bool:
        if guess.lower() == self.__get_current_string_insensitive():
            self.__correct_sentence_guess()
            return True
        self.__incorrect_sentence_guess()
        return False

    def __correct_sentence_guess(self):
        self.__nr_tries = 0
        self.__letters_guessed.clear()
        self.__correct_letters.clear()
        self.__current_round += 1

        if self.__current_round == self.__rounds + 1:
            self.game_win()
        next(self.__r)

    def __incorrect_sentence_guess(self):
        self.__nr_tries += 1
        if self.__nr_tries == self.__nr_attempts:
            self.game_over()

    def attempt_guess_letter(self, guess: str) -> bool:
        if guess in self.__get_current_letters():
            self.__correct_letter_guess(guess)
            return True
        self.__incorrect_letter_guess(guess)
        return False

    def __correct_letter_guess(self, guess: str):
        self.__letters_guessed.append(guess.lower())
        self.__correct_letters.append(guess.lower())
        self.__letters_guessed.sort()
        self.__correct_letters.sort()
        if self.__correct_letters == self.__get_current_letters():
            self.__correct_sentence_guess()

    def __incorrect_letter_guess(self, guess: str):
        self.__letters_guessed.append(guess.lower())
        self.__letters_guessed.sort()
        self.__nr_tries += 1
        if self.__nr_tries == self.__nr_attempts:
            self.game_over()

    def correct_state_letters(self):
        return self.__correct_letters

    def correct_state_sentence(self, message):
        if message.lower() == self.__get_current_string_insensitive():
            return True
        return False

    def get_all_sentences(self):
        return self.__r.get_all_sentences()

    @staticmethod
    def game_win():
        pass

    @staticmethod
    def game_over():
        pass
