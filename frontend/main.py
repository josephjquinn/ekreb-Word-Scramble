# Joseph Quinn

# This Python GUI game is a Word Scramble Game that challenges players to unscramble words within a time limit.
# Players earn points based on the length of the unscrambled word, bonus points for solving quickly,
# and lose points for using hints. The game also features options for customizing the gameplay
# and a high score leaderboard.

# using python 3.10 with customtkinter for my graphical interface

# import packages
from charset_normalizer import md__mypyc
import customtkinter
import time
import json
import requests

# api target urls
session_url = 'http://localhost:3000/session'
test_api_url = 'http://localhost:3000/'
post_api_url = 'http://localhost:3000/check-word'
accuracy_url = 'http://localhost:3000/accuracy'
hint1_url = 'http://localhost:3000/hint-1'
hint2_url = 'http://localhost:3000/hint-2'
hint3_url = 'http://localhost:3000/hint-3'
leaderboard_update_url = 'http://localhost:3000/update-leaderboard'
leaderboard_get_url = 'http://localhost:3000/get-leaderboard'
solution_url = 'http://localhost:3000/get-solution'


# game description
game_rules_text = """
Word Scramble Game Rules

Objective:
Your goal is to unscramble a scrambled word within a limited time frame and earn as many points as possible.

Gameplay:
1. You will be presented with a scrambled word.
2. You have 8 guesses to unscramble the word correctly.
3. The game is timed, so you must solve the word as quickly as possible.

Scoring:
- You earn points based on the length of the unscrambled word multiplied by 3.
- If you solve the word in under 5 seconds, you receive a bonus of 15 points.
- If you solve the word in between 5 and 10 seconds, you receive a bonus of 10 points.
- If you solve the word in between 10 and 15 seconds, you receive a bonus of 5 points.
- If you take over 15 seconds to solve the word, you do not receive any bonus points.

Game Accuracy Rating:
- Completion %: This shows how many rounds you've successfully completed out of the total rounds played. 
  The higher this number, the better your progress in the game.
- Round Accuracy %: This measures how accurate your word guesses are for the current round. 
  It's given as a percentage, where higher percentages indicate more accurate guesses.
- Game Accuracy %: This is an average of your accuracy in all the rounds you've played so far. 
  It provides an overall measure of how well you're doing in the game.


Hints:
You can use hints to help you unscramble the word, but they come at a cost to your overall score:
- Hint 1: Reveals the part of speech of the word (-1 point).
- Hint 2: Reveals the starting letter of the word (-2 points).
- Hint 3: Provides the definition of the word (-4 points).

High Score Leaderboard:
Don't forget to check the High Score Leaderboard tab! Compete with other players and see if you can claim the top spot by earning the highest score in the Word Scramble Game.

Options:
- Dark Mode Switch: This switch allows the player to toggle between dark mode and light mode.
- Username Entry Field: This field allows the player to enter their username or player name.
- Letter Count Dropdown: The player can choose a letter count from 3 to 6. This setting determines the word length of the word in the game.
- WordCode Checkbox: This checkbox enables or disables the display of the position data for each guess (-)incorrect position, (*)correct position
- Similarity:This checkbox enables or disables the display of a percentage indicating how similar the player's guessed word is to the correct word.
- Start: This button initiates the start of the Word Scramble Game.

Winning:
- Your final score is the sum of the points you earn for unscrambling the word, plus any bonus points and minus the points deducted for using hints.
- Try to achieve the highest score possible to compete with yourself and others.

Game Over:
- The game is over when you either solve the word or exhaust all 8 guesses without unscrambling the word.

Strategy Tips:
- Use hints strategically when you're stuck, but be mindful of the point deductions.
- Try to solve words quickly to earn time-based bonus points.
- Practice and build your vocabulary to improve your unscrambling skills.

Are you ready to unscramble some words and earn points? Let's start the Word Scramble Game!
"""

# setting default values for GUI appearance
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("blue")

# setting up window size, window name, window configuration(grid), creating window frames, and creating frame widgets
class App(customtkinter.CTk):
    def __init__(self):

        super().__init__()
        self.title("WordScramble.py")
        self.geometry("930x650")

