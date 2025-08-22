# EHR System - Electronic Health Records for Small Clinics

## Project Overview

This EHR (Electronic Health Records) application is designed specifically for small clinics in Pakistan. It provides a comprehensive digital solution for managing patient records, medical visits, and healthcare documentation with AI-powered features for transcription and medical summarization.

### Key Features

- **Multi-Portal System**: Separate interfaces for hospital management, doctors, and patients
- **Patient Management**: Complete patient registration and medical record management
- **Medical Record Number (MRN) System**: Unique identification for each patient with phone-based search
- **AI-Powered Transcription**: Convert doctor-patient conversations to text using AssemblyAI
- **Medical Summarization**: Generate meaningful medical summaries using OpenAI GPT-4
- **File Management**: Upload and manage medical reports, prescriptions, and clinical notes
- **Phone-based Authentication**: OTP-based login system using phone numbers
- **RESTful API**: Comprehensive API with OpenAPI/Swagger documentation

### Technology Stack

- **Backend**: Django 5.0.6 with Django Rest Framework
- **Database**: PostgreSQL
- **Authentication**: Token-based authentication with OTP
- **AI Services**: OpenAI GPT-4 for summarization, AssemblyAI for transcription
- **File Storage**: AWS S3 integration
- **Task Queue**: Celery with Redis
- **Documentation**: OpenAPI/Swagger with drf-yasg

## System Architecture

### Core Applications

1. **accounts**: User management, authentication, and authorization
2. **patients**: Patient registration, profiles, and file management
3. **medical_records**: Medical visits, notes, prescriptions, and history
4. **ai_services**: AI transcription and summarization services

### Key Models

- **User**: Extended Django user with phone-based authentication
- **Patient**: Patient profiles with MRN system
- **MedicalVisit**: Doctor-patient consultations with detailed records
- **AudioRecording**: Visit recordings with AI transcription
- **AIGeneratedSummary**: AI-powered medical summaries
- **Prescription**: Digital prescriptions and medication records

## API Endpoints

### Authentication (`/api/v1/auth/`)
- `POST /register/` - User registration
- `POST /send-otp/` - Send OTP to phone
- `POST /verify-otp/` - Verify OTP and login
- `GET/PUT /profile/` - User profile management
- `POST/GET/PUT /hospital-profile/` - Hospital staff profile
- `POST/GET/PUT /doctor-profile/` - Doctor profile

### Patients (`/api/v1/patients/`)
- `GET/POST /` - List/create patients
- `GET/PUT/DELETE /{mrn}/` - Patient detail operations
- `GET /search/phone/{phone}/` - Search patients by phone
- `GET /search/mrn/{mrn}/` - Get patient by MRN
- `GET/POST /{mrn}/files/` - Patient file management
- `GET/POST /{mrn}/emergency-contacts/` - Emergency contacts

### Medical Records (`/api/v1/medical-records/`)
- `GET/POST /visits/` - Medical visits management
- `GET/PUT/DELETE /visits/{id}/` - Visit detail operations
- `GET /history/{mrn}/` - Patient medical history
- `GET/POST /visits/{id}/recordings/` - Audio recordings
- `GET/POST /visits/{id}/notes/` - Medical notes
- `GET/POST /visits/{id}/prescriptions/` - Prescriptions
- `GET /summaries/{mrn}/` - AI summaries

