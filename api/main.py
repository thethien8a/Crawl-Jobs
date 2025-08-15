from fastapi import FastAPI, Query
from typing import Optional
import os
import pymssql

app = FastAPI(title="CrawlJob Read API", version="1.0.0")


def get_conn():
	return pymssql.connect(
		server=os.getenv("SQL_SERVER", "localhost"),
		database=os.getenv("SQL_DATABASE", "JobDatabase"),
		user=os.getenv("SQL_USERNAME", "sa"),
		password=os.getenv("SQL_PASSWORD", ""),
	)


@app.get("/health")
def health():
	return {"status": "ok"}


@app.get("/jobs")
def jobs(
	keyword: Optional[str] = Query(default=None),
	site: Optional[str] = Query(default=None),
	location: Optional[str] = Query(default=None),
	page: int = Query(default=1, ge=1),
	page_size: int = Query(default=20, ge=1, le=200),
):
	offset = (page - 1) * page_size
	where = []
	params = []
	if keyword:
		where.append("(job_title LIKE %s OR job_description LIKE %s OR search_keyword LIKE %s)")
		kw = f"%{keyword}%"
		params.extend([kw, kw, kw])
	if site:
		where.append("source_site = %s")
		params.append(site)
	if location:
		where.append("location LIKE %s")
		params.append(f"%{location}%")
	where_sql = ("WHERE " + " AND ".join(where)) if where else ""
	sql = f"""
	  SELECT job_title, company_name, salary, location, job_type, experience_level,
			 education_level, job_industry, job_position, job_deadline, source_site,
			 job_url, search_keyword, scraped_at, created_at, ISNULL(updated_at, created_at) AS updated_at
	  FROM jobs
	  {where_sql}
	  ORDER BY ISNULL(updated_at, created_at) DESC
	  OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
	"""
	with get_conn() as conn:
		with conn.cursor(as_dict=True) as cur:
			cur.execute(sql, (*params, offset, page_size))
			rows = cur.fetchall()
	return {"page": page, "page_size": page_size, "items": rows}


