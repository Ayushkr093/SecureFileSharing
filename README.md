# Secure File Sharing System

A secure file-sharing REST API built with Flask that supports two user types: **Ops Users** and **Client Users**.

## Features

### Ops Users
- Login authentication
- Upload files (`.pptx`, `.docx`, `.xlsx` only)
- Secure file storage with encrypted filenames

### Client Users
- User registration with email verification
- Secure login after email verification
- List all uploaded files
- Generate secure, encrypted download URLs
- Download files using encrypted tokens (single-use, time-limited)

## Security Features

- JWT-based authentication
- Password hashing with Werkzeug
- Encrypted download tokens with expiration
- File type validation
- Secure filename generation
- Single-use download tokens
- User-specific access control

## API Endpoints

### Authentication
- `POST /api/auth/ops/login` - Ops user login
- `POST /api/auth/client/signup` - Client user registration
- `POST /api/auth/client/verify-email` - Email verification
- `POST /api/auth/client/login` - Client user login

### Ops Operations
- `POST /api/ops/upload` - Upload files (JWT required)

### Client Operations
- `GET /api/client/files` - List all files (JWT required)
- `GET /api/client/download-file/{assignment_id}` - Get download link (JWT required)
- `GET /api/client/download-file/{encrypted_token}` - Download file

## Quick Start

### 1. Setup Environment
```bash
# Run setup script to generate secure keys
python setup.py

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Email (Optional)
Edit `.env` file to configure email settings for verification emails:
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 3. Run Application
```bash
python app.py
```

The application will run on `http://localhost:5000`

## Default Credentials

**Ops User:**
- Email: `ops@example.com`
- Password: `ops123`

## API Usage Examples

### 1. Ops User Login
```bash
curl -X POST http://localhost:5000/api/auth/ops/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ops@example.com", "password": "ops123"}'
```

### 2. Upload File (Ops)
```bash
curl -X POST http://localhost:5000/api/ops/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@document.docx"
```

### 3. Client Registration
```bash
curl -X POST http://localhost:5000/api/auth/client/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "client@example.com", "password": "password123"}'
```

### 4. Email Verification
```bash
curl -X POST http://localhost:5000/api/auth/client/verify-email \
  -H "Content-Type: application/json" \
  -d '{"token": "VERIFICATION_TOKEN"}'
```

### 5. Client Login
```bash
curl -X POST http://localhost:5000/api/auth/client/login \
  -H "Content-Type: application/json" \
  -d '{"email": "client@example.com", "password": "password123"}'
```

### 6. List Files (Client)
```bash
curl -X GET http://localhost:5000/api/client/files \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 7. Get Download Link (Client)
```bash
curl -X GET http://localhost:5000/api/client/download-file/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 8. Download File
```bash
curl -X GET "http://localhost:5000/api/client/download-file/ENCRYPTED_TOKEN" \
  --output downloaded_file.docx
```

## Project Structure

```
├── app.py              # Main application factory
├── config.py           # Configuration settings
├── models.py           # Database models
├── routes.py           # API routes and logic
├── utils.py            # Utility functions and services
├── setup.py            # Setup script
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (auto-generated)
├── uploads/           # File storage directory
└── README.md          # This file
```

## Database Schema

### Users Table
- `id` - Primary key
- `email` - Unique email address
- `password_hash` - Hashed password
- `user_type` - 'ops' or 'client'
- `is_verified` - Email verification status
- `verification_token` - Email verification token
- `created_at` - Account creation timestamp

### Uploaded Files Table
- `id` - Primary key
- `original_filename` - Original file name
- `stored_filename` - Secure stored filename
- `file_path` - File storage path
- `file_size` - File size in bytes
- `file_type` - File extension
- `uploaded_by` - Foreign key to users table
- `uploaded_at` - Upload timestamp

### Download Tokens Table
- `id` - Primary key
- `token` - Encrypted download token
- `file_id` - Foreign key to uploaded files
- `user_id` - Foreign key to users table
- `created_at` - Token creation time
- `expires_at` - Token expiration time
- `is_used` - Token usage status

## Security Considerations

1. **File Type Validation**: Only `.pptx`, `.docx`, `.xlsx` files are allowed
2. **Secure File Storage**: Files are stored with cryptographically secure random names
3. **Encrypted Download Tokens**: Download URLs contain encrypted tokens with user and file information
4. **Token Expiration**: Download tokens expire after 24 hours
5. **Single-Use Tokens**: Download tokens can only be used once
6. **User Access Control**: Users can only download files through their own generated tokens
7. **Password Hashing**: User passwords are hashed using Werkzeug's secure methods
8. **JWT Authentication**: API endpoints are protected with JWT tokens

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `JWT_SECRET_KEY` | JWT signing key | Auto-generated |
| `SQLALCHEMY_DATABASE_URI` | Database connection string | `sqlite:///file_sharing.db` |
| `MAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USE_TLS` | Use TLS for email | `True` |
| `MAIL_USERNAME` | Email username | Required for email |
| `MAIL_PASSWORD` | Email password | Required for email |
| `UPLOAD_FOLDER` | File upload directory | `uploads` |
| `MAX_CONTENT_LENGTH` | Max file size | `16777216` (16MB) |
| `ENCRYPTION_KEY` | File encryption key | Auto-generated |

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

## License

This project is for educational purposes. Please ensure compliance with your organization's security policies before deploying to production.
