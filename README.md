# What's The RUSH?
Visit [What's the RUSH](https://whatstherush.ca).

The Resilient Urban Systems and Habitat, or RUSH, Initiative is a collective mapping effort that leverages both community knowledge and government data to idenfity, track, and share climate change data, community resources, and implemented solutions.

We would like to recognize that the RUSH Initiative is exploring this work on the unceded and unsurrendered territories of the lək̓ʷəŋən and SENĆOŦEN speaking peoples. Maps have a long history of erasure of Indigenous cultures and territories. Our goal is to promote tools that support the healing of ecosystems and communities so that all beings can live their best life.

## For anyone
If you have any questions or want to to contribute to the RUSH Initiative, either as a developer or in some other capacity, feel free to reach out to our team lead _Anne-Marie Daniel_ -- annemarie@naturnd.com, or one of our developers _Doug Johnson_ -- Doug@naturnd.com, _Sam Morris_ -- dodobird181@gmail.com.

## Development
First, install [Docker Desktop](https://docs.docker.com/get-docker) for Mac, Windows, or Linux. Docker Desktop includes Docker Compose as part of the installation. Run Docker Desktop on your local machine. This starts the "Docker Daemon" which works in the background to communicate between the Docker CLI and your OS.

Then, run the development server:
```bash
# Create a network, which allows containers to communicate
# with each other, by using their container name as a hostname
docker network create rush_network

# Build dev (this may take ~5-10 mins if not cached.)
docker compose -f docker-compose.dev.yml build

# Up dev
docker compose -f docker-compose.dev.yml up
```
Open [http://localhost:3000](http://localhost:3000) with your browser to see the result. That's it, you're all set up! Below are some useful commands to help you get started.
```bash
# See container logs. You can add "db" or "next-app" after "logs" to zero-in
# on either container's individual logs.
docker-compose -f docker-compose.dev.yml logs

# Start the Prisma Admin site, which can be used to view and edit the app's data.
docker-compose -f docker-compose.dev.yml exec next-app npx prisma studio

# Apply a Prisma ORM schema change. This updates the database's schema and
# may also edit the prisma.schema file in the process. You should run
# this command after making changes to the prisma.schema file so that they are
# reflected in the database.
docker-compose -f docker-compose.dev.yml exec next-app npx prisma migrate dev

# Shell into the database.
docker compose -f docker-compose.dev.yml exec -it db psql -U admin -d postgres
```


