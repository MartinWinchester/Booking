FROM python:3.7.4-slim-buster

WORKDIR /Server

COPY Server.py Server.py
COPY Utils.py Utils.py
COPY DataBase.py DataBase.py
COPY secrets.json secrets.json
RUN pip3 install pymongo datetime flask flask_restful uuid argparse scipy numpy bidict dnspython
CMD [ "python", "Server.py" , "-s", "0.0.0.0:8080", "-db", "localhost:27020", "-gdb", "localhost:27019"]