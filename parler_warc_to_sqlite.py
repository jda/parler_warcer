#!/usr/bin/env python3
import click
import parler
from glob import glob
import sqlite3
import logging
from tqdm import tqdm

logging.basicConfig(encoding='utf-8', level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def prep_db(dbh):
    dbh.execute("""create table if not exists posts
(
pid string not null PRIMARY KEY,
display_name string,
user_name string not null,
profile_photo string,
post_text string,
post_image string,
orig_reltime string,
post_time string,
impressions int default 0 not null,
url string not null,
req_time string not null
);""")

    try:
        dbh.execute("create unique index posts_pid_uindex on posts (pid);")
    except:
        logging.warning("could not create unique index")

    dbh.execute("PRAGMA synchronous = OFF")
    dbh.execute("PRAGMA journal_mode = OFF")

def glob_warc(dir):
    gz_in_warcs = glob(f"{dir}/*.warc.gz", recursive=True)
    plain_in_warcs = glob(f"{dir}/*.warc", recursive=True)
    return gz_in_warcs + plain_in_warcs

@click.command()
@click.argument('warcdir')
@click.argument('dbfile')
def gen_db_from_warc(warcdir, dbfile):
    warcs = glob_warc(warcdir)
    db = sqlite3.connect(dbfile)
    prep_db(db)

    pbar = tqdm(warcs)
    for warc in pbar:
        pbar.set_description(f"processing {warc}")
        db.executemany(
            """INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(pid) DO UPDATE SET 
orig_reltime=excluded.orig_reltime, 
post_time=excluded.post_time,
impressions=excluded.impressions,
req_time=excluded.req_time
WHERE excluded.impressions>impressions;
""",
            parler.read_parler_warc(warc)
        )
        db.commit()

if __name__ == '__main__':
    gen_db_from_warc()
