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

CREATE TABLE IF NOT EXISTS JobSeekers (
    seeker_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    major VARCHAR(100),
    grad_year INT
);

CREATE TABLE IF NOT EXISTS JobPosters (
    poster_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    website VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS JobPosts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    poster_id INT,
    title VARCHAR(255) NOT NULL,
    location VARCHAR(100),
    salary DECIMAL(10, 2),
    attendance_type ENUM('remote', 'hybrid', 'on-site') DEFAULT 'on-site',
    description TEXT,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (poster_id) REFERENCES JobPosters(poster_id)
);

CREATE TABLE IF NOT EXISTS Resumes (
    resume_id INT AUTO_INCREMENT PRIMARY KEY,
    seeker_id INT,
    resume_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seeker_id) REFERENCES JobSeekers(seeker_id)
);

CREATE TABLE IF NOT EXISTS Applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    seeker_id INT,
    job_id INT,
    resume_id INT,
    cover_letter TEXT,
    stage VARCHAR(50) DEFAULT 'submitted',
    status VARCHAR(50) DEFAULT 'pending',
    application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seeker_id) REFERENCES JobSeekers(seeker_id),
    FOREIGN KEY (job_id) REFERENCES JobPosts(post_id),
    FOREIGN KEY (resume_id) REFERENCES Resumes(resume_id)
);

INSERT INTO JobSeekers (name, email, major, grad_year)
VALUES
('Alex Johnson', 'alex.j@example.com', 'Computer Science', 2025),
('Maria Reyes', 'maria.r@example.com', 'Data Science', 2026),
('James Kim', 'james.k@example.com', 'Software Engineering', 2024),
('Priya Patel', 'priya.p@example.com', 'Information Systems', 2025);

INSERT INTO JobPosters (company_name, email, website)
VALUES
('TechCorp Inc.', 'hiring@techcorp.com', 'https://techcorp.com'),
('DataVision LLC', 'jobs@datavision.com', 'https://datavision.com'),
('CloudBase Systems', 'recruit@cloudbase.io', 'https://cloudbase.io'),
('Nova Analytics', 'careers@novaanalytics.com', 'https://novaanalytics.com');

INSERT INTO JobPosts (poster_id, title, location, salary, attendance_type, description, is_active)
VALUES
(1, 'Software Engineer', 'Boston, MA', 95000, 'hybrid', 'Build and maintain full-stack web applications using React and Python.', 1),
(1, 'Backend Developer', 'New York, NY', 105000, 'on-site', 'Design scalable REST APIs and manage cloud infrastructure on AWS.', 1),
(2, 'Data Analyst', 'Remote', 80000, 'remote', 'Analyze large datasets and build dashboards to support business decisions.', 1),
(2, 'Machine Learning Engineer', 'Boston, MA', 120000, 'hybrid', 'Develop and deploy ML models for predictive analytics pipelines.', 1),
(3, 'Cloud Engineer', 'Seattle, WA', 115000, 'on-site', 'Manage Kubernetes clusters and CI/CD pipelines for cloud-native services.', 1),
(3, 'DevOps Engineer', 'Remote', 100000, 'remote', 'Automate deployment workflows and monitor production infrastructure.', 1),
(4, 'Business Intelligence Dev', 'Chicago, IL', 88000, 'hybrid', 'Create BI reports and maintain data warehouse integrations.', 1),
(4, 'Junior Data Scientist', 'Remote', 72000, 'remote', 'Support senior data scientists in model development and feature engineering.', 1);

INSERT INTO Resumes (seeker_id, resume_text)
VALUES
(1, 'Alex Johnson - CS graduate. Skills: Python, React, SQL, Git. Experience: intern at startup building REST APIs.'),
(1, 'Alex Johnson - alternate resume focused on data engineering and pipeline work.'),
(2, 'Maria Reyes - Data Science student. Skills: Python, R, Tableau, scikit-learn. GPA 3.9.'),
(3, 'James Kim - Software Engineering grad. Skills: Java, Spring Boot, AWS, Docker.'),
(4, 'Priya Patel - IS graduate. Skills: SQL, Power BI, Excel, Salesforce.');

INSERT INTO Applications (seeker_id, job_id, resume_id, cover_letter, stage, status, application_date)
VALUES
(1, 1, 1, 'I am excited to apply for the Software Engineer role at TechCorp.', 'interview', 'pending', '2025-03-10 09:00:00'),
(1, 3, 1, 'My data analysis experience makes me a strong fit for the Data Analyst role.', 'submitted', 'pending', '2025-03-15 11:30:00'),
(1, 8, 2, 'I am eager to grow as a data scientist and contribute to your team.', 'submitted', 'rejected', '2025-03-18 14:00:00'),
(2, 3, 3, 'As a data science student I have hands-on Tableau and Python experience.', 'offer', 'accepted', '2025-03-05 10:00:00'),
(2, 4, 3, 'I have built ML models for class projects and internships.', 'interview', 'pending', '2025-03-20 09:45:00'),
(3, 2, 4, 'I have strong backend experience with Java and AWS.', 'submitted', 'pending', '2025-04-01 08:00:00'),
(4, 7, 5, 'I have experience with Power BI and SQL reporting in enterprise environments.', 'submitted', 'pending', '2025-04-05 13:00:00');

CREATE TABLE model1_params (
    sequence_number INT,
    beta_vals TEXT
);

INSERT INTO model1_params (sequence_number, beta_vals) VALUES
(1, '[0.25, 0.45, 0.67]');