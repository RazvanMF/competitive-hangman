import socket
import threading
import os
import time
import sys
import subprocess

try:
    import pyfiglet
except ImportError:
    pass

def getCurrentIP():
    output = subprocess.check_output("netsh interface ip show config name=\"Wi-Fi\" | findstr \"IP Address\"",
                                 shell=True).decode('utf-8')
    return str(output.strip().split(" ")[-1])


# region Server Parameters and Game Constants
# IPV4 = socket.gethostbyname(socket.gethostname())  # WLAN Adapter's IPV4 address
IPV4 = "192.168.1.133"
PORT = 5585  # Port on which we're listening
ADDRESS = (IPV4, PORT)  # Full address, used to bind to the server
FORMAT = 'utf-8'  # Format in which we're encoding/decoding strings
LIVES = 10
ROUNDS = 3
# endregion

# region Hangman Game Bits and Pieces
from hangman.Controller.Service import Service
serv = Service(ROUNDS, LIVES)  # hangman game itself
# endregion

# region Bookkeeping Variables (client and thread objects)
clients = list()
threads = list()
# endregion

# region Global Game Loop Variables
winnerThread = None
winnerPlayer = None
roundIsWon = False
# endregion

guessLock = threading.Lock()  # mutually exclusive lock, guards critical variables

def guessExecutor(message, localround):
    """
    Function that checks if the sent message is correct (e.g. a letter from the sentence or the full sentence)
    :param message: string sent by the client
    :param localround: current round, used to compare to the service's saved round, incremented after a full guess
    :return:
    """
    global serv
    guessLock.acquire()  # lock critical variable "hasWon"
    if len(message) == 1:
        serv.attempt_guess_letter(message)  # puts the letter in the sentence if correct
    else:
        serv.attempt_guess_sentence(message)  # checks if the sentence given is the same as the saved one

    hasWon = False
    # check for win
    if (localround != serv.current_round):  # if the sentence was discovered, service's "current_round" should
                                                # have been implemented
        hasWon = True

    guessLock.release()  # release critical variable "hasWon"
    return hasWon


def clientSideManager(connection, address, player):
    """
    Function meant to be used by a thread, handles a given client on the server side
    :param connection: client's socket, returned by the socket.accept() command
    :param address: client's IP address and port, returned by the socket.accept() command
    :param player: integer used as an ID
    """

    global clients, threads, winnerThread, winnerPlayer, roundIsWon, barrier
    localround = 1  # the client's thread holds info on the current round playing and
                    # the number of mistakes the player can do
    locallives = 3
    print(f"[INFO ON THREAD {threading.current_thread()}] {address[0]}:{address[1]} has connected to the server. "
          f"(Player {player})")

    barrier.wait()

    # region Initial Communication between Server and Client
        # server receives a ping message, to ensure that the communication between the server and client works,
        # and the server sends the number of rounds to the client
    try:
        pingMessage = connection.recv(256).decode(FORMAT)
        connection.send(str(ROUNDS).encode(FORMAT))
    except:
        print(f"[ERROR] Couldn't perform communication between server and {address[0]}:{address[1]} (Player {player}). "
              f"Closing connection...")
        connection.close()
        return
    # endregion

    # region Main Game Loop
    while localround <= ROUNDS:
        locallives = 3
        # Global variables, used by all threads. Although they should be, winnerPlayer and winnerThread are NOT
            # guarded by a lock, but they can only be set once per round, and only after roundIsWon was set, that
            # already being a critical variable
        roundIsWon = False
        winnerPlayer = None
        winnerThread = None

        # Sending the client the coded sentence, filled with the correct guessed letters
        try:
            connection.send(serv.get_codded_sentence().encode(FORMAT))
        except:
            print(f"[ERROR] Couldn't send coded sentence to client {address[0]}:{address[1]}. "
                  f"Closing connection...")
            connection.close()
            return

        # region Round Game Loop
        while not roundIsWon:
            # Edge case, when the player made 3 or more mistakes
            if (locallives <= 0):
                message = connection.recv(256).decode(FORMAT)
                connection.send("X".encode(FORMAT))
                connection.send("No more lives.".encode(FORMAT))
                break

            # Server receives a message from the client, with a letter or the full sentence
            try:
                message = connection.recv(256).decode(FORMAT)
            except:
                print(f"[ERROR] Couldn't receive message from client {address[0]}:{address[1]}. "
                      f"Closing connection...")
                connection.close()
                return

            if message:
                # Win condition, handled by the guessExecutor function
                if (message != "query" and (winnerPlayer is None and winnerThread is None)
                        and guessExecutor(message, localround)):
                    winnerPlayer = player
                    winnerThread = threading.current_thread()

                # Missed letter or sentence condition, decrements the locallives variable
                if ((len(message) == 1 and message not in serv.correct_state_letters())
                        or (len(message) != 1 and message != "query" and winnerPlayer is None)):
                    locallives -= 1

                # Server sends 2 strings, one being a 1-byte code (~/Y/N/X), and the other one being the coded sentence
                try:
                    if winnerPlayer is None and winnerThread is None:
                        connection.send("~".encode(FORMAT))
                    elif winnerThread == threading.current_thread():
                        connection.send("Y".encode(FORMAT))
                        roundIsWon = True
                    else:
                        connection.send("N".encode(FORMAT))
                        roundIsWon = True
                    connection.send((serv.get_codded_sentence() +
                                     f"\nRemaining lives: {locallives}\n").encode(FORMAT))
                except:
                    print(f"[ERROR] Couldn't send message to client {address[0]}:{address[1]}. "
                          f"Closing connection...")
                    connection.close()
                    return
        # endregion

        print(f"[INFO] Thread {threading.current_thread()} has finished a game loop. "
              f"Waiting for all threads to finish the round...")

        # to avoid deadlocks, it just works
        time.sleep(0.5)
        barrier.wait()
        time.sleep(0.5)

        localround += 1

    connection.close()
    # endregion


def listener():
    """
    Function used by a thread to listen indefinitely to anyone attempting to connect to the server
    """
    global clients, threads, server
    playerIndex = 1
    while True:
        connection, address = server.accept()
        clientThread = threading.Thread(target=clientSideManager, args=(connection, address, playerIndex))
        playerIndex += 1
        clients.append(connection)
        threads.append(clientThread)
        clientThread.start()


def driver():
    """
    Main function
    :return:
    """
    print("WELCOME TO...")
    if ("pyfiglet" in sys.modules):
        result = pyfiglet.figlet_format("COMPETITIVE HANGMAN")
        print(result)
        print("*server-side")
    else:
        print("C O M P E T I T I V E   H A N G M A N")
        print("*server-side")
        print("*install pyfiglet next time :(")

    server.listen(noOfPlayers)
    print(f"[INFO ON MAIN THREAD] Server started and listening on {IPV4}:{PORT}")
    print("[INFO] Words:")
    for sentence in serv.get_all_sentences():
        print("\t" + str(sentence))

    listenerThread = threading.Thread(target=listener)
    threads.append(listenerThread)
    listenerThread.start()
    while True:
        time.sleep(1)


# region PRE-DRIVER CODE
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # server-side socket, over TCP, via IPV4
server.bind(ADDRESS)  # assigning the address to the server

noOfPlayers = int(input("How many players are expected to join?\n>"))
barrier = threading.Barrier(noOfPlayers)
# endregion

driver()
