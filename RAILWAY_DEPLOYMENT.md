# Railway Deployment Guide

## Environment Variables to Set in Railway Dashboard

Go to your Railway project dashboard and set these environment variables:

### Required Variables:
```
FLASK_ENV=production
FLASK_DEBUG=False
BASE_URL=https://web-production-7c9d.up.railway.app
SECRET_KEY=your-very-secure-secret-key-change-this
JWT_SECRET_KEY=your-very-secure-jwt-secret-key-change-this
```

### Database (Already configured):
```
DATABASE_URL=postgresql://postgres:PImBtqmYKmJwxqawscWsRkSXdPYTgSbM@yamanote.proxy.rlwy.net:54315/railway
```

### File Upload Configuration:
```
UPLOAD_FOLDER=/app/uploads/profile_pictures
```

### CORS Configuration:
```
CORS_ORIGINS=https://nonsocialmedia.vercel.app,http://localhost:5173,http://localhost:3000
```

## Important Notes for Railway:

1. **Ephemeral File System**: Railway uses ephemeral storage, which means uploaded files will be deleted when your app restarts. For production, consider using:
   - AWS S3
   - Cloudinary
   - Railway Volumes (if available)

2. **Port Configuration**: Railway automatically provides the PORT environment variable, which is handled in the Procfile.

3. **Database**: Your PostgreSQL database is already configured and will persist data.

## Testing the Deployment:

1. **Health Check**:
   ```bash
   curl https://web-production-7c9d.up.railway.app/api/health
   ```

2. **Upload Test** (after setting environment variables):
   ```bash
   # Register a user first, then test upload
   curl -X POST https://web-production-7c9d.up.railway.app/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","email":"test@example.com","password":"testpass","displayName":"Test User"}'
   ```

## Troubleshooting:

1. **Files not uploading**: Check Railway logs for upload directory errors
2. **Images not displaying**: Verify BASE_URL is set correctly
3. **CORS errors**: Ensure your frontend domain is in CORS_ORIGINS

## Railway Logs:
Access logs through Railway dashboard to debug issues.

## Alternative: Cloud Storage Integration

For a production-ready solution, consider integrating cloud storage:

### Cloudinary Example:
```python
# Install: pip install cloudinary
import cloudinary
import cloudinary.uploader

# Configure in your app
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# Upload function
def upload_to_cloudinary(file_path):
    result = cloudinary.uploader.upload(file_path)
    return result['secure_url']
```

This would replace the local file storage and solve the ephemeral storage issue.
