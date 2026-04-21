DROP DATABASE IF EXISTS ngo_db;
CREATE DATABASE IF NOT EXISTS ngo_db;

USE ngo_db;


CREATE TABLE IF NOT EXISTS WorldNGOs (
    NGO_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Country VARCHAR(100) NOT NULL,
    Founding_Year INTEGER,
    Focus_Area VARCHAR(100),
    Website VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Projects (
    Project_ID INT AUTO_INCREMENT PRIMARY KEY,
    Project_Name VARCHAR(255) NOT NULL,
    Focus_Area VARCHAR(100),
    Budget DECIMAL(15, 2),
    NGO_ID INT,
    Start_Date DATE,
    End_Date DATE,
    FOREIGN KEY (NGO_ID) REFERENCES WorldNGOs(NGO_ID)
);

CREATE TABLE IF NOT EXISTS Donors (
    Donor_ID INT AUTO_INCREMENT PRIMARY KEY,
    Donor_Name VARCHAR(255) NOT NULL,
    Donor_Type ENUM('Individual', 'Organization') NOT NULL,
    Donation_Amount DECIMAL(15, 2),
    NGO_ID INT,
    FOREIGN KEY (NGO_ID) REFERENCES WorldNGOs(NGO_ID)
);

INSERT INTO WorldNGOs (Name, Country, Founding_Year, Focus_Area, Website)
VALUES
('World Wildlife Fund', 'United States', 1961, 'Environmental Conservation', 'https://www.worldwildlife.org'),
('Doctors Without Borders', 'France', 1971, 'Medical Relief', 'https://www.msf.org'),
('Oxfam International', 'United Kingdom', 1995, 'Poverty and Inequality', 'https://www.oxfam.org'),
('Amnesty International', 'United Kingdom', 1961, 'Human Rights', 'https://www.amnesty.org'),
('Save the Children', 'United States', 1919, 'Child Welfare', 'https://www.savethechildren.org'),
('Greenpeace', 'Netherlands', 1971, 'Environmental Protection', 'https://www.greenpeace.org'),
('International Red Cross', 'Switzerland', 1863, 'Humanitarian Aid', 'https://www.icrc.org'),
('CARE International', 'Switzerland', 1945, 'Global Poverty', 'https://www.care-international.org'),
('Habitat for Humanity', 'United States', 1976, 'Affordable Housing', 'https://www.habitat.org'),
('Plan International', 'United Kingdom', 1937, 'Child Rights', 'https://plan-international.org');

INSERT INTO Projects (Project_Name, Focus_Area, Budget, NGO_ID, Start_Date, End_Date)
VALUES
('Save the Amazon', 'Environmental Conservation', 5000000.00, 1, '2022-01-01', '2024-12-31'),
('Emergency Medical Aid in Syria', 'Medical Relief', 3000000.00, 2, '2023-03-01', '2023-12-31'),
('Education for All', 'Poverty and Inequality', 2000000.00, 3, '2021-06-01', '2025-05-31'),
('Human Rights Advocacy in Asia', 'Human Rights', 1500000.00, 4, '2022-09-01', '2023-08-31'),
('Child Nutrition Program', 'Child Welfare', 2500000.00, 5, '2022-01-01', '2024-01-01');

INSERT INTO Donors (Donor_Name, Donor_Type, Donation_Amount, NGO_ID)
VALUES
('Bill & Melinda Gates Foundation', 'Organization', 10000000.00, 1),
('Elon Musk', 'Individual', 5000000.00, 2),
('Google.org', 'Organization', 2000000.00, 3),
('Open Society Foundations', 'Organization', 3000000.00, 4),
('Anonymous Philanthropist', 'Individual', 1000000.00, 5);

CREATE TABLE IF NOT EXISTS job_seekers (
    seeker_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    major VARCHAR(100),
    grad_year INT
);

CREATE TABLE IF NOT EXISTS job_posters (
    poster_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    website VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS job_posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    poster_id INT,
    title VARCHAR(255) NOT NULL,
    location VARCHAR(100),
    salary DECIMAL(10, 2),
    attendance_type ENUM('remote', 'hybrid', 'on-site') DEFAULT 'on-site',
    description TEXT,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (poster_id) REFERENCES job_posters(poster_id)
);

CREATE TABLE IF NOT EXISTS resumes (
    resume_id INT AUTO_INCREMENT PRIMARY KEY,
    seeker_id INT,
    resume_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seeker_id) REFERENCES job_seekers(seeker_id)
);

CREATE TABLE IF NOT EXISTS applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    seeker_id INT,
    job_id INT,
    resume_id INT,
    cover_letter TEXT,
    stage VARCHAR(50) DEFAULT 'submitted',
    status VARCHAR(50) DEFAULT 'pending',
    application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seeker_id) REFERENCES job_seekers(seeker_id),
    FOREIGN KEY (job_id) REFERENCES job_posts(post_id),
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id)
);