# initializing API and resetting variables (round, complete, round_accuracy_percents)
        self.connectAPI()


        self.grid_columnconfigure((0,1, 2, 3), weight=1, uniform ='a')
        self.grid_rowconfigure((0,2, 3), weight=1, uniform = 'b')
        self.grid_rowconfigure((1), weight=0)

        self.game_frame = customtkinter.CTkFrame(self)
        self.game_frame.grid(row=2, rowspan = 2,column=1, columnspan=2, sticky="nsew")

        self.hints_frame = customtkinter.CTkFrame(self)
        self.hints_frame.grid(row=1, column=3, rowspan=2, sticky="nsew")


        self.title_label = customtkinter.CTkLabel(self, text="Scramble!", font=customtkinter.CTkFont(size=75, weight="bold"))
        self.title_label.grid(row = 0, column= 2, columnspan=2, sticky ="w")

        self.target_label = customtkinter.CTkLabel(self, text="Word ",font=customtkinter.CTkFont(size=75, weight="bold"))
        self.target_label.grid(row=0, column=1, columnspan=1, sticky="e")

        self.entry = customtkinter.CTkEntry(self, placeholder_text="Guess: ", corner_radius=10, font=customtkinter.CTkFont(size=30))
        self.entry.grid(row=1,  column=1,sticky="new")
        self.entry.configure(state="disabled")
        self.entry.bind('<Return>', self.word_input)

        self.turns_label = customtkinter.CTkLabel(self, text="#", font=customtkinter.CTkFont(size=50))
        self.turns_label.grid(row = 1, column = 2)

        self.tabView = customtkinter.CTkTabview(self)
        self.tabView.grid(row=0, column=0, rowspan=4, columnspan =1, sticky="nsew")
        self.tabView.add("Options")
        self.tabView.add("Rules")
        self.tabView.add("Leaderboard")

        mode = customtkinter.StringVar(value="light")
        self.dark_switch = customtkinter.CTkSwitch(self.tabView.tab("Options"), text="Dark Mode", font=customtkinter.CTkFont(size=20), command=self.switch_event, variable=mode, onvalue="dark", offvalue="light")
        self.dark_switch.pack(padx=20, pady=20)

        self.username_entry = customtkinter.CTkEntry(self.tabView.tab("Options"), placeholder_text="Username", corner_radius=20, font=customtkinter.CTkFont(size=20))
        self.username_entry.pack(padx=20, pady=(10))

        self.letter_count_label = customtkinter.CTkLabel(self.tabView.tab("Options"), text="# of Letters", font=customtkinter.CTkFont(size=20))
        self.letter_count_label.pack(padx=20, pady=(10,0))

        self.letter_count = customtkinter.CTkOptionMenu(self.tabView.tab("Options"), values=["3", "4", "5", "6"], command=self.change_letter_count)
        global letter_count
        letter_count = 3
        self.letter_count.pack()

        self.wordcode_checkbox = customtkinter.CTkCheckBox(self.tabView.tab("Options"), text="WordCode", font=customtkinter.CTkFont(size=15))
        self.wordcode_checkbox.pack(padx=55, pady=(25,5), anchor="w")

        self.similarity_checkbox = customtkinter.CTkCheckBox(self.tabView.tab("Options"), text="Similarity %",font=customtkinter.CTkFont(size=15))
        self.similarity_checkbox.pack(padx=55, anchor="w")

        self.rules_text = customtkinter.CTkTextbox(self.tabView.tab("Rules"), height=550, width=400, wrap="word")
        self.rules_text.insert("0.0", game_rules_text)
        self.rules_text.configure(state="disabled")
        self.rules_text.pack()

        self.leaderboard_label = customtkinter.CTkLabel(self.tabView.tab("Leaderboard"),font=customtkinter.CTkFont(size=20, weight="bold"))
        self.leaderboard_label.pack(pady=60)
        self.print_leaderboard()

        self.start_button = customtkinter.CTkButton(self.tabView.tab("Options"), text = "Start Game", command=self.start_button, font=customtkinter.CTkFont(size=25, weight="bold"), corner_radius=20, height=60)
        self.start_button.pack(padx=20, pady=20)

        self.hint1 = customtkinter.CTkButton(self.hints_frame, text="Hint 1", command=self.hint1, state="disabled")
        self.hint1.pack(padx=20, pady=(25, 5))

        self.hint2 = customtkinter.CTkButton(self.hints_frame, text="Hint 2", command=self.hint2, state="disabled")
        self.hint2.pack(padx=20, pady=5)

        self.hint3 = customtkinter.CTkButton(self.hints_frame, text="Hint 3", command=self.hint3, state="disabled")
        self.hint3.pack(padx=20, pady=5)

        self.game_frame.grid_columnconfigure((0), weight=1, uniform = 'b')
        self.game_frame.grid_rowconfigure((0), weight=0, uniform = 'd')

        self.points_view = customtkinter.CTkTabview(self)
        self.points_view.grid(column=3, row=3, sticky="nsew")
        self.points_view.add("Score")
        self.points_view.add("Recent")
        self.points_label = customtkinter.CTkLabel(self.points_view.tab("Score"), text="Score:", font=customtkinter.CTkFont(size=40, weight="bold"))
        self.points_label.pack(padx=20, pady=(10, 0))

        self.completion_percent_label = customtkinter.CTkLabel(self.points_view.tab("Recent"), text="Completion: ", font=customtkinter.CTkFont(size=20))
        self.completion_percent_label.grid(row=0, column=0)
        self.game_accuracy_percent_label = customtkinter.CTkLabel(self.points_view.tab("Recent"),text="Game Accuracy: ", font=customtkinter.CTkFont(size=20))
        self.game_accuracy_percent_label.grid(row=2, column=0)
        self.round_accuracy_percent_label = customtkinter.CTkLabel(self.points_view.tab("Recent"), text="Round Accuracy: ", font=customtkinter.CTkFont(size=20))
        self.round_accuracy_percent_label.grid(row=1, column=0)

        self.hint1Label = customtkinter.CTkLabel(self.hints_frame, font=customtkinter.CTkFont(size=15))
        self.hint2Label = customtkinter.CTkLabel(self.hints_frame, font=customtkinter.CTkFont(size=15))
        self.hint3Label = customtkinter.CTkLabel(self.hints_frame, font=customtkinter.CTkFont(size=15))

