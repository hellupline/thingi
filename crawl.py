#!/usr/bin/env python3

import json
import logging
import os
import pathlib
import time
import urllib.parse

import click
import requests
import tqdm

with open("config.json") as f:
    # need a better way :D
    config = json.load(f)

RESULTS_DIR = pathlib.Path("./results").expanduser().absolute().resolve()

logfmt = "[%(asctime)s : %(levelname)s : %(pathname)s : %(lineno)s : %(funcName)s] %(message)s"
logging.basicConfig(format=logfmt, datefmt="%Y-%m-%dT%H:%M:%S%z")
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {config['api_key']}"})


URL_BASE = urllib.parse.ParseResult(
    scheme="https",
    netloc="api.thingiverse.com",
    path="/things/",
    params="",
    query="",
    fragment="",
)


@click.command()
@click.option("--start", default=1, help="Thingiverse Start ID.")
@click.option("--end", default=5028592, help="Thingiverse End ID.")
def main(start: int, end: int):
    for i in tqdm.tqdm(range(start, end + 1), ncols=80):
        name = str(i).zfill(7)
        filename = RESULTS_DIR / name[0] / name[1] / name[2] / name[3] / f"{name}.json"
        if os.path.exists(filename):
            logger.warning("thing exists: %d", i)
            continue
        try:
            do_request(get_url(i), filename=filename, thing_id=i)
        except Exception:
            return
        logger.info("thing saved: %d", i)
        time.sleep(0.1)


def get_url(i: int) -> str:
    url_path = pathlib.Path(URL_BASE.path) / str(i)
    u = URL_BASE._replace(path=str(url_path))
    return urllib.parse.urlunparse(u)


def do_request(url: str, filename: pathlib.Path, thing_id: int, retries: int = 3):
    while retries > 0:
        try:
            return _do_request(url, filename, thing_id)
        except Exception:
            logger.exception("retry %d at thing: %d", retries, thing_id)
            retries -= 1
            if retries == 0:
                raise


def _do_request(url: str, filename: pathlib.Path, thing_id: int):
    try:
        r = session.request(method="GET", url=url)
        r.raise_for_status()
    except requests.HTTPError as e:
        if e.response.status_code == 403:
            logger.warning("thing forbidden: %d", thing_id)
            with filename.open(mode="w") as f_error:
                json.dump({"status_code": e.response.status_code, "body": r.text}, f_error)
            return
        if e.response.status_code == 404:
            logger.warning("thing not found: %d", thing_id)
            with filename.open(mode="w") as f_error:
                json.dump({"status_code": e.response.status_code, "body": r.text}, f_error)
            return
        logger.exception("failed at thing: %d", thing_id)
        raise
    except Exception:
        logger.exception("failed at thing: %d", thing_id)
        raise
    with filename.open(mode="wb") as f:
        f.write(r.content)


if __name__ == "__main__":
    main()
