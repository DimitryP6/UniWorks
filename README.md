# UniWorks

**UniWorks** is a data-driven internship and job search platform designed for university students, employers, career analysts, and system administrators in one centralized system. Students can manage job applications across multiple platforms in one place, employers can target qualified candidates, and data analysts can track hiring trends and outcomes. 

## Team ATDM

| Name | Northeastern Email |
|---|---|
| Armarni Hall (Point Person) | hall.ar@northeastern.edu |
| Seongcheol Hong | hong.seon@northeastern.edu |
| Yinuo Bai | bai.yinu@northeastern.edu |
| Dimitry Pianykh | pianykh.d@northeastern.edu |

## User Personas

- **Job Seeker (Sarah Smith)** – A university student looking to manage and track job applications in one place
- **Job Poster (Tom Bombadil)** – An employer posting jobs and reviewing applicants
- **Data Analyst (Lauren Mitchell)** – A career center analyst tracking hiring trends and student outcomes
- **System Administrator (Alex Rial)** – A platform admin maintaining data integrity and system health

## Prerequisites
In order to populate the database with fake values, run the _database-files/data_generator.py_ script,
which will in turn create a _02_uniworks_dml.sql_, which can then be composed when Docker runs to populate the database initially.
If _database-files/data_generator.py_ is not run, then there will be no fake data inserted.
Also, a _.env_ file can be created under the api subdirectory, and Docker's compose command should work.

## Pitch & Demo Video

https://northeastern-my.sharepoint.com/:v:/r/personal/hall_ar_northeastern_edu/Documents/Recordings/Project%20recording-20260421_111949-Meeting%20Recording.mp4?csf=1&web=1&e=dA1MBL&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D

## Set up Info 
 
### 1. Clone the repo

```bash
git clone <your-repo-url>
cd UniWorks
```

### 2. Create the '.env' file

Make a .env file in the api folder in this format
```
SECRET_KEY=your-secret-key
DB_USER=root
DB_HOST=db
DB_PORT=3306
DB_NAME=UniWorks
MYSQL_ROOT_PASSWORD=your-strong-password
```

### 3. Start the Docker Containers

```bash
docker compose up -d --build
```

### 4. Stopping the Containers
```bash
docker compose down
```
