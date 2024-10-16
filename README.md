# Overview

I follow an agile approach. This should be reflective of the various branches in git.

Stages:
1. The Baseline Pipeline is representative of a proof of concept (POC). Demonstrate initial value and get stackholder feedback.
2. The Airflow branch is representative of a more robust pipeline addressing limitations of running pipeline as a script.
3. Postgres branch is representative of a more robust pipeline addressing limitations of using local sqlite


# Note on running Pipeline via docker-compose
Please ensure settings in docker allow for sufficient resources to be allocated in Docker settings. Preferably 8 CPUs and 8GB of memory. This is to ensure that the pipeline runs smoothly.


## 1. Baseline Pipeline and FastAPI Application
This is presented in git branch: `baseline-pipeline`

1. The pipeline processing is done within python script: `pipeline.py`
2. This reads the data from the xml file and writes it to a local sqlite database.
3. The sqlite3 databse has two tables : raw_data_extracts and keyword_pairs_frequency_table
4. The endpoints are exposed using FastAPI application

### Key Decisions
- Used `NlmDcmsID` as the unique identifier for the meeting abstracts.
- Excluded keywords with attribute `Owner="NASA"` from the keyword pairs frequency table. This is because the high frequency with which they appear in the data would skew the results.


### Running the Baseline Pipeline

Details on how to create a Docker image and run a container from that image, follow these steps:

1. **Build the Docker Image**: Open a terminal in the directory containing the `Dockerfile` and run the following command:

```bash
docker build -t causaly-data-pipeline-app-v1 .
```

This command builds a Docker image using the instructions in the `Dockerfile` in the current directory (`.`). The `-t` option tags the image with the name `causaly-data-pipeline-app-v1`.

2. **Run the Docker Container**: After the image has been built, you can start a container from this image using the following command:

```bash
docker run -d -p 8000:80 causaly-data-pipeline-app-v1
```

This command starts a new Docker container from the `causaly-data-pipeline-app-v1` image. The `-d` option runs the container in detached mode (in the background). The `-p` option maps port 8000 on your local machine to port 80 on the Docker container.

After running this command, the application inside the Docker container should be accessible at `http://localhost:8000/docs#`.

The Fastapi application provides a nice interface to try out both endpoints:

