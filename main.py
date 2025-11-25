#!/usr/bin/env python
import sys
import warnings
from dotenv import load_dotenv

# Remove or comment out these debug lines
# import litellm
# litellm._turn_on_debug()

# Add this line to suppress the warning
warnings.filterwarnings("ignore", message=".*not a Python type.*")
# Keep your existing warning filter
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

from gmail_crew_ai.crew import GmailCrewAi

def run():
    """Run the Gmail Crew AI."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get user input for number of emails to process
        try:
            email_limit = input("How many emails would you like to process? (default: 7): ")
            if email_limit.strip() == "":
                email_limit = 7
            else:
                email_limit = int(email_limit)
                if email_limit <= 0:
                    print("Number must be positive. Using default of 7.")
                    email_limit = 7
        except ValueError:
            print("Invalid input. Using default of 7 emails.")
            email_limit = 7
        
        print(f"Processing {email_limit} emails...")
        print("IN here 1")
        # Create and run the crew with the specified email limit
        result = GmailCrewAi().crew().kickoff(inputs={'email_limit': email_limit})
        print("IN here 2")
        # Check if result is empty or None
        if not result:
            print("\nNo emails were processed. Inbox might be empty.")
            return 0
            
        # Print the result in a clean way
        print("DONE 3")
        if result:
            print("Done 4")
            print("\nCrew execution completed successfully! 🎉")
            print("Results have been saved to the output directory.")
            return 0  # Return success code
        else:
            print("Done 5")
            print("\nCrew execution completed but no results were returned.")
            return 0  # Still consider this a success
    except Exception as e:
        print(f"\nError: {e}")
        return 1  # Return error code

if __name__ == "__main__":
    sys.exit(run())  # Use the return value as the exit code
