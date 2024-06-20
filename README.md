
# ![Maggma](docs/logo_w_text.svg)

[![Static Badge](https://img.shields.io/badge/documentation-blue?logo=github)](https://materialsproject.github.io/maggma) [![testing](https://github.com/materialsproject/maggma/workflows/testing/badge.svg)](https://github.com/materialsproject/maggma/actions?query=workflow%3Atesting) [![codecov](https://codecov.io/gh/materialsproject/maggma/branch/main/graph/badge.svg)](https://codecov.io/gh/materialsproject/maggma) [![python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&amp;logoColor=white)]()

## What is Maggma

Maggma is a framework to build scientific data processing pipelines from data stored in
a variety of formats -- databases, Azure Blobs, files on disk, etc., all the way to a
REST API. The rest of this README contains a brief, high-level overview of what `maggma` can do.
For more, please refer to [the documentation](https://materialsproject.github.io/maggma)


## Installation from PyPI

Maggma is published on the [Python Package Index](https://pypi.org/project/maggma/).  The preferred tool for installing
packages from *PyPi* is **pip**.  This tool is provided with all modern
versions of Python.

Open your terminal and run the following command.

``` shell
pip install --upgrade maggma
```

## Basic Concepts

`maggma`'s core classes -- [`Store`](#store) and [`Builder`](#builder) -- provide building blocks for
modular data pipelines. Data resides in one or more `Store` and is processed by a
`Builder`. The results of the processing are saved in another `Store`, and so on:

```mermaid
flowchart LR
    s1(Store 1) --Builder 1--> s2(Store 2) --Builder 2--> s3(Store 3)
s2 -- Builder 3-->s4(Store 4)
```

### Store

A major challenge in building scalable data pipelines is dealing with all the different types of data sources out there. Maggma's `Store` class provides a consistent, unified interface for querying data from arbitrary data sources. It was originally built around MongoDB, so it's interface closely resembles `PyMongo` syntax. However, Maggma makes it possible to use that same syntax to query other types of databases, such as Amazon S3, GridFS, or files on disk, [and many others](https://materialsproject.github.io/maggma/getting_started/stores/#list-of-stores). Stores implement methods to `connect`, `query`, find `distinct` values, `groupby` fields, `update` documents, and `remove` documents.

### Builder

Builders represent a data processing step, analogous to an extract-transform-load (ETL) operation in a data
warehouse model. Much like `Store` provides a consistent interface for accessing data, the `Builder` classes
provide a consistent interface for transforming it. `Builder` transformation are each broken into 3 phases: `get_items`, `process_item`, and `update_targets`:

1. `get_items`: Retrieve items from the source Store(s) for processing by the next phase
2. `process_item`: Manipulate the input item and create an output document that is sent to the next phase for storage.
3. `update_target`: Add the processed item to the target Store(s).

Both `get_items` and `update_targets` can perform IO (input/output) to the data stores. `process_item` is expected to not perform any IO so that it can be parallelized by Maggma. Builders can be chained together into an array and then saved as a JSON file to be run on a production system.

### API Tools

TBD - Jason?

## Origin and Maintainers

Maggma has been developed and is maintained by the [Materials Project](https://materialsproject.org/) team at Lawrence Berkeley National Laboratory and the [Materials Project Software Foundation](https://github.com/materialsproject/foundation).

Maggma is written in [Python](http://docs.python-guide.org/en/latest/) and supports Python 3.9+.
