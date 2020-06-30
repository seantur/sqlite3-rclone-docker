Backup sqlite3 databases

## dockerhub:

    seantur/sqlite3-rclone-backup

# Generate rclone config

    docker run -it -v $PWD/.conf/rclone:/root/.config/rclone sqlite-rclone rclone config

# Example

    docker run -e AWS_ACCESS_KEY_ID= -e AWS_SECRET_ACCESS_KEY= -e RCLONE_REMOTE= -e RCLONE_PATH=backups -e DB_PATH=/sql/my.db -v /$PWD/.conf/rclone:/root/.config/rclone -v /$PWD/sql:/sql -v /$PWD/backups/:/backups sqlite-rclone


## Environment Variables

### required

* RCLONE_REMOTE: the name of the rclone remote in the rclone config
* RCLONE_PATH: the path of rclone remote
* DB_PATH: the path to the DB *from the backup container* (This will be application dependent)

### optional

there may be rclone specific environment variables, i.e. _AWS_ACCESS_KEY_ID_ and _AWS_SECRET_ACCESS_KEY_ for s3 compatible rclone remotes.

* DAY_N: how many days of backups to keep, default: 7
* WEEK_N: how many weeks of backups to keep, default: 4 
* MONTH_N: how many months of backups to keep, default: 12
* YEAR_N: how many years of backups to keep, default: 5


## Volume Mounts

* You will need to mount a folder to /backups for persistant storage. (/backups is what gets sync'd to the rclone remote)
* You will need to mount the folder that contains the sqlite db
* You will also need to mount the folder that contains the rclone config
