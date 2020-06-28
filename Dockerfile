FROM alpine:latest

RUN apk update \
        && apk add sqlite curl python3

RUN curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip \
        && unzip rclone-current-linux-amd64.zip \
        && cd rclone-*-linux-amd64 \
        && cp rclone /usr/bin/ \
        && chown root:root /usr/bin/rclone \
        && chmod 755 /usr/bin/rclone \
        && rm /rclone-current-linux-amd64.zip

COPY backup_and_prune.py /

RUN echo '0 0 * * *     /backup_and_prune.py' > /etc/crontabs/root

CMD ["crond", "-f"]
