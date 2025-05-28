# Deployment Guide for Profile Picture Upload

## Key Changes Made

### 1. Fixed Duplicate Configuration
- Removed duplicate file upload configuration that was causing conflicts
- Centralized configuration in the config.py file

### 2. Server-Compatible File URLs
- Changed from relative paths (`/uploads/...`) to absolute URLs using `BASE_URL`
- Added `get_base_url()` function to dynamically determine the correct URL

### 3. Environment-Specific Configuration
- Added `UPLOAD_FOLDER` and `BASE_URL` environment variables
- Updated config.py to support different upload paths for dev/production

### 4. Improved Error Handling
- Added directory creation validation
- Added file existence checks
- Better error logging for debugging

### 5. Security Improvements
- Added `secure_filename()` for uploaded files
- Added CORS headers for image serving
- File path validation

## Environment Variables for Production

Set these environment variables on your server:

```bash
# Required for production
export FLASK_ENV=production
export BASE_URL=https://your-backend-domain.com
export UPLOAD_FOLDER=/app/uploads/profile_pictures
export DATABASE_URL=your-production-database-url
export JWT_SECRET_KEY=your-secure-jwt-secret

# Optional
export SECRET_KEY=your-secure-secret-key
export PORT=5000
```

## Server Deployment Steps

### For Railway/Heroku/Similar Platforms:

1. **Set Environment Variables in Dashboard:**
   - `FLASK_ENV=production`
   - `BASE_URL=https://your-app-name.railway.app` (or your domain)
   - `UPLOAD_FOLDER=/app/uploads/profile_pictures`
   - `JWT_SECRET_KEY=your-secure-secret`

2. **For Railway specifically:**
   - The Procfile is already configured: `web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120`

3. **For Docker deployments:**
   ```dockerfile
   # Add to your Dockerfile
   RUN mkdir -p /app/uploads/profile_pictures
   RUN chmod 755 /app/uploads/profile_pictures
   ```

### For VPS/Traditional Server:

1. **Set up the upload directory:**
   ```bash
   sudo mkdir -p /var/www/uploads/profile_pictures
   sudo chown www-data:www-data /var/www/uploads/profile_pictures
   sudo chmod 755 /var/www/uploads/profile_pictures
   ```

2. **Set environment variables:**
   ```bash
   export UPLOAD_FOLDER=/var/www/uploads/profile_pictures
   export BASE_URL=https://your-domain.com
   ```

3. **For production, consider using nginx to serve static files:**
   ```nginx
   location /uploads/ {
       alias /var/www/uploads/;
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

## Testing the Fix

1. **Test locally first:**
   ```bash
   cd backend
   python app.py
   ```

2. **Test upload endpoint:**
   ```bash
   curl -X POST -F "file=@test-image.jpg" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:5000/api/auth/profile-picture
   ```

3. **Check if image is accessible:**
   ```bash
   curl -I http://localhost:5000/uploads/profile_pictures/your-user-id.jpg
   ```

## Common Server Issues and Solutions

### Issue 1: Permission Denied
**Problem:** Upload directory not writable
**Solution:** 
```bash
chmod 755 /path/to/uploads
chown app-user:app-user /path/to/uploads
```

### Issue 2: Images Not Loading
**Problem:** Incorrect BASE_URL or CORS issues
**Solution:** 
- Check BASE_URL environment variable
- Verify CORS settings include your frontend domain

### Issue 3: File Not Found Errors
**Problem:** Upload directory path issues
**Solution:**
- Use absolute paths in production
- Check UPLOAD_FOLDER environment variable

### Issue 4: Large File Uploads Fail
**Problem:** Server timeout or size limits
**Solution:**
- Increase nginx client_max_body_size
- Adjust gunicorn timeout settings
- Check MAX_CONTENT_LENGTH setting

## Monitoring and Logs

To debug upload issues on server:

```bash
# Check application logs
tail -f /var/log/your-app/app.log

# Check nginx logs (if using nginx)
tail -f /var/log/nginx/error.log

# Check directory permissions
ls -la /path/to/uploads/profile_pictures/
```

## Alternative: Cloud Storage (Recommended for Production)

For better scalability, consider using cloud storage:

1. **AWS S3/CloudFront**
2. **Google Cloud Storage**
3. **Cloudinary** (image-specific)

This eliminates server storage issues and provides better performance.
