# parler_warcer
Given a directory containing WARCs of parler posts,
parse out post data and insert into a sqlite db.

## Usage
_on Windows 10, in folder where this was cloned/unzipped_

```
PS D:\DataProjects\parler_warcer> python -m venv venv
PS D:\DataProjects\parler_warcer> .\venv\Scripts\Activate.ps1
PS D:\DataProjects\parler_warcer> .\venv\Scripts\pip3 install -r requirements.txt
PS D:\DataProjects\parler_warcer> .\venv\Scripts\python3 .\parler_warc_to_sqlite.py H:\parler\warc parler.db
```

## Database schema
```sql
create table posts
(
	pid string not null
		primary key,
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
);

create unique index posts_pid_uindex
	on posts (pid);
```
