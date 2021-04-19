printf "apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: booking-server-ingress
  labels:
    app: booking-server-ingress
spec:
  rules:
  - http:
      paths:
      - path: /dns
        pathType: Prefix
        backend:
          service:
            name: booking-server-service
            port:
              number: 8080

---

apiVersion: v1
kind: PersistentVolume
metadata:
  name: booking-transaction-data-pv
  labels:
    type: local
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteMany
  capacity:
    storage: 1Gi
  hostPath:
    path: /c/Users/Owner/PycharmProjects/Booking/TransactionLogs

---

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: booking-transaction-data-pvc
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: booking-server
  labels:
    app: booking-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: booking-server
  template:
    metadata:
      labels:
        app: booking-server
    spec:
      containers:
      - name: booking-server
        image: distributedsystemsdesign/booking:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
          limits:
            cpu: 200m
            memory: 200Mi
        volumeMounts:
              - mountPath: .
                name: booking-transaction-data-pv-storage
      volumes:
      - name: booking-transaction-data-pv-storage
        persistentVolumeClaim:
          claimName: booking-transaction-data-pvc
                

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: booking-db
  labels:
    app: booking-db
spec:
  replicas: 2
  selector:
    matchLabels:
      app: booking-db
  template:
    metadata:
      labels:
        app: booking-db
    spec:
      containers:
      - name: booking-db
        image: mongo:latest
        ports:
          - containerPort: 27017
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
          limits:
            cpu: 200m
            memory: 200Mi
        env:
          - name: MONGO_USER
            value: MONGO
          - name: MONGO_PASSWORD
            value: MONGO
          - name: MONGO_DB
            value: MONGO

---

apiVersion: v1
kind: Service
metadata:
  name: booking-server-service
spec:
 type: LoadBalancer
 ports:
 - port: 8080
 selector:
   app: booking-server" > deployment.yaml