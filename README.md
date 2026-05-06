# Django E-Store (Production Ready)

A premium, full-stack e-commerce application built with Django and Bootstrap 5.

## Features
- **User System**: Custom Auth, Profile, Multiple Addresses.
- **Product System**: Categories, Search, Multiple Images, Stock Tracking.
- **Cart**: Persistent cart, Guest checkout ready.
- **Orders**: Status tracking, Admin management.
- **Security**: CSRF, Environment Variables, Secure Auth.

## Local Setup
1. **Clone and Navigate**:
   ```bash
   cd d:/ecom
   ```
2. **Setup Environment**:
   - Rename `.env.example` to `.env` (or use the one provided).
   - Install dependencies: `pip install -r requirements.txt`.
3. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```
4. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```
5. **Start Server**:
   ```bash
   python manage.py runserver
   ```

## Deployment Instructions

### Render / Heroku
1. **Environment Variables**: Add all keys from `.env` to the platform's dashboard.
2. **Database**: Provision a PostgreSQL instance.
3. **Build Command**: `pip install -r requirements.txt; python manage.py migrate; python manage.py collectstatic --no-input`
4. **Start Command**: `gunicorn core.wsgi`

### Static Files
- WhiteNoise is pre-configured to serve static files.
- `STATIC_ROOT` is set to `staticfiles`.
