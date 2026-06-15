# Clinic Service API - CURL Examples

## Prerequisites
- Application running at `http://127.0.0.1:8000`
- `.env` configured with a valid PostgreSQL connection and JWT secret

## Quick: get a bearer token and export it (requires `jq`)

```bash
# login and extract access token to $TOKEN
TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=Admin123!" | jq -r .access_token)

# use token in subsequent requests
echo "Token: $TOKEN"
```

## 1. Register a User
Register a new user (patient, doctor, or admin):

```bash
curl -s -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Alice Patient","email":"alice@example.com","password":"Patient123!","role":"patient"}'
```

```bash
curl -s -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Admin User","email":"admin@example.com","password":"Admin123!","role":"admin"}'
```

## 2. Create Clinic & Doctor (Admin)
Create a clinic (admin-only):

```bash
curl -s -X POST "http://127.0.0.1:8000/clinics/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"City Medical Center","address":"123 Main St","phone":"555-1234","specialty":"General Medicine","description":"Community clinic"}'
```

Create a doctor (admin-only):

```bash
curl -s -X POST "http://127.0.0.1:8000/doctors/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"full_name":"Dr. John Doe","email":"dr.john@example.com","password":"Doctor123!","specialty":"Cardiology","license_number":"LIC-2026-100"}'
```

## 3. Search & Discovery

List clinics or search:

```bash
curl -s "http://127.0.0.1:8000/clinics/"
curl -s "http://127.0.0.1:8000/clinics/search?name=City&specialty=General"
```

Search doctors by specialty:

```bash
curl -s "http://127.0.0.1:8000/doctors/search?specialty=Cardiology"
```

## 4. Appointment Workflow

Book an appointment (patient):

```bash
curl -s -X POST "http://127.0.0.1:8000/appointments/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"doctor_id":1,"patient_id":2,"appointment_date":"2026-06-05T14:00:00","reason":"Checkup"}'
```

Approve an appointment (doctor or admin):

```bash
curl -s -X POST "http://127.0.0.1:8000/appointments/1/approve" \
  -H "Authorization: Bearer $TOKEN"
```

Reschedule an appointment (patient):

```bash
curl -s -X POST "http://127.0.0.1:8000/appointments/1/reschedule" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"appointment_date":"2026-06-06T10:00:00"}'
```

Cancel an appointment (patient or admin):

```bash
curl -s -X POST "http://127.0.0.1:8000/appointments/1/cancel" \
  -H "Authorization: Bearer $TOKEN"
```

Get my appointments (patient):

```bash
curl -s -X GET "http://127.0.0.1:8000/appointments/my" \
  -H "Authorization: Bearer $TOKEN"
```

Get doctor appointments (doctor):

```bash
curl -s -X GET "http://127.0.0.1:8000/appointments/doctor" \
  -H "Authorization: Bearer $TOKEN"
```

## 5. Medical Records & Prescriptions

Create a medical record (doctor):

```bash
curl -s -X POST "http://127.0.0.1:8000/medical-records/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"patient_id":2,"doctor_id":1,"diagnosis":"Hypertension","treatment":"Lifestyle modification","notes":"Follow-up in 2 weeks."}'
```

Get patient records (patient):

```bash
curl -s -X GET "http://127.0.0.1:8000/medical-records/my" \
  -H "Authorization: Bearer $TOKEN"
```

Create a prescription (doctor):

```bash
curl -s -X POST "http://127.0.0.1:8000/prescriptions/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"patient_id":2,"doctor_id":1,"medication":"Amlodipine","dosage":"5mg","instructions":"Take once daily."}'
```

Get my prescriptions (patient):

```bash
curl -s -X GET "http://127.0.0.1:8000/prescriptions/my" \
  -H "Authorization: Bearer $TOKEN"
```

## 6. Admin & Dashboard

View clinic dashboard summary (admin):

```bash
curl -s -X GET "http://127.0.0.1:8000/dashboard/clinic-summary" \
  -H "Authorization: Bearer $TOKEN"
```

## Notes
- Replace `$TOKEN` with the token you obtained from the login example if not using the extraction snippet.
- Replace resource IDs like `1` with actual IDs returned by the API.
- Ensure the app is running before executing these commands.
