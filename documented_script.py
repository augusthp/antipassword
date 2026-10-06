import time
import subprocess
import getpass
import os

# my fake username and password
UNAME = "asdf"


def readPsw(env):
	#right now the way this works if you have to supply a public key (PW_KEY)
	#the program will ask you for the public key when you run it
	#it will ask you for the key 4 times, thats a bug I need to fix
	#it also isn't very secure because it prints the password in plane text
	# key = os.environ.get("PW_KEY")
	# if not key:
	# 	key = getpass.getpass("Enter Decryption key: ")
	# env = os.environ.copy()
	# env["PW_KEY"] = key
	try:
		results = subprocess.run(
			["openssl", "aes-256-cbc", "-d", "-a", "-iter", "10000",
			"-in", "encpassword.txt", "-pass", "env:PW_KEY" ],
			capture_output=True, text=True, check=True, env=env
		)
	except subprocess.CalledProcessError as e:
		print("openssl error:", e.stderr)
		exit(1)
	return int(results.stdout.strip())
	
def prompt2():
	"""
	This code asks the user for a password
	It turns the first 3 characters typed in into a number
	That makes it easier to check against the 
	PSWD variable later
	"""
	try:
		return int(input("enter password: ").strip())
	except ValueError:
		return None

def prompt1():
	"""
	This code asks the user for a username
	It turns whatever is typed in to lower case (.lower())
	And it removes any extra spaces typed in (.strip())
	That makes it easier to check against the 
	UNAME variable later
	"""
	return input("enter username: ").lower().strip()

def access():
	"""
	This part of the code handles signing the 
	guestbook file
	"""
	print("Access Granted!")

	# Get current timestamp in milliseconds
	ms_timestamp = int(time.time() * 1000)

	message = input("Enter your message to leave in the guestbook. \n Hackers - Please include your name!\n\t")
	with open("guestbook.txt", "a") as f:
		f.write(f"{ms_timestamp}: {message}\n")
	print("Message saved successfully.")
	
def auth():
	"""
	This part of the code checks to see if 
	the typed in username and password match what is 
	stored in the variables
	"""

	key = os.environ.get("PW_KEY")
	if not key:
		key = getpass.getpass("Enter Decryption key: ")
	env = os.environ.copy()
	env["PW_KEY"] = key
	uguess = prompt1()
	upswd = prompt2()
	PSWD = readPsw(env)
	print(uguess, "vs", UNAME, "...", uguess == UNAME)
	print(upswd, "vs", PSWD, "...", upswd == PSWD)

	if uguess == UNAME and upswd == PSWD:
		access()
		logged_in = True
	else:
		print("Access Denied")


"""
this code kicks us off
Like turning the ignition in a car
"""
if __name__ == "__main__":
	auth()	# vroom 	

