DROP DATABASE IF EXISTS UniWorks;
CREATE DATABASE UniWorks;
USE UniWorks;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL,
    full_name  VARCHAR(100) NOT NULL,
    is_active  BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT CURRENT_TIMESTAMP
                  ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE INDEX (email)
);

CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT,
    has_access BOOLEAN DEFAULT 1,
    role VARCHAR(50) NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (admin_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE job_seekers (
    seeker_id INT AUTO_INCREMENT,
    major VARCHAR(100) NOT NULL,
    profile_picture VARCHAR(255),
    city_state VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    degree_level ENUM('Bachelors', 'Masters', 'PHD') NOT NULL,
    graduation_year DATE NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (seeker_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE job_posters (
    poster_id INT AUTO_INCREMENT,
    company_name VARCHAR(100) NOT NULL,
    industry VARCHAR(150),
    user_id INT NOT NULL,
    PRIMARY KEY (poster_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE company_websites (
    poster_id INT,
    website_link VARCHAR(255),
    PRIMARY KEY (poster_id, website_link),
    FOREIGN KEY (poster_id) REFERENCES job_posters(poster_id)
);

CREATE TABLE resumes (
    resume_id INT AUTO_INCREMENT,
    education TEXT,
    work_experience TEXT,
    personal_project TEXT,
    hobby TEXT,
    author_id INT NOT NULL,
    PRIMARY KEY (resume_id),
    FOREIGN KEY (author_id) REFERENCES job_seekers(seeker_id)
);

CREATE TABLE personal_websites (
    resume_id INT,
    website VARCHAR(255),
    PRIMARY KEY (resume_id, website),
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id)
);

CREATE TABLE system_logs (
    log_id INT AUTO_INCREMENT,
    error_code VARCHAR(50) NOT NULL,
    error_description TEXT NOT NULL,
    resolved_at DATE,
    resolution_status ENUM('Started', 'In progress', 'Resolved') NOT NULL,
    creator_id INT NOT NULL,
    PRIMARY KEY (log_id, creator_id),
    FOREIGN KEY (creator_id) REFERENCES admins(admin_id)
);

CREATE TABLE job_posts (
    post_id INT AUTO_INCREMENT,
    job_title VARCHAR(150) NOT NULL,
    job_salary DECIMAL(10,2),
    job_description TEXT,
    job_duration VARCHAR(100) NOT NULL,
    city_state VARCHAR(100) NOT NULL,
    attendance_type VARCHAR(50),
    is_active BOOLEAN DEFAULT 1,
    poster_id INT NOT NULL,
    PRIMARY KEY (post_id),
    FOREIGN KEY (poster_id) REFERENCES job_posters(poster_id)
);

CREATE TABLE job_links (
    post_id INT,
    job_link VARCHAR(255),
    PRIMARY KEY (post_id, job_link),
    FOREIGN KEY (post_id) REFERENCES job_posts(post_id)
);

CREATE TABLE job_limits (
    limit_id INT AUTO_INCREMENT,
    max_count INT,
    discipline VARCHAR(100),
    min_gpa DECIMAL(3,2),
    university VARCHAR(150),
    job_id INT NOT NULL,
    PRIMARY KEY (limit_id),
    FOREIGN KEY (job_id) REFERENCES job_posts(post_id)
);

CREATE TABLE applications (
    application_id INT AUTO_INCREMENT,
    cover_letter TEXT,
    stage VARCHAR(50),
    status VARCHAR(50),
    application_date DATE NOT NULL,
    applicant_id INT NOT NULL,
    job_id INT NOT NULL,
    resume_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (application_id),
    FOREIGN KEY (applicant_id) REFERENCES job_seekers(seeker_id),
    FOREIGN KEY (job_id) REFERENCES job_posts(post_id),
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id)
);

CREATE TABLE activities (
    activity_num INT AUTO_INCREMENT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    activity_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    notes TEXT,
    type ENUM('Interview', 'Offer') NOT NULL,
    status ENUM('Rejected', 'Accepted', 'Unknown'),
    application_id INT NOT NULL,
    PRIMARY KEY (activity_num, application_id),
    FOREIGN KEY (application_id) REFERENCES applications(application_id)
);

CREATE TABLE data_reports (
    report_id INT AUTO_INCREMENT NOT NULL,
    filter_criteria TEXT,
    description TEXT,
    create_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                          ON UPDATE CURRENT_TIMESTAMP,
    creator_id INT NOT NULL,
    PRIMARY KEY (report_id),
    FOREIGN KEY (creator_id) REFERENCES admins(admin_id)
);

CREATE TABLE application_reports (
    report_id INT,
    application_id INT,
    PRIMARY KEY (report_id, application_id),
    FOREIGN KEY (report_id) REFERENCES data_reports(report_id),
    FOREIGN KEY (application_id) REFERENCES applications(application_id)
);