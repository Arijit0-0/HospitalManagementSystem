# CareAxis Hospital Management System

CareAxis is a hospital management system built with Flask, MySQL, HTML, CSS, and Bootstrap. It supports patient registration, appointment booking, doctor directory management, audit tracking, admin reporting, and role-based access for patients, doctors, and administrators.

## Tech Stack

- Python 3.14
- Flask
- Flask-Login
- Flask-SQLAlchemy
- PyMySQL
- MySQL via XAMPP
- HTML, CSS, Bootstrap

## Key Features

- Role-based login for `Admin`, `Doctor`, and `Patient`
- Patient appointment booking and editing
- Doctor directory and department mapping
- Appointment dashboard with live counts
- Admin dashboard for system overview
- Reports page with appointment summaries
- Trigger-based audit log from MySQL
- Printable reports for submission/demo use

## Project Structure

```text
New project/
├── PROJECT/
│   ├── main.py
│   ├── static/
│   └── templates/
├── hms.sql
├── requirements.txt
└── README.md
```

## Setup Instructions

1. Start `Apache` and `MySQL` in XAMPP.
2. Open phpMyAdmin and create a database named `hms`.
3. Import `hms.sql` into the `hms` database.
4. Open a terminal in `C:\Users\deyar\OneDrive\Documents\New project`.
5. Install dependencies:

```powershell
py -3.14 -m pip install -r requirements.txt
```

6. Run the application:

```powershell
cd "C:\Users\deyar\OneDrive\Documents\New project\PROJECT"
python main.py
```

7. Open:

```text
http://127.0.0.1:5000
```

## Default Admin Account

- Email: `admin@careaxis.local`
- Password: `Admin@123`

## Main Modules

- `Overview`: dashboard landing page with live operational data
- `Directory`: doctor listing by department
- `Book Visit`: patient appointment booking form
- `Appointments`: booking management table
- `Reports`: admin-only reporting page
- `Activity Log`: admin-only audit trail
- `Admin`: admin-only control center

## Notes

- MySQL is provided by XAMPP, but the application itself is a Flask/Python project, not a PHP project.
- The system uses password hashing for newly created accounts.
- Audit history depends on the SQL triggers included in `hms.sql`.

## Future Enhancements

- Billing and invoice generation
- Bed or room allocation
- Laboratory test management
- Prescription records
- File upload for medical documents

## GitHub Checklist

Before publishing the repository, make sure these files are included:

- `PROJECT/main.py`
- `PROJECT/templates/`
- `PROJECT/static/`
- `hms.sql`
- `requirements.txt`
- `render.yaml`
- `README.md`
- `PROJECT_REPORT.md`

## Render Deployment

This repository includes a `render.yaml` blueprint for simple deployment on Render.

### Recommended free deployment mode

- Render web service
- SQLite fallback storage for demo hosting
- Seeded admin user and doctor directory on first boot

### Deploy Steps

1. Push this repository to GitHub.
2. Sign in to Render.
3. Create a new Blueprint instance from the GitHub repository.
4. Render will read `render.yaml` automatically.
5. Wait for the build to finish.
6. Open the generated `onrender.com` URL.

### Render Notes

- Local development still uses XAMPP MySQL by default.
- Render deployment uses `USE_SQLITE=true` from `render.yaml` for a free, self-contained demo setup.
- The first startup automatically creates tables and seeds:
  - default admin account
  - doctor directory data

## Default Demo Credentials

- Admin Email: `admin@careaxis.local`
- Admin Password: `Admin@123`