INSERT INTO job_seekers (name, email, major, grad_year)
VALUES
('Alex Johnson', 'alex.j@example.com', 'Computer Science', 2025),
('Maria Reyes', 'maria.r@example.com', 'Data Science', 2026),
('James Kim', 'james.k@example.com', 'Software Engineering', 2024),
('Priya Patel', 'priya.p@example.com', 'Information Systems', 2025),
('Ethan Brooks', 'ethan.b@example.com', 'Computer Engineering', 2025),
('Sophia Nguyen', 'sophia.n@example.com', 'Cybersecurity', 2026),
('Liam Carter', 'liam.c@example.com', 'Data Science', 2024),
('Aisha Williams', 'aisha.w@example.com', 'Computer Science', 2027),
('Noah Martinez', 'noah.m@example.com', 'Software Engineering', 2025),
('Emma Thompson', 'emma.t@example.com', 'Business Analytics', 2026);

INSERT INTO job_posters (company_name, email, website)
VALUES
('TechCorp Inc.', 'hiring@techcorp.com', 'https://techcorp.com'),
('DataVision LLC', 'jobs@datavision.com', 'https://datavision.com'),
('CloudBase Systems', 'recruit@cloudbase.io', 'https://cloudbase.io'),
('Nova Analytics', 'careers@novaanalytics.com', 'https://novaanalytics.com'),
('Apex Software', 'jobs@apexsoftware.com', 'https://apexsoftware.com'),
('Meridian Health Tech', 'careers@meridianht.com', 'https://meridianht.com'),
('Orion Fintech', 'hire@orionfintech.io', 'https://orionfintech.io');

INSERT INTO job_posts (poster_id, title, location, salary, attendance_type, description, is_active)
VALUES
(1, 'Software Engineer', 'Boston, MA', 95000, 'hybrid', 'Build and maintain full-stack web applications using React and Python.', 1),
(1, 'Backend Developer', 'New York, NY', 105000, 'on-site', 'Design scalable REST APIs and manage cloud infrastructure on AWS.', 1),
(2, 'Data Analyst', 'Remote', 80000, 'remote', 'Analyze large datasets and build dashboards to support business decisions.', 1),
(2, 'Machine Learning Engineer', 'Boston, MA', 120000, 'hybrid', 'Develop and deploy ML models for predictive analytics pipelines.', 1),
(3, 'Cloud Engineer', 'Seattle, WA', 115000, 'on-site', 'Manage Kubernetes clusters and CI/CD pipelines for cloud-native services.', 1),
(3, 'DevOps Engineer', 'Remote', 100000, 'remote', 'Automate deployment workflows and monitor production infrastructure.', 1),
(4, 'Business Intelligence Dev', 'Chicago, IL', 88000, 'hybrid', 'Create BI reports and maintain data warehouse integrations.', 1),
(4, 'Junior Data Scientist', 'Remote', 72000, 'remote', 'Support senior data scientists in model development and feature engineering.', 1),
(5, 'Frontend Engineer', 'Boston, MA', 90000, 'hybrid', 'Build responsive UIs using React and TypeScript for enterprise SaaS products.', 1),
(5, 'Full Stack Developer', 'Austin, TX', 98000, 'on-site', 'Work across frontend and backend to ship new product features every sprint.', 1),
(5, 'QA Engineer', 'Remote', 75000, 'remote', 'Design and execute automated test suites to ensure product quality.', 1),
(6, 'Software Engineer - Healthcare', 'Boston, MA', 102000, 'hybrid', 'Build HIPAA-compliant data pipelines and patient-facing web tools.', 1),
(6, 'Data Engineer', 'Remote', 110000, 'remote', 'Design ETL pipelines and maintain cloud data warehouses on Snowflake and AWS.', 1),
(7, 'Quantitative Analyst', 'New York, NY', 130000, 'on-site', 'Build risk models and trading algorithms using Python and SQL.', 1),
(7, 'Platform Engineer', 'New York, NY', 118000, 'hybrid', 'Maintain internal developer platforms and improve CI/CD tooling.', 1);

INSERT INTO resumes (seeker_id, resume_text)
VALUES
(1, 'Alex Johnson - CS graduate. Skills: Python, React, SQL, Git. Experience: intern at startup building REST APIs.'),
(1, 'Alex Johnson - alternate resume focused on data engineering and pipeline work.'),
(2, 'Maria Reyes - Data Science student. Skills: Python, R, Tableau, scikit-learn. GPA 3.9.'),
(3, 'James Kim - Software Engineering grad. Skills: Java, Spring Boot, AWS, Docker.'),
(4, 'Priya Patel - IS graduate. Skills: SQL, Power BI, Excel, Salesforce.'),
(5, 'Ethan Brooks - Computer Engineering student. Skills: C++, Python, Embedded Systems, FPGA. Experience: hardware lab assistant.'),
(6, 'Sophia Nguyen - Cybersecurity student. Skills: Network Security, Python, Wireshark, Penetration Testing. GPA 3.8.'),
(7, 'Liam Carter - Data Science grad. Skills: Python, TensorFlow, PyTorch, SQL, Spark. Experience: ML intern at analytics firm.'),
(8, 'Aisha Williams - CS student. Skills: Java, Python, React, Node.js. Experience: teaching assistant for intro programming.'),
(9, 'Noah Martinez - Software Engineering student. Skills: Go, Kubernetes, Docker, gRPC. Experience: DevOps intern at cloud startup.'),
(10, 'Emma Thompson - Business Analytics student. Skills: SQL, Tableau, Excel, Python, Salesforce. GPA 3.7.');

