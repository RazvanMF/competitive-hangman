from hangman.Controller.Service import Service


class UI:
    def __init__(self, nr_sentences: int, nr_attempts: int, file_name: str = "sentences.txt"):
        self.__s = Service(nr_sentences, nr_attempts, file_name)

    def __main_menu(self):
        print(f"Round: {self.__s.current_round}/{self.__s.rounds}")
        print(f"Attempts: {self.__s.tries}/{self.__s.attempts}")
        print(f"Current sentence: ")
        print(self.__s.get_codded_sentence())
        print("Letters guessed:")
        print(self.__s.letters)
        print("Choice menu")
        print("1. Guess a letter (case insensitive)")
        print("2. Guess the sentence (case insensitive)")
        print("3. Pass")

    def __game_flow(self):
        while True:
            if (self.__s.attempts == self.__s.tries):
                print("You are loser.")
                return
            self.__main_menu()
            choice = input(">")
            if choice == '1':
                letter = input("Letter: ")
                self.__s.attempt_guess_letter(letter)
            elif choice == '2':
                sentence = input("Sentence: ")
                self.__s.attempt_guess_sentence(sentence)
            elif choice == '3':
                continue
            else:
                raise RuntimeError("Invalid choice")

    def run(self):
        try:
            self.__game_flow()
        except RuntimeError as e:
            print(e)
