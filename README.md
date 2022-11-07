# tmd67-be
Backend api of TM D67 website.

## Requirements
Docker

(Recommends) Vscode with plugin [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

---
## Run pruduction server
Download `data.json` from `tmd67-data` repo and put it in this folder and run:

    docker-compose up -d

Then you can see the api docs via http://localhost.

---
## Contributing
Thanks for the contributing! Please fork this repo to your personal repositories and contribute with pull requests.

### Set up your dev environment
If you are using Vscode and have [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) installed, follow the instruction of the pop-up notification.

### Set up your database
Download `data.json` from `tmd67-data` repo and put it in this folder and run:

    make migrate

### Run the test server
    make run
