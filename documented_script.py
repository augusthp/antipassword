import time
import subprocess
import os
import argparse
import steganographer

# my fake username and password
UNAME = "asdf"

# the folder this script lives in. The assignment says every file the
# script reads or writes must be in this same folder, so we build
# file paths from this instead of from wherever the user ran python
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_args():
	"""
	This code reads the file names typed after the script name
	when it is run, for example:
	python3 documented_script.py encpassword.txt guestbook.txt
	pwfile is the encrypted password file and guestbook is the
	file that messages get saved to. Nothing is hard-coded, so
	any file names can be used. If one is missing, argparse
	prints a usage message instead of crashing.
	"""
	parser = argparse.ArgumentParser(
		description="Guestbook that checks an OpenSSL-encrypted password file")
	# each add_argument is one word the user must type after the script name
	parser.add_argument("pwfile", help="name of the encrypted password file")
	parser.add_argument("guestbook", help="name of the guestbook file to add messages to")
	return parser.parse_args()

def readPsw(env, pw_path):
	#the env variable it takes in stores the key. with the wrong key you can't open
	#the file
	#pw_path is the full path to the encrypted password file. It used to be
	#typed directly into the command below ("encpassword.txt"), but the
	#assignment says file names must come from script arguments, so
	#auth() now passes it in
	"""readPWS decrypts the openssl file so it can be read and compared
	to the user entered password. This subprocess.run just runs these commands
	which I think is why this doesn't work on windows.
	"""
	#make sure the password file exists before running openssl, so a missing
	#file gets a clear message instead of an openssl error
	if not os.path.isfile(pw_path):
		print("Password file not found: " + os.path.basename(pw_path))
		exit(1)
	
	try:
		#-d decrypts, -a reads the base64 text, and -iter 10000 must match
		#the flags used to encrypt the file or decryption will fail.
		#-in pw_path tells openssl which file to decrypt
		#we don't ask python to turn openssl's output into text, because a wrong
		#key gives back junk that isn't text and would crash it. we decode it
		#ourselves below. timeout=10 stops it hanging (limit is 15 seconds)
		results = subprocess.run(
			["openssl", "aes-256-cbc", "-d", "-a", "-iter", "10000",
			"-in", pw_path, "-pass", "env:PW_KEY" ],
			capture_output=True, check=True, env=env, timeout=10
		)
	#if this fails it should return an error message instead of just crashing
	except FileNotFoundError:
		print("OpenSSL was not found. Please install it and try again.")
		exit(1)
	except subprocess.TimeoutExpired:
		print("Checking the password took too long. Please try again.")
		exit(1)
	except subprocess.CalledProcessError:
		#openssl couldn't decrypt, which means the wrong key. we say the same
		#thing as a wrong password so nobody can tell which image is right
		print("Access Denied")
		exit(1)
	#openssl gave back raw bytes. with the wrong key they can be junk, so we
	#only accept them if they turn into text made of digits (the real password
	#is all digits). anything else gets treated like a wrong password
	try:
		text = results.stdout.decode("utf-8").strip()
	except UnicodeDecodeError:
		text = ""
	if not (text.isascii() and text.isdigit()):
		print("Access Denied")
		exit(1)
	return int(text)
	
def prompt2():
	"""
	This code asks the user for a password
	It turns what was typed in into a number (passwords are digits only)
	so it can be compared with the password decrypted by readPsw()
	If anything other than digits is typed it returns None instead,
	which never matches the real password
	"""
	#this try block lets prompt2 take in letters 
	#since the code says passwords should be numbers only 
	#this will always return "None" if a user types a letter
	#meaning the password will be wrong
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

def access(guestbook_path):
	"""
	This part of the code handles signing the
	guestbook file
	guestbook_path is the full path to the guestbook file. It used to be
	typed directly into this function ("guestbook.txt"), but it was corrected 
	to have auth() pass it in because file names must come from scrip arguments
	"""
	print("Access Granted!")

	# Get current timestamp in milliseconds
	ms_timestamp = int(time.time() * 1000)

	message = input("Enter your message to leave in the guestbook. \n Hackers - Please include your name!\n\t")
	with open(guestbook_path, "a") as f:
		f.write(f"{ms_timestamp}: {message}\n")
	print("Message saved successfully.")
	
def auth(pw_path, guestbook_path):
	"""
	This part of the code checks to see if 
	the typed in username and password match what is 
	stored in the variables
	pw_path and guestbook_path are the full paths to the encrypted
	password file and the guestbook. auth() does not open either one
	itself. It passes pw_path to readPsw() and guestbook_path to access()
	"""
	
	#this part looks for the decrpytion key
	#if none is set then it asks the user for the key
	#You need to set the decrpytion key when you use openssl
	#after that you need it each time the program runs.
	key = os.environ.get("PW_KEY")
	#attempts counts how many times we have asked for the campus image.
	#retrieve_data() returns nothing when the image is missing or has no
	#key, and the loop used to ask again forever. Now it gives up after 3 tries
	attempts = 0
	while not key and attempts < 3:
		key = steganographer.retrieve_data() # retrieves the key for the chosen campus
		attempts += 1
	#if we still have no key after 3 tries, stop with a clear message
	#instead of crashing later or leaving the user stuck at the prompt
	if not key:
		print("No valid campus image after 3 tries. Run the program again with the correct image file name.")
		exit(1)
	env = os.environ.copy()
	env["PW_KEY"] = key
	uguess = prompt1()
	upswd = prompt2()

	#readPsw gets the password file path so it knows which file to decrypt,
	#and access gets the guestbook path so it knows where to save the message

	if uguess == UNAME and upswd == readPsw(env, pw_path):
		access(guestbook_path)
	else:
		print("Access Denied")


"""
this code kicks us off
Like turning the ignition in a car
"""
if __name__ == "__main__":
	#get_args() reads the two file names typed after the script name
	args = get_args()
	#os.path.basename keeps only the file name from what was typed, so
	#something like ../other.txt or /tmp/other.txt can't point outside
	#the script's folder. The assignment says all files must live there.
	#os.path.join then puts that file name onto SCRIPT_DIR (the folder
	#this script is in), so both files are found there no matter which
	#folder the user ran python from
	pw_path = os.path.join(SCRIPT_DIR, os.path.basename(args.pwfile))
	guestbook_path = os.path.join(SCRIPT_DIR, os.path.basename(args.guestbook))
	#hand both paths to auth(), which passes them on to readPsw() and access()
	auth(pw_path, guestbook_path)	# vroom

