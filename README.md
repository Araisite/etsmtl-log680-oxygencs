# LOG-680 - E24 - Grp1 - Eq13

## Install all packages

You need to run:

```bash
pipenv install
pip install python-dotenv black pylint
```

## Pre-commit file

Your pre-commit file should look like this:

./.git/hooks/pre-commit

```bash
#!/bin/bash

# Ensure Python executable and scripts are in the PATH
export PATH=%LOCALAPPDATA%/Programs/Python/Python312/python.exe:%LOCALAPPDATA%/Programs/Python/Python312/Scripts:$PATH

files=$(git diff --cached --name-only --diff-filter=ACM "*.py" | tr '\n' ' ')

pylint $files
pylint_exit=$?


black --check $files
black_exit=$?

echo "The result of python pylint module: $pylint_exit"
echo "The result of python black module: $black_exit"
echo "For the 2 lines above anything different of 0 is not good..."
echo ""
echo "Will commit in 3 seconds whatever the previous results were..."
sleep 3


# FOR PROD UNCOMMENT THIS TO MAKE SURE THE SYNTAX IS ABSOLUTELY PERFECT BEFORE DOING THE COMMIT
#if [ $pylint_exit -ne 0 ] || [ $black_exit -ne 0 ]; then
#    echo "Linting or formatting check failed. Commit aborted."
#    exit 1
#fi

exit 0
```

## .env file

Your ./.env file should look like this

```
#HVAC Simulator
HOST=http://XXX.XXX.XXX.XXX
TOKEN=XXXXXXXX
T_MAX=22
T_MIN=18

#Database
DATABASE_URL=XXX.XXX.XXX.XXX
DB_NAME=XXXXXXX
DB_USER=XXXXXX
DB_PASS=XXXXXX
DB_PORT=XXXX
```

# Docker

## Build and run the docker image

Since we don't include the .env file into the image, we have to pass it as a parameter when we run the image. Hence :

### Building the image

```sh
docker build -t my-image .
```

### Running the image

```sh
docker run --env-file .env my-image
```

# LOG-680 : Template for Oxygen-CS

This Python application continuously monitors a sensor hub and manages HVAC (Heating, Ventilation, and Air Conditioning) system actions based on received sensor data.

It leverages `signalrcore` to maintain a real-time connection to the sensor hub and utilizes `requests` to send GET requests to a remote HVAC control endpoint.

This application uses `pipenv`, a tool that aims to bring the best of all packaging worlds to the Python world.

## Requierements

- Python 3.8+
- pipenv

## Getting Started

Install the project's dependencies :

```bash
pipenv install
```

## Setup

You need to setup the following variables inside the App class:

- HOST: The host of the sensor hub and HVAC system.
- TOKEN: The token for authenticating requests.
- T_MAX: The maximum allowed temperature.
- T_MIN: The minimum allowed temperature.
- DATABASE_URL: The database connection URL.

## Running the Program

After setup, you can start the program with the following command:

```bash
pipenv run start
```

## Logging

The application logs important events such as connection open/close and error events to help in troubleshooting.

## To Implement

There are placeholders in the code for sending events to a database and handling request exceptions. These sections should be completed as per the requirements of your specific application.

## License

MIT

## Contact

For more information, please feel free to contact the repository owner.
