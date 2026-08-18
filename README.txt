# Project Title

A brief description of what the project does.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

To run this project using Docker, follow these steps:



1. Install Docker: If you don't have Docker installed, you can download and install it from the official Docker website: [https://www.docker.com/get-started](https://www.docker.com/get-started).

1.Clone the repository:

  $ git clone -b develop https://hala72@bitbucket.org/lonesys/e-learning-project.git


2.Change to the project directory

2. Build the Docker images: Open a terminal or command prompt and navigate to the root directory of the project. Run the following command to build the Docker image:

   ```bash
   docker-compose build


## Usage

Explain how to use the project. Provide examples, code snippets, or screenshots if applicable.


2. add .env file to this path : tr/backend/.env <you will find .env.example file in backend folder>

2. run:
    python manage.py loaddata --ignorenonexistent data.json after that uncommet .

3. Run the Docker containers:Open a terminal or command prompt and navigate to the root directory of the project. Run the following command to build the Docker image:

   ```bash
   docker-compose up

3. Add DB required data :  Open a terminal or command prompt for the backend container . Run the following commands to make migrations and add required data:

   ```bash
   python manag.py makemigrations
   python manag.py migrate
