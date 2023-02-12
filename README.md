# tmd67-be
Backend api of TM D67 website. Currently based on [Django REST framework](https://www.django-rest-framework.org/) and [Strawberry GraphQL Django](https://strawberry-graphql.github.io/strawberry-graphql-django/)

## Requirements
Docker

(Recommends) Vscode with plugin [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

---
## Docs
- base-url: https://testtmd67api.azurewebsites.net/
- spec: https://www.notion.so/c2caef7031e34d02873b4a40f9d47108

## 環境變數
| 名稱 | 值（模擬）                            | 模組       | 註 |
| --- |--------------------------------|----------| --- |
| LOGOUT_REDIRECT_URL | https://ac.toastmasters.org.tw | Identity | 首頁，支付後追加/me |
| LOGIN_REDIRECT_URL | https://ac.toastmasters.org.tw/me | Identity | 登入後的頁面 |
| MerchantID | MS12345678                     | Payment  | 藍新 |
| HashKey | AAAvw3YlqoEk6G4HqRKDAYpHKZWxBBB | Payment  | 藍新 |
| HashIV | AAAC1FplieBBB                  | Payment  | 藍新 |
| Version | 2.0                            | Payment  | 藍新 |
| MPG_GW | https://ccore.newebpay.com/MPG/mpg_gateway | Payment  | 藍新 |
| ItemDesc | 2023 Annual Conference Ticket  | Payment  | 藍新 |
| RETURN_URL | http://gw.tmd67.com/newebpay-return/ | Payment  | 藍新 |
| NOTIFY_URL | http://gw.tmd67.com/newebpay-return/ | Payment  | 藍新 |
| GG_CLIENT_ID | fmoirt.apps.googleusercontent.com | Google   | Google |
| GG_CLIENT_SECRET | U18cIQr0Nb5EEE                 | Google   | Google |
| GG_REDIRECT_URI | https://api.tmd67.com/google/callback/ | Google   | Google |

## Run pruduction server
Download `data.json` from `tmd67-data` repo and put it in this folder and run:

    docker-compose up -d

Then you can see the api docs via http://localhost.

GraphQL api can be viewed at http://localhost/graphql.

---
## Contributing
Thanks for the contributing! Please fork this repo to your personal repositories and contribute with pull requests.

### Set up your dev environment
If you are using Vscode and have [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) installed, follow the instruction of the pop-up notification and you will create a container with test environment.

If you prefer use manual env, run:

    pip install -r requirements_dev.txt

### Set up your database
By default, Dev Containers will provide a Postgres DB on localhost for testing. See [here](https://github.com/toastmasters-d67/tmd67-be/blob/main/.devcontainer/docker-compose.yml#L29) for more details such as username.

For data migration, download `data.json` from `tmd67-data` repo and put it in this folder and run:

    make migrate

### Run the test server
    make run
