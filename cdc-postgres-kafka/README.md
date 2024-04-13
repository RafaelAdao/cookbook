# Capture Data Change from Postgres and Publish to Kafka

This project demonstrates how to [capture data change (CDC)](https://debezium.io/documentation/faq/#what_is_change_data_capture) from Postgres and publish to Kafka. The project uses [Debezium](https://debezium.io/documentation/faq/#what_is_debezium) as the CDC tool to capture data change from Postgres and publish to Kafka.

## The challange

In large enterprises, data is stored in multiple databases. I have seen too many times codes that send the same data to multiple databases. Like this:

```python
relational_db.save(data)
nosql_db.save(data)
search_engine.save(data)
```

There are big challenges with this approach:

1. **Consistency**: How to keep consistency between these databases? How to deal with the failure of one of these databases? And if the ordering of the data is important?
2. **Scalability**: How to deal with scalability when the performance depends on the slowest database?
3. **Complexity**: The code is complex and hard to maintain. Imagine many points in the code and others microservices doing the same thing.

The traditional way to keep consistency between these databases is to use the ETL (Extract, Transform, Load) process. The ETL process is a batch-oriented process that extracts data from the source database, transforms the data, and loads the data into the target database. The ETL process has some limitations, like the ETL process is batch-oriented, which means it can't provide real-time data synchronization. The ETL process is also complex and expensive.

![alt text](etl.png)

### Change Data Capture (CDC)

Change Data Capture, or CDC, is an older term for a system that monitors and captures the changes in data so that other software can respond to those changes. Data warehouses often had built-in CDC support, since data warehouses need to stay up-to-date as the data changed in the upstream OLTP databases.

![alt text](cdc.png)

## Using Debezium to capture data change

[Debezium](https://debezium.io/documentation/faq/#what_is_debezium) is a set of distributed services that capture row-level changes in your databases so that your applications can see and respond to those changes. Debezium records in a transaction log all row-level changes committed to each database table. Each application simply reads the transaction logs they’re interested in, and they see all of the events in the same order in which they occurred.

You can check what databases Debezium supports [here](https://debezium.io/documentation/faq/#what_databases_can_debezium_monitor).

You can output the data change to different sinks like Kafka, Amazon Kinesis, Google Cloud Pub/Sub, etc.

In this cookbook, I will use Debezium Postgres connector via Kafka Connect.

## Setting Up Debezium Components Using Docker Run Commands

In this tutorial, we'll guide you through setting up the Debezium components - Zookeeper, Kafka, PostgreSQL, and Connect - using individual `docker run` commands.

### 1. Zookeeper

Zookeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services. Let's start by running Zookeeper:

```bash
docker run --rm \
  --name zookeeper \
  -p 2181:2181 \
  debezium/zookeeper:2.1
```

### 2. Kafka

Kafka is a distributed streaming platform that is commonly used for building real-time streaming data pipelines and applications. Here's how you can run Kafka:

```bash
docker run --rm \
  --name kafka \
  -p 9092:9092 \
  --env ZOOKEEPER_CONNECT=zookeeper:2181 \
  --link zookeeper \
  debezium/kafka:2.1
```

### 3. PostgreSQL

PostgreSQL is a powerful, open-source relational database system. Let's launch a PostgreSQL instance:

```bash
docker run --rm \
  --name postgres \
  -p 5432:5432 \
  --env POSTGRES_PASSWORD=postgres \
  --env POSTGRES_HOST_AUTH_METHOD=trust \
  --env POSTGRES_USER=postgres \
  postgres:15.2-alpine3.17
```

docker exec -it postgres psql -U postgres

CREATE DATABASE inventory;
\c inventory;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  weight FLOAT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO
  products (name, weight)
VALUES
  ('scooter', 3.14),
  ('car battery', 8.1),
  ('12-pack drill bits', 0.8),
  ('hammer', 0.75);

### 4. Connect

Debezium Connect is an open-source distributed platform for building streaming data pipelines and applications. Here's how to set up Debezium Connect:

```bash
docker run --rm \
  --name connect \
  -p 8083:8083 \
  --env CONFIG_STORAGE_TOPIC=connect_configs \
  --env OFFSET_STORAGE_TOPIC=connect_offsets \
  --env STATUS_STORAGE_TOPIC=connect_statuses \
  --env BOOTSTRAP_SERVERS=kafka:9092 \
  --link kafka \
  --link postgres \
  debezium/connect:2.1
```

### Summary

By following these steps, you've set up the Debezium components - Zookeeper, Kafka, PostgreSQL, and Connect - using `docker run` commands. These components are now ready to use for building your streaming data pipelines and applications.