### AI Services (`/api/v1/ai/`)
- `POST /transcription/start/` - Start audio transcription
- `GET /transcription/status/{id}/` - Transcription status
- `POST /summary/visit/` - Generate visit summary
- `POST /summary/patient-history/` - Generate patient history summary
- `GET /stats/` - AI processing statistics

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- AWS S3 bucket (for file storage)
- OpenAI API key
- AssemblyAI API key

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ehr-system
   ```

2. **Create and activate virtual environment**
   ```bash
   cd server
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb ehr_system
   
   # Create superuser for PostgreSQL
   sudo -u postgres createuser --superuser yourusername
   sudo -u postgres psql -c "ALTER USER yourusername PASSWORD 'yourpassword';"
   ```

5. **Environment Configuration**
   ```bash
   # Copy environment file
   cp .env.example .env
   
   # Edit .env file with your configuration
   nano .env
   ```

6. **Database Migration**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create Django Superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

9. **Start Redis Server**
   ```bash
   redis-server
   ```

10. **Start Celery Worker** (in a new terminal)
    ```bash
    cd server
    celery -A ehr_system worker -l info
    ```

11. **Run Development Server**
    ```bash
    python manage.py runserver
    ```

### Production Server Setup

#### Using Docker (Recommended)

1. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     db:
       image: postgres:13
       environment:
         POSTGRES_DB: ehr_system
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: yourpassword
       volumes:
         - postgres_data:/var/lib/postgresql/data
     
     redis:
       image: redis:6-alpine
     
     web:
       build: .
       command: gunicorn ehr_system.wsgi:application --bind 0.0.0.0:8000
       volumes:
         - .:/code
         - static_volume:/code/staticfiles
         - media_volume:/code/media
       ports:
         - "8000:8000"
       depends_on:
         - db
         - redis
       env_file:
         - .env
     
     celery:
       build: .
       command: celery -A ehr_system worker -l info
       volumes:
         - .:/code
       depends_on:
         - db
         - redis
       env_file:
         - .env
     
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - static_volume:/var/www/static
         - media_volume:/var/www/media
       depends_on:
         - web

   volumes:
     postgres_data:
     static_volume:
     media_volume:
   ```

2. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11

   WORKDIR /code

   COPY requirements.txt /code/
   RUN pip install -r requirements.txt

   COPY . /code/

   RUN python manage.py collectstatic --noinput

   EXPOSE 8000

   CMD ["gunicorn", "ehr_system.wsgi:application", "--bind", "0.0.0.0:8000"]
   ```

3. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   ```

#### Manual Server Setup

1. **Install system dependencies**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv postgresql postgresql-contrib redis-server nginx
   ```

2. **Setup application**
   ```bash
   # Create application user
   sudo useradd --system --gid nginx --shell /bin/bash --home /var/www/ehr-system ehr-system
   
   # Clone repository
   sudo -u ehr-system git clone <repo-url> /var/www/ehr-system
   cd /var/www/ehr-system/server
   
   # Setup virtual environment
   sudo -u ehr-system python3.11 -m venv venv
   sudo -u ehr-system ./venv/bin/pip install -r requirements.txt
   ```

3. **Configure PostgreSQL**
   ```bash
   sudo -u postgres createdb ehr_system
   sudo -u postgres createuser ehr_system
   sudo -u postgres psql -c "ALTER USER ehr_system PASSWORD 'secure_password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ehr_system TO ehr_system;"
   ```

4. **Setup Gunicorn service**
   ```bash
   sudo nano /etc/systemd/system/ehr-system.service
   ```
   
   ```ini
   [Unit]
   Description=EHR System Django Application
   After=network.target

   [Service]
   User=ehr-system
   Group=nginx
   WorkingDirectory=/var/www/ehr-system/server
   ExecStart=/var/www/ehr-system/server/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/ehr-system/server/ehr_system.sock ehr_system.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

5. **Setup Celery service**
   ```bash
   sudo nano /etc/systemd/system/ehr-system-celery.service
   ```
   
   ```ini
   [Unit]
   Description=EHR System Celery Worker
   After=network.target

   [Service]
   User=ehr-system
   Group=nginx
   WorkingDirectory=/var/www/ehr-system/server
   ExecStart=/var/www/ehr-system/server/venv/bin/celery -A ehr_system worker -l info

   [Install]
   WantedBy=multi-user.target
   ```

6. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/ehr-system
   ```
   
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location /static/ {
           alias /var/www/ehr-system/server/staticfiles/;
       }

       location /media/ {
           alias /var/www/ehr-system/server/media/;
       }

       location / {
           proxy_set_header Host $http_host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_pass http://unix:/var/www/ehr-system/server/ehr_system.sock;
       }
   }
   ```

7. **Enable and start services**
   ```bash
   sudo systemctl enable ehr-system ehr-system-celery
   sudo systemctl start ehr-system ehr-system-celery
   sudo systemctl enable nginx
   sudo systemctl start nginx
   sudo ln -s /etc/nginx/sites-available/ehr-system /etc/nginx/sites-enabled/
   sudo systemctl reload nginx
   ```

## Usage Guide

### For Hospital Management

1. **Register** using phone number and OTP verification
2. **Create hospital profile** with license details
3. **Onboard new patients** with MRN generation
4. **Search patients** using phone numbers or MRN
5. **Manage patient files** and emergency contacts

### For Doctors

1. **Register** as doctor and create medical profile
2. **Enter patient MRN** to access patient records
3. **Create medical visits** with detailed information
4. **Record audio** during consultations
5. **Generate AI summaries** from visit transcripts
6. **Add medical notes** and prescriptions
7. **View patient medical history** and AI-generated summaries

### For Patients

1. **Login** using phone number and OTP
2. **View medical history** and visit records
3. **Upload medical reports** and test results
4. **Access AI-generated summaries** of medical visits
5. **View prescriptions** and treatment plans

## API Documentation

- **Swagger UI**: Available at `/swagger/` when running the server
- **ReDoc**: Available at `/redoc/` for alternative documentation view
- **OpenAPI JSON**: Available at `/swagger.json` for API clients

## Security Features

- Phone number-based authentication with OTP verification
- Token-based API authentication
- Role-based access control (Hospital Staff, Doctor, Patient)
- Data encryption in transit and at rest
- Secure file upload with validation
- CORS protection and rate limiting

## Performance Optimization

- Database indexing on frequently queried fields
- Pagination for large result sets
- Async AI processing with Celery
- Redis caching for session management
- Optimized database queries with select_related and prefetch_related

## Monitoring and Maintenance

### Health Checks

- **API Health**: `GET /api/v1/health/`
- **Database**: Check connection and migrations
- **Redis**: Verify queue processing
- **AI Services**: Monitor API quotas and response times

### Logging

- Application logs in `/var/log/ehr-system/`
- Error tracking and monitoring
- AI processing statistics and costs

### Backup Strategy

1. **Database Backups**: Daily PostgreSQL dumps
2. **File Backups**: AWS S3 automatic backups
3. **Configuration Backups**: Environment and settings files

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check PostgreSQL service status
   - Verify database credentials in .env
   - Ensure database exists and user has permissions

2. **AI Service Failures**
   - Verify API keys for OpenAI and AssemblyAI
   - Check API quotas and billing status
   - Monitor Celery worker status

3. **File Upload Issues**
   - Check AWS S3 permissions and bucket configuration
   - Verify MEDIA_ROOT and MEDIA_URL settings
   - Check file size limits and formats

### Performance Issues

1. **Slow API Responses**
   - Enable database query logging
   - Check for N+1 query problems
   - Monitor database connection pool

2. **High Memory Usage**
   - Monitor Celery worker memory consumption
   - Check for memory leaks in AI processing
   - Optimize large file handling

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## License

This project is proprietary software developed for small clinics in Pakistan. All rights reserved.

## Support

For technical support and documentation:
- Email: support@ehr-system.local
- Documentation: `/swagger/` endpoint
- Issues: Create issue in repository

## Changelog

### Version 1.0.0
- Initial release with core EHR functionality
- Multi-portal system (Hospital, Doctor, Patient)
- AI-powered transcription and summarization
- Phone-based authentication system
- Comprehensive API with Swagger documentation
