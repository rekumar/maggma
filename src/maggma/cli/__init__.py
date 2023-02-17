#!/usr/bin/env python
# coding utf-8


import asyncio
import logging
import sys
from itertools import chain

import click
from monty.serialization import loadfn

from maggma.cli.distributed import find_port
from maggma.cli.multiprocessing import multi
from maggma.cli.serial import serial
from maggma.cli.source_loader import ScriptFinder, load_builder_from_source
from maggma.utils import ReportingHandler, TqdmLoggingHandler


from pydantic import BaseSettings, Field

sys.meta_path.append(ScriptFinder())


class CLISettings(BaseSettings):
    
    WORKER_TIMEOUT: int = Field(
        3600,
        description="Timeout in seconds for a distributed worker",
    )
    
    MANAGER_TIMEOUT: int = Field(
        900,
        description="Timeout in seconds for the worker manager",
    )
    
    class Config:
        env_prefix = "MAGGMA_"
        extra = "ignore"
    

@click.command()
@click.argument("builders", nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    count=True,
    help="Controls logging level per number of v's",
    default=0,
)
@click.option(
    "-n",
    "--num-processes",
    "num_processes",
    help="Number of processes to spawn for each worker. Defaults to single processing",
    default=1,
    type=click.IntRange(1),
)
@click.option(
    "-r",
    "--reporting",
    "reporting_store",
    help="Store in JSON/YAML form to send reporting data to",
    type=click.Path(exists=True),
)
@click.option("-u", "--url", "url", default=None, type=str, help="URL for the distributed manager")
@click.option(
    "-p",
    "--port",
    "port",
    default=None,
    type=int,
    help="Port for distributed communication." " mrun will find an open port if None is provided to the manager",
)
@click.option(
    "-N",
    "--num-chunks",
    "num_chunks",
    default=0,
    type=int,
    help="Number of chunks to distribute to workers",
)
@click.option(
    "-w",
    "--num-workers",
    "num_workers",
    default=0,
    type=int,
    help="Number of distributed workers to process chunks",
)
@click.option("--no_bars", is_flag=True, help="Turns of Progress Bars for headless operations")
@click.option("--rabbitmq", is_flag=True, help="Enables the use of RabbitMQ as the work broker")
@click.option(
    "-q",
    "--queue_prefix",
    "queue_prefix",
    default="builder",
    type=str,
    help="Prefix to use in queue names when RabbitMQ is select as the broker",
)
def run(
    builders,
    verbosity,
    reporting_store,
    num_workers,
    url,
    port,
    num_chunks,
    no_bars,
    num_processes,
    rabbitmq,
    queue_prefix,
):
    # Import proper manager and worker
    if rabbitmq:
        from maggma.cli.rabbitmq import manager, worker
    else:
        from maggma.cli.distributed import manager, worker

    # Set Logging
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(len(levels) - 1, verbosity)]  # capped to number of levels
    root = logging.getLogger()
    root.setLevel(level)
    ch = TqdmLoggingHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    root.addHandler(ch)

    builder_objects = []

    for b in builders:
        if str(b).endswith(".py") or str(b).endswith(".ipynb"):
            builder_objects.append(load_builder_from_source(b))
        else:
            builder_objects.append(loadfn(b))

    builder_objects = [b if isinstance(b, list) else [b] for b in builder_objects]
    builder_objects = list(chain.from_iterable(builder_objects))

    if reporting_store:
        reporting_store = loadfn(reporting_store)
        root.addHandler(ReportingHandler(reporting_store))

    if url:
        if num_chunks > 0:
            # Manager
            if port is None:
                port = find_port()
                root.critical(f"Using random port for mrun manager: {port}")

            if rabbitmq:
                manager(
                    url=url,
                    port=port,
                    builders=builder_objects,
                    num_chunks=num_chunks,
                    num_workers=num_workers,
                    queue_prefix=queue_prefix,
                )
            else:
                manager(
                    url=url,
                    port=port,
                    builders=builder_objects,
                    num_chunks=num_chunks,
                    num_workers=num_workers,
                )

        else:
            # Worker
            if rabbitmq:
                worker(
                    url=url,
                    port=port,
                    num_processes=num_processes,
                    no_bars=no_bars,
                    queue_prefix=queue_prefix,
                )
            else:
                worker(url=url, port=port, num_processes=num_processes, no_bars=no_bars)
    else:
        if num_processes == 1:
            for builder in builder_objects:
                serial(builder, no_bars)
        else:
            loop = asyncio.get_event_loop()
            for builder in builder_objects:
                loop.run_until_complete(multi(builder=builder, num_processes=num_processes, no_bars=no_bars))
