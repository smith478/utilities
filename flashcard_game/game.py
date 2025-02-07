import random
import time

def get_max_number():
    while True:
        try:
            max_num = int(input("Enter the highest number to use (e.g., 10): "))
            if max_num < 1:
                print("Please enter a number greater than 0.")
            else:
                return max_num
        except ValueError:
            print("Please enter a valid number.")

def main():
    print("\nWelcome to Math Flash Cards! 🚀")
    print("Answer the problems. Type 'quit' to exit.\n")
    max_num = get_max_number()
    score = 0

    correct_messages = [
        "🌟 Awesome! You're a math star!",
        "🎉 Correct! Way to go!",
        "👍 Perfect! You nailed it!",
        "👏 Great job! Keep it up!",
        "💯 Nailed it! Math champion!",
        "✨ Wow! You're on fire!"
    ]

    incorrect_messages = [
        "😬 Oops! Try another one!",
        "❌ Not quite, but nice try!",
        "🤔 Close! You'll get the next one!",
        "💪 Keep going! Practice makes perfect!",
        "📚 Review time! Let's try again!",
        "🍀 Don't worry! You've got this!"
    ]

    print("\nLet's start! (Faster answers = higher scores)\n" + "-"*40)

    while True:
        # Choose operation
        operation = random.choice(['+', '-'])
        if operation == '+':
            num1 = random.randint(0, max_num)
            num2 = random.randint(0, max_num)
            answer = num1 + num2
        else:
            num1 = random.randint(1, max_num)
            num2 = random.randint(0, num1)
            answer = num1 - num2

        # Present problem
        problem = f"➡️   {num1} {operation} {num2} = ? "
        print(problem)
        start_time = time.time()
        user_input = input().strip().lower()
        end_time = time.time()

        if user_input == 'quit':
            print(f"\nGame over! Your final score is {score}. 🏁")
            print("Thanks for playing! Come back soon! 😊\n")
            break

        try:
            user_answer = int(user_input)
            time_taken = end_time - start_time

            if user_answer == answer:
                # Calculate score based on time (faster = higher score)
                base_score = 10
                time_bonus = max(0, 5 - int(time_taken))  # Bonus for quick answers
                problem_score = base_score + time_bonus
                score += problem_score

                print(f"\n{random.choice(correct_messages)}")
                print(f"Time: {time_taken:.1f} seconds")
                print(f"Score: +{problem_score} (Total: {score}) 🌈\n" + "-"*40)
            else:
                print(f"\n{random.choice(incorrect_messages)}")
                print(f"The correct answer was: {answer}")
                print(f"Time: {time_taken:.1f} seconds")
                print(f"Current Score: {score} 💪\n" + "-"*40)
        except ValueError:
            print("\n🛑 Please enter a number or 'quit'\n" + "-"*40)

if __name__ == "__main__":
    main()