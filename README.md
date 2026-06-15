# Lagovia Train Tracker

_Welcome to Lagovia, a small fictional land where the trains are always late and
citizens want to know exactly how late._

This project is a small full-stack application that allows users to query
the [Belgium irail APIs](https://api.irail.be/) for matching stations and
get the departure times and delays of the next trains departing from a station
within the next 15 minutes.

The project is built using [FastAPI](https://fastapi.tiangolo.com/) for the
backend and [Vue](https://vuejs.org/) for the frontend. 

It also implements [fuzzy search](#fuzzy-search) for station names and a [caching
mechanism](#caching) to reduce the number of requests to the irail APIs and
improve performance.

## Usage

### Backend

First, python 3 is required. Install the dependencies using pip:
```bash
pip install -r requirements.txt
```

To start the backend server in development mode, run the following command:
```bash
fastapi dev server.py
```

### Frontend

All the code for the frontend is in the `./frontend` directory.

First, nodejs and npm are required. Install the dependencies using npm:
```bash
npm install
```
To start the frontend server in development mode, run the following command:
```bash
npm run dev
```

## Stack choice

### Backend

My preferred choice for the backend is usually Go, but I chose to use Python for
this project because it was in the recommended tech stack and I feel comfortable
enough with Python, although I don't have much experience with FastAPI.
I also wanted to try FastAPI for a while, so this project was a good opportunity to
do it.

### Frontend 

I chose to use Vue for its simplicity and because its the framework I know best.
I'm interested in learning React, but I don't feel confident enough to use it
for this project, especially considering the tight deadline and the follow up
interview with questions about the code.

For the UI library I chose to use DaisyUI and Tailwind CSS because they are easy
to use and allow me to quickly build a simple and clean UI.

### Fuzzy search

Fuzzy search was not mandatory but it's actually very useful and easy to add.
I used [rapidfuzz](https://pypi.org/project/rapidfuzz/) for the fuzzy search
implementation, using the `partial_ratio` function to compare the user input
with the station names.

### Caching

Because querying the irail APIs for every user input is not efficient and can
lead to rate limiting, I implemented a simple caching mechanism using
[chachetools](https://pypi.org/project/cachetools/). The cache is a simple
in-memory TTL cache that stores the results of the API calls for a certain amount
of time (2 minutes for the station list and 30 seconds for the departure times).

The caching layer helped to reduce requests time by **26 times** on average. A simple
benchmarking script is included in the `./benchmark` directory, the following
is the result of running it on my machine:

| City     | Cold (ms) | Warm (ms) | Speedup |
|----------|----------:|----------:|--------:|
| Brussel  | 443.9 | 28.7 | 15.47× |
| Gent     | 1636.0 | 24.7 | 66.37× |
| Antwerp  | 873.1 | 23.7 | 36.79× |
| Liège    | 411.5 | 23.4 | 17.57× |
| Brugge   | 717.8 | 23.1 | 31.02× |
| Leuven   | 160.7 | 21.8 | 7.39× |
| Namur    | 195.9 | 22.3 | 8.79× |
| Mechelen | 541.1 | 23.2 | 23.34× |
| **Average** | **622.5** | **23.9** | **26.09×** |

> [!NOTE]
> In theory the irail APIs should support caching using conditional requests
> as documented in their [API documentation](https://docs.irail.be/#header-caching),
> but I was not able to make it work because the actual APIs do not return the
> `etag` header, so I had to implement a custom caching mechanism.

## Time spent

The backend implementation took around 1 hour. The frontend implementation
took around 1 hour. The caching (because I was stuck trying to make the irail
API caching work) too around 2 hours. Probably the actual caching implementation
took around 30 minutes. Adding 1/2 hours for everything else (setup, debugging,
benchmarking, etc) the total time spent on the project is around **5/6 hours**.