# application function. Setting initial values for buttons & entry boxes
    def run_game(self):
        global running
        global start_time
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.turns_label.configure(text = int(elapsed_time))
        if running == True:
            self.after(1000, self.run_game)
            self.entry.configure(state="normal")
            self.start_button.configure(state="disabled")
            self.hint1.configure(state="normal")
            self.hint2.configure(state="normal")
            self.hint3.configure(state="normal")
        else:
            self.entry.configure(state="disabled")
            self.start_button.configure(state="normal")
            self.hint1.configure(state="disabled")
            self.hint2.configure(state="disabled")
            self.hint3.configure(state="disabled")


# function to retrieve scrambled word from API
    def get_word(self):
        api_url = 'http://localhost:3000/get-word'
        global letter_count
        letter = letter_count
        data = {'letters': letter}
        try:
            response = requests.post(api_url, data=data)
            if response.status_code == 200:
                word = response.json()['word']
            else:
                print(f'Error: Received status code {response.status_code} from the API.')

        except requests.exceptions.RequestException as e:
            print(f'Error: Failed to connect to the API: {e}')
        return word


# function to check solution through API. Returns correctness boolean, position_data, and similarity %
    def check_word(self, input_word):
        global position_data
        global similarity

        data = {'word': input_word}

        try:
            response = requests.post(post_api_url, data=data)

            if response.status_code == 200:
                result = response.json()['result']
                position_data = response.json()['score']['code']
                similarity = response.json()['score']['similarity']
                if result == "correct":
                    return True
                else:
                    return False
            else:
                print(f'Error: Received status code {response.status_code} from the API.')

        except requests.exceptions.RequestException as e:
            print(f'Error: Failed to connect to the API: {e}')


# function that starts the game after use presses the start button
    def start_button(self):
        if self.username_entry.get() == "":
            self.warning_label = customtkinter.CTkLabel(self.game_frame, text="Enter Username", text_color="red", font=customtkinter.CTkFont(size=20, weight="bold"))
            self.warning_label.grid(row=0, column=0)
        else:
            if self.check_api_connection():
                self.target_label.configure(text_color="DodgerBlue4", font=customtkinter.CTkFont(size=75, weight="bold"))
                for i in range(10):
                    self.guess_label = customtkinter.CTkLabel(self.game_frame, text=(""))
                    self.guess_label.grid(row=i, column=0, sticky="nsew")
                global guess_number
                guess_number = 0
                global running
                running = True
                global start_time
                start_time = time.time()
                global start_word
                start_word = self.get_word()
                self.title_label.configure(text="")
                self.target_label.configure(text=start_word + " ")
                self.target_label.grid(columnspan=3, sticky="nsew")
                global count
                count = 1
                global h1, h2, h3
                h1 = False
                h2 = False
                h3 = False
                self.run_game()


