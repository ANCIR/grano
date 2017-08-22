web:
	docker run -p 5000:5000 granoproject/grano grano runserver -h 0.0.0.0

base:
	docker build -t granoproject/base:latest contrib/base
	docker push granoproject/base:latest

image-latest:
	docker build -t granoproject/grano:latest .
	docker push granoproject/grano:latest
