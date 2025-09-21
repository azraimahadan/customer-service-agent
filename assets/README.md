# Assets Directory

This directory contains the static build files for the SUARA Customer Service Agent web interface.

## Structure

```
assets/
└── web/                    # Static web files
    ├── index.html         # Main application entry point
    ├── 404.html           # 404 error page
    ├── 404/               # 404 directory
    └── _next/             # Next.js static assets
        ├── static/        # Static assets (CSS, JS, etc.)
        │   ├── chunks/    # JavaScript chunks
        │   └── css/       # Compiled CSS files
        └── LprY7n9KvblgXpbnsuAQW/  # Build-specific assets
```

## Usage

### Serving the Static Files

These files can be served by any web server. The main entry point is `index.html`.

**Examples:**

1. **Using Python HTTP Server:**
   ```bash
   cd assets/web
   python -m http.server 8000
   ```

2. **Using Node.js serve package:**
   ```bash
   npx serve assets/web
   ```

3. **Using Nginx:**
   ```nginx
   server {
       listen 80;
       root /path/to/customer-service-agent/assets/web;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
   }
   ```

## Features

The static build includes:
- ✅ **Optimized React components** - All TypeScript compiled to JavaScript
- ✅ **Tailwind CSS** - Custom blue (#180092) and orange (#FF5E00) theme
- ✅ **Responsive design** - Mobile-friendly chat interface
- ✅ **Modern UI components** - Chat bubbles, input forms, file upload
- ✅ **Icons** - Lucide React icons included
- ✅ **Production optimized** - Minified and optimized for performance

## API Configuration

The static files are configured to connect to the backend API. You may need to update the API URL by setting the `NEXT_PUBLIC_API_URL` environment variable before building, or by modifying the API client directly.

Default API URL: `http://localhost:8000`

## Build Information

- **Built with:** Next.js 14.0.0
- **Build date:** ${new Date().toISOString()}
- **Build mode:** Static export
- **Optimization:** Production build with tree shaking and minification