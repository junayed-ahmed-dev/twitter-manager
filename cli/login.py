import getpass
from modules.auth import login, signup
from cli.dashboard import DashboardCLI

def login_cli():
    while True:
        print("\nWelcome to Tweet Manager")
        print("1. Login")
        print("2. Signup")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            user_id = input("User ID: ").strip()
            pwd = getpass.getpass("Password: ").strip()
            if not user_id or not pwd:
                print("Error: User ID and Password cannot be empty.")
                continue
            if login(user_id, pwd):
                print("Login successful! Redirecting to your dashboard...")
                DashboardCLI(user_id).start()
            else:
                print("Login Failed: Invalid credentials!")
        elif choice == "2":
            name = input("Name: ").strip()
            email = input("Email: ").strip()
            phone = input("Phone: ").strip()
            pwd = getpass.getpass("Password: ").strip()
            user_id = signup(name, email, phone, pwd)
            if user_id:
                print(f"Signup successful! Your User ID: {user_id}\nUse this ID to log in.")
            else:
                print("Signup Failed: Invalid input or email already registered.")
        elif choice == "3":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    login_cli()
