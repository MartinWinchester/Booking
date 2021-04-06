import requests
import sys
import argparse, time, logging
logging.basicConfig(format='%(levelname)s: %(asctime)s - %(message)s',filename='cilent_log.txt', level=logging.DEBUG)


def isGetResponseValide(re):
	if 'JID' not in re.keys():
		return False
	if 'Source' not in re.keys():
		return False
	if 'Destination' not in re.keys():
		return False
	if 'From' not in re.keys():
		return False
	if 'To' not in re.keys():
		return False
	return True

def testGet(url):
	logging.info("Start testing get request")
	while True: 
		try:
			response = requests.get(url+"/book", params={'UID': 5})
			# check response status_code
			if (response.status_code != 200):
				logging.debug("get request not succeed")
				print("get request not succeed")
			# check validation of reponse json object
			if !isGetResponseValide(response.json()):
				logging.debug("GET response not valid")
				print("GET response not valid")

			time.sleep(2)
		except Exception as Argument:
			logging.exception("Connection Refused")



def readCommand( argv ):
	parser = argparse.ArgumentParser()
	parser.add_argument("-t", "--test", default="get")
	parser.add_argument("-s", "--server", default="http://localhost:8080")
	args = parser.parse_args()
	OwnUrl = args.server
	if args.test == "get":
		testGet(OwnUrl)


if __name__ == '__main__':
    args = readCommand( sys.argv[1:] )
