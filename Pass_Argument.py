while True:
    try:
        userInput = input("Would you like to 'upgrade' or 'downgrade' the image: ")
        userInput = userInput.lower();
    except ValueError:
        print("Sorry, I didn't understand that.")
        continue

    if userInput not in ['upgrade', 'downgrade']:
        print("Sorry, your response must be either 'upgrade' or 'downgrade'.")
        continue
    else:
        #age was successfully parsed, and we're happy with its value.
        #we're ready to exit the loop.
        break
if userInput == "upgrade": 
    print("You are upgraded")
elif userInput == "downgrade":
    print("You are downgraded")
