<div id="top"></div>
<!--
*** Authord by MeisamT.
-->
     
<!-- Website LOGO -->
<br />
<div align="center">
  <a href="https://aasood.com">
    <img src="https://aasood.com/media/logo/stores/1/file.png" alt="Logo" width="107" height="47">
  </a>
 
 
<h3 align="center">Product Microservice</h3>

 
  <p align="center">
    A microservice to create product and get its information.
    <br />
    <a href="#"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://devprod.aasood.com">View Demo</a>
    ·
    <a href="https://gitlab.aasood.com/ecommerce/backend/product/-/issues">Report Bug</a>
    ·
    <a href="https://gitlab.aasood.com/ecommerce/backend/product/-/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->

## About The Project

For the ecommerce project, we needed a microservice for creating and manipulating products. So we created this
microservice.

This microservice will do:

* Create a product
* Get a product
* Get all products
* Update a product
* Delete a product
* Get kowsar information about a product
* Validate a product based on custom attributes
* Add a product to custom category
* Remove a product from custom category
* Get all products in a custom category

We have specified a schema for the product; Here is an example:

```json
{
  "system_code": "100104011011",
  "attributes": {
    "image": "/src/default.png",
    "year": 2020
  }
}
```

Let me explain them individually:
`system_code` is the unique identifier for the product. When you set the system_code, it would get the `main_category`
, `sub_category`, `brand`, `model` and `config`' from the kowsar collection.
`attributes` is a dictionary of required attributes for the product. For example in the above example, the product will
have an `image` and `year` attribute.

<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

In this project, we used the following technologies:

* [Python](https://www.python.org)
* [Mongo DB](https://www.mongodb.com)
* Later, [Vue.js](https://vuejs.org) may included.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->

## Getting Started

In this part, there is an instructions on setting up the project locally. To get a local copy up and running follow
these simple steps.

### Prerequisites

For this project, you need python v3.9 and mongodb
v5[Install MongoDB Community Edition](https://docs.mongodb.com/manual/administration/install-community/)

### Installation

After installing prerequisites, now you can install dependencies of this project:

1. Clone the repo
   ```sh
   git clone git@200.100.100.162:ecommerce/backend/product.git
   ```
2. Setup an environment
    ```sh
    sudo apt install python3-virtualenv
    virtualenv venv
    source venv/bin/activate
    ```
3. Install pip packages
   ```sh
   pip install -r requirements.txt
   ```
4. In main directory(where `setup.py` file is) use this command to install the project
   ```sh
   pip install -e .
   ```
5. Create .env file in main directory

    ```text
    APP_NAME="product"

    MONGO_HOST="localhost"
    MONGO_PORT="27017"
    MONGO_USER=""
    MONGO_PASS=""
    
    REDIS_HOST="localhost"
    REDIS_PORT="6379"
    REDIS_USER=""
    REDIS_PASS=""
    REDIS_DB="1"
    
    RABBIT_HOST="localhost"
    
    UVICORN_HOST="0.0.0.0"
    UVICORN_PORT="8000"
    
    TELEGRAM_BOT_TOKEN=""
    CHAT_IDS=[123456789]
    ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->

## Usage

To run the project, make sure that the mongodb service is up locally and run this in the app directory

```sh
python main.py
```

- You can visit [localhost:8000](http://localhost:8000) for root directory.

<p align="right">(<a href="#top">back to top</a>)</p>

## Database Visualization

Download mongodb compass:
[MongoDB Compass](https://www.mongodb.com/try/download/compass)

## Testing

For testing the project, run this command in main directory

```sh
pytest
```

## Coverage

Testing coverage can also be achieved by:

```shell
pytest --cov
```

<!-- ROADMAP -->

## Roadmap

- [x] Get and manipulate Kowsar data
- [x] CRUD for products
- [x] validate products
- [x] add products to custom category
- [x] Refactor according to needs
- [ ] Multi-language Support
    - [x] Persian
    - [x] English
    - [ ] Arabic

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any
contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also
simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->

## License

All rights reserved

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->

## Contact

Meisam Taghizadeh - [@meisam2236](https://t.me/meisam2236) - meisam2236@gmail.com

Fatemeh Khosravi - [@fatemehkhosravy](https://t.me/fatemehkhosravy) - ftmkhosravy@gmail.com

Project
Link: [https://gitlab.aasood.com/ecommerce/backend/product](https://gitlab.aasood.com/ecommerce/backend/product)

<p align="right">(<a href="#top">back to top</a>)</p>
