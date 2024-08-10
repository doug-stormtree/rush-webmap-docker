# What's The RUSH?
The Resilient Urban Systems and Habitat (or R.U.S.H.) Initiative is a collective mapping effort that leverages both community knowledge and government data to idenfity, track, and share climate change data, community resources, and implemented solutions.

We would like to recognize that the R.U.S.H. Initiative is exploring this work on the unceded and unsurrendered territories of the lək̓ʷəŋən and SENĆOŦEN speaking peoples. Maps have a long history of erasure of Indigenous cultures and territories. Our goal is to promote tools that support the healing of ecosystems and communities so that all beings can live their best life.

Visit our website [here](https://whatstherush.ca).

## For anyone
If you have any questions or want to to contribute to the R.U.S.H. Initiative, either as a developer or in some other capacity, feel free to reach out to our team lead _Anne-Marie Daniel_ -- annemarie@naturnd.com, or one of our developers _Doug Stormtree_ -- Doug@naturnd.com, _Sam Morris_ -- dodobird181@gmail.com.

## For developers
We use GitHub issues to track project contributions. If you would like to contribute please make a fork and open a pull-request against this repository.

### Setup Environment
1. Fork this repo.
2. Clone it onto your local machine.
2. Create a `.env` file in the project directory with the following info:
    ```
    POSTGRES_USER=awesome_rushapp_contributor
    POSTGRES_PASSWORD=super_secret_local_development_password
    POSTGRES_DB=postgres
    DB_HOST=db
    DB_PORT=5432
    ```
    This file is read by docker-compose.yml to set container environment variables.

3. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) on your local machine.
4. Build the app using `docker compose build` while in the main project directory.
5. Run the app using `docker compose up`.
6. That's it! Please see the developer contact emails above if you have any questions, comments, or concerns. Cheers, and happy coding!
