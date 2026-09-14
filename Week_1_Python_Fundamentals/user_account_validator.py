"""
User Account Validator
Processes a list of user accounts and checks whether each account is valid.
"""

accounts = [
    ("sisanda", "sisanda@company.com", True),
    ("thando", "thandocompany.com", True),
    ("", "admin@company.com", True),
    ("lwazi", "lwazi@company.com", False)
]

def validate_account(username, email, active):
    problems = []

    if not username.strip():
        problems.append("Username is missing")

    if "@" not in email or "." not in email:
        problems.append("Email address is invalid")

    if not active:
        problems.append("Account is inactive")

    return problems

def main():
    print("\n=== USER ACCOUNT VALIDATION ===")

    valid_count = 0

    for username, email, active in accounts:
        problems = validate_account(username, email, active)

        display_name = username if username else "(blank username)"

        if not problems:
            print(f"{display_name}: VALID")
            valid_count += 1
        else:
            print(f"{display_name}: INVALID")
            for problem in problems:
                print(f"  - {problem}")

    print(f"\nValid accounts: {valid_count}/{len(accounts)}")

if __name__ == "__main__":
    main()
