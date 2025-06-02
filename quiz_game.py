import time
import json
import threading
import os
import sounds
import sys
from sounds import play_correct_sound, play_wrong_sound, play_welcome_sound
from inputimeout import inputimeout, TimeoutOccurred

# Load questions from JSON file
def load_questions(filename):
    try:
        with open(filename, 'r') as file:
            questions_data = json.load(file)
            return questions_data
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file {filename} is not valid JSON.")
        return []

# Load questions at the start
questions = load_questions('quiz_questions.json')


# Display function
def display_welcome():
    print("****************************************************")
    print("*                                                   *")
    print("*           WELCOME TO THE QUIZ GAME!              *")
    print("*                                                   *")
    print("****************************************************")
    print("\n")
    print("Test your knowledge and win!")
    print("Here's how to play: ")
    print("- You will be presented with Multiple Choice Questions, Or Open-ended questions, Or a simple True/False question.")
    print("- If it's an MCQ, Choose your answer by entering your desired option")
    print("- If it's a True/False question, Choose either True or False")
    print("- If it's an Open-ended question, please type your answer")
    print("- The game will keep track of your score ")
    print("- You can attempt as many questions as you want")

    print(f"\nWelcome {user_name}, Let's get ready to begin yeah? ")
    time.sleep(1)

user_name = input("Enter your name for the high score list: ").strip() or "Player"


def get_questions_by_difficulty(questions, difficulty):
    return [q for q in questions if q['difficulty'] == difficulty]


def calculate_score(base_points, difficulty):
    multipliers = {
        'easy': 1,
        'medium': 1.5,
        'hard': 2
    }
    return int(base_points * multipliers[difficulty])


def display_difficulty_feedback(difficulty):
    messages = {
        'easy': "You've chosen the easy mode. Perfect for beginners!",
        'medium': "Medium mode it is. Let's test your knowledge!",
        'hard': "You're brave! The hard mode awaits."
    }
    print(messages[difficulty])


def select_difficulty():
    print("\nSelect your difficulty level:")
    print("1. Easy")
    print("2. Medium")
    print("3. Hard")
    
    while True:
        choice = input("Enter your choice (1/2/3): ")
        if choice in ['1', '2', '3']:
            difficulty = ['easy', 'medium', 'hard'][int(choice) - 1]
            return difficulty
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def play_game(questions):
    score = 0
    for question in questions:
        print("\n" + "="*20 + "\n")
        print(question["question"])

        user_ans = get_user_answer(question)

        q_type = question['type']
        correct_answer = question['correct']

        if q_type == 'multiple-choice':
            correct = (user_ans == correct_answer)
        elif q_type == 'true/false':
            correct = user_ans is not None and user_ans.strip().lower()[0] == correct_answer.strip().lower()[0]
        elif q_type == 'open-ended':
            correct = user_ans is not None and any(user_ans.strip().lower() == ans.lower() for ans in correct_answer)
        else:
            print(f"Unknown question type: {q_type}")
            correct = False

        if correct:
            score += 1
            print("Correct answer!")
            sounds.play_correct_sound()
        else:
            print(f"Sorry, the correct answer was {correct_answer}")
            sounds.play_wrong_sound()

        total_result.append({
            "question": question["question"],
            "correct_answer": correct_answer,
            "user_answer": user_ans,
            "correct": correct
        })

    return score


