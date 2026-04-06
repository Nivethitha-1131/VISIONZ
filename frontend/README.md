# VISIONZ Frontend

Static frontend application for VISIONZ defect detection system.

## Files

- `index.html` - Main application dashboard
- `landing.html` - Landing page
- `login.html` - Authentication page
- `profile.html` - User profile page
- `analytics.html` - Analytics dashboard
- `reports.html` - Reports page
- `js/` - JavaScript files
  - `api.js` - API communication layer
  - `navbar.js` - Navigation bar component
- `data/` - Static data files
  - `users.json` - User data

## Deployment

The frontend is served as static files from the `frontend/` directory.

When deployed to Vercel:
1. Static files are served with proper caching headers
2. SPA routing is configured to serve `index.html` for unknown routes
3. API requests are proxied to `/api/:path*` endpoints

## Development

To test locally, use a simple HTTP server:
```bash
# Python 3
python -m http.server 8080

# Or Node.js
npx http-server
```

Then visit `http://localhost:8080`
