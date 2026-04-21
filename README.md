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
