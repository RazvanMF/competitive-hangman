import socket
import sys
import os
import argparse

try:
    import pyfiglet
except ImportError:
    pass


#IPV4 = socket.gethostbyname(socket.gethostname())
IPV4 = sys.argv[1] if len(sys.argv) >= 2 else '192.168.1.133'
PORT = 5585
ADDRESS = (IPV4, PORT)
FORMAT = 'utf-8'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def ActionLoop():
    print("You can send a letter, the full sentence or the command \"query\" to see what was already guessed")
    try:
        client.send("ping".encode(FORMAT))
        nrOfRounds = int(client.recv(256).decode(FORMAT))
    except:
        print(f"[ERROR] Couldn't perform communication between client and {ADDRESS[0]}:{ADDRESS[1]}. "
              f"Closing connection...")
        client.close()
        return

    localround = 1
    while localround <= nrOfRounds:
        roundIsWon = False
        print(f"-------ROUND {localround}-------\n")
        try:
            codedSentence = client.recv(256).decode(FORMAT)
            print(codedSentence)
        except:
            print(f"[ERROR] Couldn't receive coded sentence from server {ADDRESS[0]}:{ADDRESS[1]}. "
                  f"Closing connection...")
            client.close()
            return

        while not roundIsWon:
            letterOrSentence = ""
            while (letterOrSentence == ""):
                letterOrSentence = input(">").lower()
            try:
                client.send(letterOrSentence.encode(FORMAT))
            except:
                print(f"[ERROR] Couldn't send message to server {ADDRESS[0]}:{ADDRESS[1]}. "
                      f"Closing connection...")
                client.close()
                return

            try:
                guessOption = client.recv(1).decode(FORMAT)
                guessOutput = client.recv(256).decode(FORMAT)
                if (guessOption == "~"):
                    print(guessOutput)
                elif (guessOption == "Y"):
                    print(f"You've correctly guessed the word!")
                    roundIsWon = True
                elif (guessOption == "N"):
                    print(f"Someone else guessed the word before you.")
                    roundIsWon = True
                else:
                    print(guessOption)
                    roundIsWon = True
            except:
                print(f"[ERROR] Couldn't receive message from server {ADDRESS[0]}:{ADDRESS[1]}. "
                      f"Closing connection...")
                client.close()
                return

        localround += 1
        print("Waiting for the other clients to finish...\n")


def driver():
    print("WELCOME TO...")
    if ("pyfiglet" in sys.modules):
        result = pyfiglet.figlet_format("COMPETITIVE HANGMAN")
        print(result)
        print("*client-side")
    else:
        print("C O M P E T I T I V E   H A N G M A N")
        print("*client-side")
        print("*install pyfiglet next time :(")

    print(f"[INFO] Trying to connect to {ADDRESS[0]}:{ADDRESS[1]}")
    try:
        client.connect(ADDRESS)
    except:
        print("[ERROR] Failure. Closing...")
        sys.exit(-1)
    print("Waiting for the other clients to join...\n")
    ActionLoop()

driver()


