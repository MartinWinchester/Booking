printf "version: '3.8'

networks:
  booking-network:
    name: booking-network
    driver: bridge

services:
  booking-server:
    container_name: booking-server
    build: Server/
    restart: always
    networks: 
      - booking-network
    ports:
      - 8080:8080
    depends_on:
      - booking-db
    volumes:
      - booking-transaction-data:$(pwd)/TransactionLogs

  booking-db:
    container_name: booking-db
    image: mongo:latest
    networks: 
      - booking-network
    ports:
      - 27017:27017
    restart: always
    environment:
      MONGO_USER: user
      MONGO_PASSWORD: password

volumes:
  booking-transaction-data:" > docker-compose.yml