def get_user_answer(question):
    q_type = question['type']
    options = question.get('options', [])
    timeout_duration = 10
    
    print("\n" + question['question'])
    if q_type == 'multiple-choice':
        print("Options:")
        for idx, option in enumerate(options):
            print(f"  {chr(65+idx)}. {option}")
        prompt = "Your answer (A/B/C/D): "
    elif q_type == 'true/false':
        print("Options: True or False")
        prompt = "Your answer (True/False): "
    else:
        prompt = "Your answer: "

    timer_expired = threading.Event()
    answer = [None]
    
    def countdown():
        for remaining in range(timeout_duration, 0, -1):
            if timer_expired.is_set():
                return
            print(f"\rTime left: {remaining} ", end="", flush=True)
            time.sleep(1)
        print("\r⏰ Time's up! Moving on to the next question...")
        timer_expired.set()
    

    def get_input():
        try:
            answer[0] = input(prompt)
            timer_expired.set()
        except:
            pass
    


    countdown_thread = threading.Thread(target=countdown)
    countdown_thread.daemon = True
    countdown_thread.start()
    
    input_thread = threading.Thread(target=get_input)
    input_thread.daemon = True
    input_thread.start()
    
    input_thread.join(timeout=timeout_duration)
    timer_expired.set()
    
    if answer[0] is not None:
        answer = answer[0].strip().upper()
        if q_type == 'multiple-choice':
            if answer in ['A', 'B', 'C', 'D'][:len(options)]:
                return answer
            print("Invalid option. Please try again.")
        elif q_type == 'true/false':
            if answer in ['TRUE', 'FALSE', 'T', 'F']:
                return answer[0]
            print("Please enter True or False.")
        else:
            return answer if answer else None
    else:
        print()
        return None


HIGH_SCORES_FILE = "high_scores.json"

def load_high_scores():
    if not os.path.exists(HIGH_SCORES_FILE):
        return []
    with open(HIGH_SCORES_FILE , "r") as file:
        content = file.read().strip()
        if not content:
            return []
        return json.loads(content)
    

def save_high_scores(scores):
    with open(HIGH_SCORES_FILE , "w") as file:
        json.dump(scores , file , indent = 4)


def add_high_scores(name, score):
    scores = load_high_scores()
    scores.append({"name" : name , "score" : score})
    scores.sort(key = lambda x: x["score"] , reverse = True)
    top_10 = scores[:10]
    save_high_scores(top_10)
    return top_10

def display_high_scores():
    scores = load_high_scores()
    if not scores:
        print("No high scores yet!")

    print("\n--- High Scores ---")
    for index , score in enumerate(scores , 1):
        print(f"{index}. {score['name']} - {score['score']} points")


def game_end(score):
    print("\nGame Over!")
    print(f"Your final score: {score}")
    
    save_score = input("Would you like to save your score? (yes/no): ")

    if save_score.lower() == "yes":
        name = input("Enter your name: ")
        add_high_scores({"name": name, "score": score})
        print("Score saved successfully!")
    display_high_scores()


total_result = []

def display_results(score):
    total_questions = len(total_result)
    if total_questions == 0:
        print("No results yet!")
        return

    total_correct = sum(1 for result in total_result if result["correct"])
    accuracy = (total_correct / total_questions) * 100

    print("\n--- Final Results ---")
    print(f"Total Questions: {total_questions}")
    print(f"Total Correct: {total_correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Final Score: {score}\n")

    print("Question-by-Question Results:")
    for i, result in enumerate(total_result, 1):
        question = result['question']
        correct_answer = result['correct_answer']
        user_answer = result['user_answer']
        is_correct = result['correct']

        print(f"\nQuestion {i}:")
        print(f"Question: {question}")
        print(f"Your Answer: {user_answer}")
        print(f"Correct Answer: {correct_answer}")
        print(f"Result: {'Correct' if is_correct else 'Incorrect'}")


def main():
    play_welcome_sound()
    display_welcome()
    total_score = 0
    total_rounds = 0
    play_again = 'y'

    while play_again.lower() == 'y':
        current_round = total_rounds + 1
        print(f"\nStarting Round {current_round}...\n")

        current_difficulty = select_difficulty()
        current_questions = get_questions_by_difficulty(questions, current_difficulty)
        display_difficulty_feedback(current_difficulty)

        current_round_score = play_game(current_questions)
        total_score += current_round_score
        total_rounds += 1

        print(f"\nRound {current_round} completed! You scored {current_round_score} points.")
        print(f"Total Score so far: {total_score} points\n")

        display_high_scores()

        play_again = input("Would you like to play another round? (y/n): ")

    print("\nThanks for playing!")
    display_high_scores()
    add_high_scores(user_name, total_score)
    game_end(total_score)
    display_results(total_score)


if __name__ == "__main__":
    main()
