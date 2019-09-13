# Stacki's first GraphQL API 🍼

## Installation

You will [Docker](https://www.docker.com/products/docker-desktop) and [Docker Compose](https://docs.docker.com/compose/) to get started without a Stacki frontend.

## Getting Started

Once you have Docker installed, just enter `docker-compose up` in this directory. Docker compose with build the images and seed the database with a frontend and two backends. Then just open your browser and go to `localhost:8000`.

### Adding new types to the schema

New schema files must be added to the `app/schema` directory. If you are defining Query, Mutation, or Subscription types they must be extended. A server restart is required when adding new schema files.

```grapqhl
extend type Query {
  newQuery: ReturnType
}

extend type Mutation {
  newMutation(newId: Int!): ReturnType
}

extend type Subsctiption {
  newSubscription(subId: Int!): ReturnType
}
```

### Adding new resolvers

New resolvers must be added to the `app/resolvers` directory. All resolver must contain the following or the server will crash. We're working on this.

```python
from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()
object_types = []
```

The server should restart by itself when updating resolver, but you may have to restart it yourself. ¯\\\_(ツ)_/¯

## Progress

This is a very loose list of what has been accomplished.

| Table                  | Create             | Read               | Update             | Delete             |
| ---------------------- | ------------------ | ------------------ | ------------------ | ------------------ |
| Access                 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| aliases                |                    |                    |                    |                    |
| appliances             | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| attributes             | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| attributes_doc         |                    |                    |                    |                    |
| boot                   | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| bootactions            | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| bootnames              | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| boxes                  | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| cart_stacks            |                    |                    |                    |                    |
| carts                  |                    |                    |                    |                    |
| environments           | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| firewall_rules         |                    |                    |                    |                    |
| firmware               |                    |                    |                    |                    |
| firmware_imp           |                    |                    |                    |                    |
| firmware_make          |                    |                    |                    |                    |
| firmware_mapping       |                    |                    |                    |                    |
| firmware_model         |                    |                    |                    |                    |
| firmware_version_regex |                    |                    |                    |                    |
| groups                 | in progress        | in progress        | in progress        | in progress        |
| ib_memberships         |                    |                    |                    |                    |
| ib_partitions          |                    |                    |                    |                    |
| memberships            | :x:                | :x:                | :x:                | :x:                |
| interfaces             | :heavy_check_mark: | :heavy_check_mark: |                    |                    |
| hosts                  |                    | :heavy_check_mark: |                    |                    |
| oses                   | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| partitions             | :x:                | :x:                | :x:                | :x:                |
| public_keys            | :x:                | :x:                | :x:                | :x:                |
| pallets                | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| routes                 |                    |                    |                    |                    |
| scope_map              | :x:                | :heavy_check_mark: | :x:                | :x:                |
| stacks                 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| storage_controller     | in progress        | in progress        | in progress        | in progress        |
| storage_partition      | in progress        | in progress        | in progress        | in progress        |
| networks               | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| switchports            |                    |                    |                    |                    |
| tags                   |                    |                    |                    |                    |