[/get_most_occurring_keywords](http://localhost:8000/docs#/default/get_most_occurring_keywords_get_most_occurring_keywords_post)

[/add_meeting_abstract](http://localhost:8000/docs#/default/add_meeting_abstract_add_meeting_abstract_post)


### Limitations

1. The pipeline runs in a single python script. If the pipeline fails at anypoint, the entire pipeline needs to be rerun.
2. This is not efficient. It also does not clearly communicate to end users the status of the pipeline.
3. The script iterates over each meeting abstract and extracts uid, keywords. It stores the data in memory in a pandas dataframe. This is not efficient for large datasets.
4. The sqlite database is created during the pipeline and stored within the mounted data drive, the data is not persisted once container is stopped.
5. The add meeting abstract does not check to see whether the meeting abstract already exists in the database. This can lead to duplicate entries.
6. The add meeting abstract endpoint also only updates the keyword pairs frequency table and not the keyword pairs table. This prevents us checking for further duplicates.
7. The keywords are processed in a basic format: lower cased and stripped of punctuation. This can lead to duplicates if the same keyword is written in different formats. E.g eyes vs eye
8. Minimal validation on required fields in sql tables. Keywords may pair with null values.


### Highlights of POC
1. Limit the number of expense GROUP BY operations performed when adding new meeting abstracts. We therefore only update the keyword pairs which are added. Rather than performing an entire GROUP BY on the whole table.
2. The POC is fully tested. See tests in `tests` directory.
3. Utilised .pre-commit-config.yaml to ensure code is linted and formatted before committing to git.
4. All functions are type hinted to allow mypy type checking in pre-commit hooks.


## 2. Airflow
This is present in git branch: `slim-airflow`.

The baseline pipeline was just run in a script which provided several issues:

- No clear communication to end users on the status of the pipeline
- No way to restart the pipeline from where it failed
- No way to schedule the pipeline to run at a specific time
- No way to monitor the pipeline

These issues can be addressed by using Apache Airflow.

I followed the documentation from Apache Airflow to run airflow in docker found [here](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html).
This provided a skeleton of the docker-compose file to run the Airflow instance in docker.
See initial `docker-compose` file in commit sha: 8164e9a9d71b555253cd91ec9a4cf505810ae727

*Note* : This docker-compose is not intended for production, but provides a useful demo of airflow capabilities.


### Running the Airflow Pipeline

1. **Start Airflow**: Open a terminal in the directory containing the `docker-compose.yaml` file and run the following command:

```bash
 docker-compose up
```

1. **Access the Airflow UI**: After starting the Airflow instance, you can access the Airflow UI by navigating to `http://localhost:8080` in your web browser.
   1. [airflow_ui_login](http://localhost:8080)

2. Access to airflow UI is password protected. The default username and password are `airflow` and `airflow` respectively.

3. **Running the DAG**: The DAG is located in the `dags` directory. The DAG is called `data_pipeline_dag.py`. You can trigger the DAG to run by clicking on the `Trigger DAG` button in the Airflow UI.

4. **Access the FastAPI Application**: The FastAPI application is still running in a separate container. You can access the FastAPI application at `http://localhost:8010/docs#` as before.
    1. [/get_most_occurring_keywords](http://localhost:8010/docs#/default/get_most_occurring_keywords_get_most_occurring_keywords_post)
    2. [/add_meeting_abstract](http://localhost:8010/docs#/default/add_meeting_abstract_add_meeting_abstract_post)

5. **Closing down docker-compose**: After you have finished using the app, you can stop the containers by running the following command:

```bash
docker-compose down --volumes --rmi all
```


### Limitations

1. The Airflow instance is not production ready. It is intended for demo purposes only.
2. **Security Risks/Vulnerabilities** Credentials for airflow and postgres db are stored in the docker-compose file. This is not secure. In a production environment, these should be stored in a secure location e.g Azure Key Vault.
3. Data store is persisted to a sqlite database. The sqlite database is stored in the mounted data drive and is therefore persisted after running `docker-compose down`. In a production environment, this should be persisted to a permanent db in a secure location.


### Additional Improvements

1. Structured the src directory to be more modular. This will allow for easier testing and maintenance.
2. Added logic to ensure duplicate meeting abstracts are not added to the database.
3. Added logic to ensure additional meeting abstract keyword pairs are inserted into the database.
4. Refactored codebase to remove redundant code.
5. Removed unnecessary sections of template docker-compose.yaml file from airflow.
6. Mounted on the data drive to prevent xlm data having to be copied into docker image.
7. Ensured all the tests run with tox.This will allow for easier testing and maintenance especially when incorporating CI/CD pipelines. Open terminal in same level as `tox.ini` and run command

```bash
 tox
```

# 3. Postgres
This is present in git branch: `main`

Docker-compose file has been updated to include an additional postgres database container (in addition to the one used by airflow). The sqlite database has been removed. A database connection is now made via sqlalchemy to the postgres database.
As the containers are all running in the same network, the DAG scripts and FastAPI application can connect to the postgres database via the service name rather than IP address.
The code is however now easily pointed to persisted data to another database by changing the connection config.

### Limitations
Tests are run in the same way as before. SQl utils utilise sqlite in memory database still. The sql queries are transferable between sqlite and postgres. In an ideal world, the tests would be run against a postgres database which is spun up and then torn down after the tests are run.


### Running/Stopping the Postgres Pipeline
Follow same steps as running the airflow pipeline. The only difference is that the data is now stored to a postgres database rather than a sqlite database. The postgres database is NOT persisted after the docker-compose is stopped. The reason I created an additional postgres container is to provide some separation from the database included as part of airflow.



# 4. Future Improvements

1. Processing of keywords is still very basic. This can be improved by using a more sophisticated NLP library. Keywords can be stemmed and lemmatized to reduce duplicates.
2. The pipeline can be further improved by using a more sophisticated database. The current database is a relational database. A graph database may be more suitable for this type of data.
3. Address several security risks of passwords being stored in docker-compose file which is on git. This can be done by using Azure Key Vault.
4. Pipeline is currently set up to only run once, it isn't designed for regular batch processing.
5. Explore ways to parallelize the pipeline e.g using Ray
6. Add some form validation to the FastAPI application. This can be done using Pydantic.
