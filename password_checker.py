"""
Password Strength Checker
Checks whether a password follows basic security rules.
"""

def check_password(password):
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Use at least 8 characters.")

    if any(char.isupper() for char in password):
        score += 1
    else:
        feedback.append("Add an uppercase letter.")

    if any(char.islower() for char in password):
        score += 1
    else:
        feedback.append("Add a lowercase letter.")

    if any(char.isdigit() for char in password):
        score += 1
    else:
        feedback.append("Add a number.")

    if any(not char.isalnum() for char in password):
        score += 1
    else:
        feedback.append("Add a special character.")

    if score <= 2:
        strength = "Weak"
    elif score <= 4:
        strength = "Medium"
    else:
        strength = "Strong"

    return strength, feedback

def main():
    password = input("Enter a password to check: ")

    strength, feedback = check_password(password)

    print(f"\nPassword strength: {strength}")

    if feedback:
        print("Suggestions:")
        for suggestion in feedback:
            print(f"- {suggestion}")
    else:
        print("Your password meets all the basic requirements.")

if __name__ == "__main__":
    main()
