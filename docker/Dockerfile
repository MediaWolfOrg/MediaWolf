FROM python:3.12-alpine

# Set arguments and env
ARG release_version
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/tubetube \
    release_version=${release_version}

# Create User
ARG puid=1000
ARG pgid=1000
RUN addgroup -g $pgid general_user && \
    adduser -D -u $puid -G general_user -s /bin/sh general_user

# Create directories and set permissions
COPY . /mediawolf
WORKDIR /mediawolf
RUN chown -R $puid:$pgid /mediawolf


RUN apk update && apk add --no-cache su-exec

# Install Firefox and Xvfb for web scraping
# RUN apk --no-cache add \
#    firefox \
#    xvfb \ 
#    ttf-freefont \
#    fontconfig \
#    dbus

# Install requirements and run code
RUN pip install --upgrade pip --root-user-action=ignore && \
    pip install --no-cache-dir --root-user-action=ignore -r /mediawolf/docker/requirements.txt
ENV PYTHONPATH="${PYTHONPATH}:/mediawolf/backend"

# Make the script executable
RUN chmod +x /mediawolf/docker/init.sh

# Expose port
EXPOSE 5000

# Start the app
ENTRYPOINT ["/mediawolf/docker/init.sh"]