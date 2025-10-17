# alx_travel_app_0x02

## Chapa Payment Integration

This project integrates the Chapa API for secure payment processing in Django. Users can make bookings and pay via Chapa, with payment status tracked and verified.

### Setup

1. Duplicate the project from `alx_travel_app_0x01`.
2. Store your Chapa API key in `.env` as `CHAPA_SECRET_KEY`.
3. Add the Payment model in `listings/models.py`.
4. Implement payment initiation and verification endpoints in `listings/views.py`.

### Payment Workflow

- When a booking is created, payment is initiated via Chapa.
- The user is redirected to Chapa's checkout page.
- After payment, the status is verified and updated in the Payment model.
- On successful payment, a confirmation email is sent (Celery recommended for production).
- Errors and failures are handled gracefully.

### API Endpoints

- `POST /initiate_payment/` — Initiates payment and returns Chapa checkout URL.
- `POST /verify_payment/` — Verifies payment status and updates the Payment model.

### Testing

- Use Chapa's sandbox environment for testing.
- Logs and screenshots should be collected to demonstrate successful payment initiation, verification, and status update.

### Evidence

- [ ] Payment initiation log/screenshot
- [ ] Payment verification log/screenshot
- [ ] Payment status update in Payment model

---

For more details, see `listings/views.py` and `listings/models.py`.
