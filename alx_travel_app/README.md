# alx_travel_app_0x03

## Background Task Management with Celery and Email Notifications

This project implements background task management using Celery with RabbitMQ as the message broker. It includes automatic email notifications for bookings sent asynchronously to improve application performance.

## Features

- Asynchronous task processing with Celery
- RabbitMQ message broker integration
- Email notifications for booking confirmations
- Django REST Framework API endpoints
- Booking and Payment management
- Chapa payment integration (from previous version)

## Project Structure

```
alx_travel_app/
├── alx_travel_app/
│   ├── __init__.py          # Celery app initialization
│   ├── settings.py          # Django settings with Celery configuration
│   ├── celery.py            # Celery configuration
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── listings/
│   ├── __init__.py
│   ├── models.py            # Booking and Payment models
│   ├── views.py             # BookingViewSet and PaymentViewSet
│   ├── serializers.py       # DRF serializers
│   ├── tasks.py             # Celery tasks for email notifications
│   ├── urls.py              # Listings URL configuration
│   └── admin.py             # Admin configuration
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in git)
└── README.md                # This file
```

## Prerequisites

- Python 3.8+
- RabbitMQ server
- Virtual environment (recommended)

## Installation & Setup

### 1. Clone the Repository

```bash
cd alx_travel_app_0x03/alx_travel_app
```

### 2. Create and Activate Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Start RabbitMQ

#### Windows (using Chocolatey):
```bash
choco install rabbitmq
rabbitmq-service start
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
```

#### macOS (using Homebrew):
```bash
brew install rabbitmq
brew services start rabbitmq
```

Verify RabbitMQ is running:
```bash
# Check RabbitMQ status
sudo systemctl status rabbitmq-server  # Linux
rabbitmq-diagnostics status            # All platforms
```

### 5. Configure Environment Variables

Create or update the `.env` file in the `alx_travel_app` directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (using SQLite by default)
# Add your database configuration if using PostgreSQL/MySQL

# Celery Configuration
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=rpc://

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# For production, use SMTP:
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@alxtravelapp.com

# Chapa Payment (optional)
CHAPA_SECRET_KEY=your_chapa_secret_key_here
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Start the Application

You need to run three separate terminals:

#### Terminal 1: Django Development Server
```bash
python manage.py runserver
```

#### Terminal 2: Celery Worker
```bash
celery -A alx_travel_app worker --loglevel=info
```

#### Terminal 3 (Optional): Celery Flower (Monitoring)
```bash
pip install flower
celery -A alx_travel_app flower
```
Then visit http://localhost:5555 to monitor tasks.

## API Endpoints

### Bookings

- `GET /api/bookings/` - List all bookings
- `POST /api/bookings/` - Create a new booking (triggers email notification)
- `GET /api/bookings/{id}/` - Retrieve a specific booking
- `PUT /api/bookings/{id}/` - Update a booking
- `DELETE /api/bookings/{id}/` - Delete a booking

### Payments

- `GET /api/payments/` - List all payments
- `POST /api/payments/` - Create a payment
- `POST /api/payments/initiate/` - Initiate Chapa payment
- `POST /api/payments/verify/` - Verify Chapa payment

## Testing the Background Task

### 1. Create a Booking via API

Using curl:
```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "test@example.com",
    "property_name": "Luxury Beach Villa",
    "check_in_date": "2025-12-01",
    "check_out_date": "2025-12-05",
    "guests": 2,
    "total_price": "500.00"
  }'
```

Using Python requests:
```python
import requests

data = {
    "user_email": "test@example.com",
    "property_name": "Luxury Beach Villa",
    "check_in_date": "2025-12-01",
    "check_out_date": "2025-12-05",
    "guests": 2,
    "total_price": "500.00"
}

response = requests.post('http://localhost:8000/api/bookings/', json=data)
print(response.json())
```

### 2. Verify Email Task Execution

Check the Celery worker terminal for task execution logs:
```
[2025-11-02 12:34:56,789: INFO/MainProcess] Task listings.tasks.send_booking_confirmation_email[...] received
[2025-11-02 12:34:56,890: INFO/ForkPoolWorker-1] Task listings.tasks.send_booking_confirmation_email[...] succeeded
```

### 3. Check Email Output

If using `console.EmailBackend` (development), check the Django server terminal for email content.

If using SMTP, check the recipient's inbox.

## How It Works

1. **Booking Creation**: When a POST request is made to `/api/bookings/`, the `BookingViewSet.create()` method is called.

2. **Data Validation**: The serializer validates the booking data.

3. **Database Save**: The booking is saved to the database and a unique booking reference is generated.

4. **Async Task Trigger**: The `send_booking_confirmation_email.delay()` method is called, which:
   - Queues the email task in RabbitMQ
   - Returns immediately without blocking
   - Celery worker picks up the task from the queue

5. **Email Sending**: The Celery worker executes the task in the background, sending the confirmation email.

6. **Response**: The API returns a success response to the client immediately, without waiting for the email to be sent.

## Key Files Explained

### `alx_travel_app/celery.py`
Configures the Celery application, sets up autodiscovery of tasks, and defines the broker settings.

### `alx_travel_app/settings.py`
Contains Celery configuration:
- `CELERY_BROKER_URL`: RabbitMQ connection URL
- `CELERY_RESULT_BACKEND`: Where to store task results
- Email configuration for Django

### `listings/tasks.py`
Defines the `send_booking_confirmation_email` shared task that sends booking confirmation emails asynchronously with retry logic.

### `listings/views.py`
Contains the `BookingViewSet` which triggers the email task upon booking creation using `.delay()`.

## Troubleshooting

### RabbitMQ Connection Error
```
Error: [Errno 111] Connection refused
```
**Solution**: Ensure RabbitMQ is running:
```bash
sudo systemctl status rabbitmq-server
```

### Celery Worker Not Processing Tasks
```
[WARNING/MainProcess] consumer: Cannot connect to amqp://guest:**@localhost:5672//
```
**Solution**: Check RabbitMQ is running and CELERY_BROKER_URL is correct in .env

### Email Not Sending
**Solution**:
- Check Celery worker logs for errors
- Verify EMAIL_* settings in .env
- If using Gmail, ensure you're using an App Password, not your regular password

### Task Not Found Error
```
KeyError: 'listings.tasks.send_booking_confirmation_email'
```
**Solution**: Restart the Celery worker to pick up new tasks

## Production Considerations

1. **Use a Production Broker**: Consider using a managed RabbitMQ service or Redis
2. **Email Backend**: Switch to SMTP backend (Gmail, SendGrid, AWS SES, etc.)
3. **Task Monitoring**: Use Celery Flower or similar monitoring tools
4. **Error Handling**: Implement proper error handling and logging
5. **Retry Logic**: Configure retry policies for failed tasks
6. **Security**: Never commit .env files or API keys to version control

## Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Email Documentation](https://docs.djangoproject.com/en/stable/topics/email/)

## License

This project is for educational purposes as part of the ALX Professional Development Backend Engineering program.
