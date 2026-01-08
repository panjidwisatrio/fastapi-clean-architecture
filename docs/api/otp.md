# OTP API

One-Time Password verification system.

## Request OTP
```http
POST /otp/request
```

Sends 6-digit OTP code to email.

## Verify OTP
```http
POST /otp/verify
```

Validates OTP code (10-minute expiry).

## Features

- Email delivery
- Time-limited codes
- Rate limiting
- Secure validation
