# 🧑‍💼 Job Board Website API

Welcome to the **Job Board Website**, a modern backend system for job listings, applications, and recruitment workflows. Built with **Django 5**, **DRF**, **MySQL**, and **Docker**, it supports authentication, user profiles, job postings, applications, interviews, and admin control — all with clean API documentation via **Swagger**.

---

## 🚀 Features

### 🧾 Core

* ✅ Authentication with Djoser (Registration, Login, Reset, Activation)
* ✅ Employer & Applicant Profiles
* ✅ Custom Email Availability Check

### 🧳 Recruitment

* ✅ Job Categories & Tags
* ✅ Company Profiles
* ✅ Job Postings
* ✅ Applications & Status Management
* ✅ Interview Scheduling
* ✅ Applicant Notes (Private to Employers)

### 📚 API & Dev Tools

* 📘 Swagger & ReDoc API Documentation (`/swagger/`, `/redoc/`)
* 🛠 Django Debug Toolbar
* 🔐 Token Authentication (DRF + Djoser)
* 📦 Fully Dockerized with MySQL service

---

## ⚙️ Tech Stack

| Layer            | Technology                 |
| ---------------- | -------------------------- |
| Backend          | Django 5, DRF              |
| Auth             | Djoser, SimpleJWT          |
| Database         | MySQL (Dockerized)         |
| Docs             | drf-yasg (Swagger/OpenAPI) |
| Containerization | Docker + docker-compose    |
| Dev Tools        | Django Debug Toolbar       |

---

## 🐳 Docker Setup

1. **Build and start services**:

```bash
docker-compose up --build
```

2. **Run migrations**:

```bash
docker-compose exec web python manage.py migrate
```

3. **Create superuser (optional)**:

```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Collect static files**:

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

> Swagger UI: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)

---

## 🧪 API Endpoints

All API endpoints follow a clean versioned structure:

| Endpoint                         | Description              |
| -------------------------------- | ------------------------ |
| `/api/auth/`                     | Djoser Auth Endpoints    |
| `/api/core/users/`               | User List & Detail       |
| `/api/core/employer-profiles/`   | Employer Profiles        |
| `/api/core/applicant-profiles/`  | Applicant Profiles       |
| `/api/core/check-email/`         | Email Availability Check |
| `/api/recruitment/categories/`   | Job Categories           |
| `/api/recruitment/jobs/`         | Job Listings             |
| `/api/recruitment/applications/` | Application Submission   |
| `/swagger/`                      | Swagger UI               |
| `/redoc/`                        | ReDoc UI                 |

---

## 🔐 Environment Variables (.env.docker)

```env
DEBUG=True
SECRET_KEY=your-secret-key
MYSQL_DATABASE=jobboard_db
DB_USER=root
DB_PASSWORD=your-db-password
DB_HOST=db
DB_PORT=3306
MYSQL_ROOT_PASSWORD=your-db-root-password
```

---

## 🧠 Author

Developed by **Hatef Barin** — powered by Django, Docker, and clean code.

> Feel free to fork, modify, and contribute. Pull requests welcome!

---

## 📄 License

Licensed under the [BSD License](https://opensource.org/licenses/BSD-3-Clause).