# function to return hint 1 data from API
    def hint1(self):
        global h1
        speech_type=''
        try:
            response = requests.get(hint1_url)
            if response.status_code == 200:
                speech_type = response.json()['partOfSpeech']
            else:
                print(f'Error: Received status code {response.status_code} from the API.')
                speech_type = "Unknown"
        except requests.exceptions.RequestException as e:
            print(f'Error: Failed to connect to the API: {e}')
        self.hint1Label.configure(text="Speech: "+speech_type)
        self.hint1Label.pack(pady=2)
        h1 = True


# function to return hint 2 data from API
    def hint2(self):
        global h2
        try:
            response = requests.get(hint2_url)
            if response.status_code == 200:
                first_letter = response.text
            else:
                print(f'Error: Received status code {response.status_code} from the API.')
        except requests.exceptions.RequestException as e:
            print(f'Error: Failed to connect to the API: {e}')
        self.hint2Label.configure(text="The first letter is " + first_letter)
        self.hint2Label.pack()
        h2 = True


# function to return hint 3 data from API
    def hint3(self):
        global h3
        definition = ""
        try:
            response = requests.get(hint3_url)
            if response.status_code == 200:
                result = response.json()['definition']
                definition = result
            else:
                print(f'Error: Received status code {response.status_code} from the API.')
                definition = "No definition available "
        except requests.exceptions.RequestException as e:
            print(f'Error: Failed to connect to the API: {e}')
        self.hint3Label.configure(text=definition, wraplength= 175)
        self.hint3Label.pack()
        h3 = True


# enables dark mode switch functionality
    def switch_event(self):
        customtkinter.set_appearance_mode(self.dark_switch.get())


# enables letter count selection function
    def change_letter_count(self, selection):
        global letter_count
        letter_count = selection

# function that runs everytime user presses enter, it will process user guess
    def word_input(self, event = None):
        global guess_number
        global letter_num
        global running
        global start_word
        global count
        global complete
        word = self.entry.get()
        if len(word) == len(start_word):
            letter_num= True
            if running:
                guess_number = guess_number + 1
                self.entry.delete(0, 'end')
                if (self.check_word(word)):
                    complete = True
                    running = False
                    self.postGame()
                    return
                self.write_word(word)
                if count >= 8:
                    complete = False
                    running = False
                    self.postGame()
                count += 1
        else:
            letter_num = False
            self.write_word("Wrong number of letters")

# function to write string parameter to game screen, also includes position_data and similarity % if boxes are checked
    def write_word(self, text):
        global letter_num
        global count
        global similarity
        global position_data
        information= ""
        if self.similarity_checkbox.get() == 1 & letter_num == True:
            information = information + "[" +similarity + "] "
        if self.wordcode_checkbox.get() == 1 & letter_num == True:
            information = information + position_data + " "
        self.guess_label = customtkinter.CTkLabel(self.game_frame, text=(text + " " + information), font=customtkinter.CTkFont(size=30))
        self.guess_label.grid(row=count, column=0, sticky="nsew")


# funtion that runs after round completion, displays score and recent round data
    def postGame(self):
        global complete
        global scramble
        global guess_number

        scramble = self.target_label.cget("text")

        self.hint1Label.configure(text="")
        self.hint2Label.configure(text="")
        self.hint3Label.configure(text="")

        if complete:
            self.accuracy(guess_number)
            self.write_word(self.get_solution())
            self.target_label.configure(text_color="green")
            self.target_label.configure(text=scramble + " -> " + self.get_solution())
            self.points_label.configure(text="Score: \n" + self.score())
            self.update_leaderboard()
            self.print_leaderboard()

        else:
            self.accuracy(guess_number)
            self.target_label.configure(text_color="red", font=customtkinter.CTkFont(size=40, weight="bold"), text="No More Guesses\n" + scramble + " -> " + self.get_solution())