INSERT INTO applications (seeker_id, job_id, resume_id, cover_letter, stage, status, application_date)
VALUES
(1, 1, 1, 'I am excited to apply for the Software Engineer role at TechCorp.', 'interview', 'pending', '2025-03-10 09:00:00'),
(1, 3, 1, 'My data analysis experience makes me a strong fit for the Data Analyst role.', 'submitted', 'pending', '2025-03-15 11:30:00'),
(1, 8, 2, 'I am eager to grow as a data scientist and contribute to your team.', 'submitted', 'rejected', '2025-03-18 14:00:00'),
(1, 9, 1, 'I have built responsive UIs with React and TypeScript and would love to join your frontend team.', 'interview', 'pending', '2025-03-22 10:00:00'),
(1, 12, 1, 'I am passionate about building healthcare software and meet all the requirements listed.', 'offer', 'accepted', '2025-03-28 09:00:00'),
(1, 13, 2, 'I have experience designing ETL pipelines and working with cloud data warehouses.', 'submitted', 'pending', '2025-04-02 11:00:00'),
(1, 6, 1, 'I am excited about the DevOps Engineer role and have hands-on experience with CI/CD pipelines.', 'submitted', 'rejected', '2025-04-08 08:30:00'),
(1, 15, 2, 'I am eager to contribute to your platform engineering team and improve developer tooling.', 'interview', 'pending', '2025-04-10 14:00:00'),
(2, 3, 3, 'As a data science student I have hands-on Tableau and Python experience.', 'offer', 'accepted', '2025-03-05 10:00:00'),
(2, 4, 3, 'I have built ML models for class projects and internships.', 'interview', 'pending', '2025-03-20 09:45:00'),
(2, 8, 3, 'I am excited to support senior data scientists and grow my skills in model development.', 'submitted', 'pending', '2025-04-01 12:00:00'),
(3, 2, 4, 'I have strong backend experience with Java and AWS.', 'submitted', 'pending', '2025-04-01 08:00:00'),
(3, 5, 4, 'I have hands-on experience with Kubernetes and Docker from my AWS internship.', 'interview', 'pending', '2025-04-03 09:00:00'),
(3, 6, 4, 'I am passionate about DevOps and have automated deployment workflows in past roles.', 'submitted', 'rejected', '2025-04-07 10:30:00'),
(4, 7, 5, 'I have experience with Power BI and SQL reporting in enterprise environments.', 'submitted', 'pending', '2025-04-05 13:00:00'),
(4, 3, 5, 'My SQL and data visualization skills make me a great fit for the Data Analyst role.', 'interview', 'pending', '2025-04-08 11:00:00'),
(5, 5, 6, 'My background in computer engineering gives me strong cloud infrastructure fundamentals.', 'submitted', 'pending', '2025-04-06 09:00:00'),
(5, 10, 6, 'I love building full-stack features and thrive in sprint-based environments.', 'submitted', 'pending', '2025-04-09 15:00:00'),
(6, 6, 7, 'My cybersecurity background helps me build and monitor secure production infrastructure.', 'interview', 'pending', '2025-04-04 08:00:00'),
(6, 15, 7, 'I am excited to contribute to internal developer platforms and security tooling.', 'submitted', 'pending', '2025-04-11 10:00:00'),
(7, 4, 8, 'I have built and deployed ML models using TensorFlow and scikit-learn for real-world datasets.', 'offer', 'accepted', '2025-03-15 09:00:00'),
(7, 13, 8, 'I have experience with Spark and Snowflake and would love to design data pipelines for your team.', 'interview', 'pending', '2025-04-02 14:00:00'),
(8, 1, 9, 'I am a motivated CS student eager to contribute to full-stack web application development.', 'submitted', 'pending', '2025-04-10 09:30:00'),
(8, 9, 9, 'I have built React projects and am excited to join your frontend engineering team.', 'submitted', 'pending', '2025-04-12 11:00:00'),
(9, 6, 10, 'My DevOps internship gave me hands-on experience with CI/CD automation and monitoring.', 'offer', 'pending', '2025-03-25 08:00:00'),
(9, 5, 10, 'I have deployed Kubernetes clusters and would love to manage cloud-native services for your team.', 'interview', 'pending', '2025-04-05 10:00:00'),
(10, 7, 11, 'My BI coursework and SQL expertise make me a strong candidate for this reporting role.', 'submitted', 'pending', '2025-04-07 13:00:00'),
(10, 3, 11, 'I have built Tableau dashboards and analyzed business datasets in my analytics coursework.', 'interview', 'pending', '2025-04-09 09:00:00');

CREATE TABLE model1_params (
    sequence_number INT,
    beta_vals TEXT
);

INSERT INTO model1_params (sequence_number, beta_vals) VALUES
(1, '[0.25, 0.45, 0.67]');