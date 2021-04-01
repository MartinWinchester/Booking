import requests
import sys
import argparse, time, logging
logging.basicConfig(format='%(levelname)s: %(asctime)s - %(message)s',filename='cilent_log.txt', level=logging.DEBUG)


def testGet(url):
	logging.info("Start testing get request")
	while True: 
		try:
			response = requests.get(url+"/book", params={'UID': 5})
			print(response.status_code)
			print(response.encoding)
			print(response.json())
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
