IMAGE=seantur/sqlite3-rclone-backup
TAG=latest

build:
	docker build -t $(IMAGE):$(TAG) .

push: build
	docker push $(IMAGE):$(TAG)