# calculates score
    def score(self):
        global h1, h2, h3, start_word

        hint_score = 0
        time_score = 0
        word_score = 0

        word_length = len(start_word)
        word_score = word_length*3

        time = self.turns_label.cget("text")
        if time < 5:
            time_score = 15
        elif 5<time<10:
            time_score = 10
        elif 10<time<15:
            time_score = 5
        elif time > 15:
            time_score = 0

        if h1:
            hint_score = hint_score - 1
        if h2:
            hint_score = hint_score - 2
        if h3:
            hint_score = hint_score - 4

        score = word_score + time_score + hint_score
        return str(score)


# function that contacts API to return accuracy % data
    def accuracy(self, guess_attempts):
        data = {'guess_attempts': guess_attempts}

        try:
            response = requests.post(accuracy_url, data=data)
            if response.status_code == 200:
                completion_percent = response.json()['completion']
                round_accuracy = response.json()['round_accuracy']
                game_accuracy = response.json()['game_accuracy']

                self.completion_percent_label.configure(text="Completion: {}%".format(round(completion_percent)))
                self.round_accuracy_percent_label.configure(text="Round Accuracy: {}% ".format(round(round_accuracy)))
                self.game_accuracy_percent_label.configure(text="Game Accuracy: {}%".format(round(game_accuracy)))

            else:
                print(f'Error: Received status code {response.status_code} from the API.')

        except requests.exceptions.RequestException as e:
            print(f'Error: Failed to connect to the API: {e}')


# function to convert leaderboard (name/score) data into malleable array
    def read_high_scores(self, filename):
        try:
            with open(filename, 'r') as file:
                high_scores = [line.strip().split(", ") for line in file.readlines()]
                return high_scores
        except FileNotFoundError:
            return []


# function to return the solution for each round <<-- (DISPLAY PURPOSES NOT UTILIZED FOR GAME LOGIC)
    def get_solution(self):
        try:
            response = requests.get(solution_url)
            if response.status_code == 200:
                return(response.text)
            else:
                print(f'Error: Received status code {response.status_code} from the API.')
        except requests.exceptions.RequestException as e:
            print(f'Error: Failed to connect to the API: {e}')


# function to get leaderboard information from API and print to GUI
    def print_leaderboard(self):
        leaderboard_txt = ""
        try:
            response = requests.get(leaderboard_get_url)
            if response.status_code == 200:
                response = response.text
                data = json.loads(response)
                leaderboard_list = data["leaderboard"].split('\n')
                for entry in leaderboard_list:
                    leaderboard_txt = leaderboard_txt + entry + ('\n')
            else:
                print(f'Error: Received status code {response.status_code} from the API.')
        except requests.exceptions.RequestException as e:
            print(f'Error: Failed to connect to the API: {e}')
        self.leaderboard_label.configure(text=leaderboard_txt)


# function to update the API leaderboard with current round score and username date
    def update_leaderboard(self):
        data = {"username": str(self.username_entry.get()),
                "newScore": int(self.score())
                }
        try:
            response = requests.post(leaderboard_update_url, json=data)  # Use json=data to send data as JSON
            if response.status_code == 200:
                print("Leaderboard Updated")
            else:
                print(f'Error: Received status code {response.status_code} from the API.')
                print(f'Response content: {response.text}')

        except requests.exceptions.RequestException as e:
            print(f'Error: Failed to connect to the API: {e}')


# verifies API connection
    def check_api_connection(self):
        try:
            response = requests.get(test_api_url)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f'Error: Failed to connect to the API: {e}')
            self.warning_label = customtkinter.CTkLabel(self.game_frame, text="API Server Not Running", text_color="red",font=customtkinter.CTkFont(size=20, weight="bold"))
            self.warning_label.grid(row=0, column=0)
            return False


# another API connection verification, used to initialize variables on the backend server
    def connectAPI(self):
        try:
            response = requests.get(session_url)
            if response.status_code == 200:
                print("Operational")
        except requests.exceptions.RequestException as e:
            print(f'Error: Failed to connect to the API: {e}')


# refresh for dual-running scripts
def refresh(self):
        self.update()
        self.after(1000, self.refresh)


# main loop
if __name__ == "__main__":
    app = App()
    app.mainloop()
