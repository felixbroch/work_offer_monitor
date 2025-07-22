# Deployment Guide

## Quick Start

This application is designed to be deployed on Vercel with a simple setup process.

## Prerequisites

- Node.js 18+ and npm
- OpenAI API key
- Git repository (GitHub recommended)

## Deployment Steps

### 1. Vercel Deployment

1. **Connect Repository**
   - Fork or clone this repository to your GitHub account
   - Visit [vercel.com](https://vercel.com) and sign in with GitHub
   - Click "New Project" and import your repository

2. **Environment Variables**
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
3. **Deploy**
   - Vercel will automatically detect Next.js and deploy
   - The application will be available at your Vercel URL

### 2. Local Development

```bash
# Install dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt

# Start development servers
npm run dev
```

## Configuration

- Modify `data/companies_to_watch.csv` to add your target companies
- Adjust filtering criteria in `config/config.py`
- API settings are managed through the web interface

## Features

- **Web Interface**: Modern Next.js frontend with TypeScript
- **API Backend**: Flask API for job search and data management
- **Real-time Updates**: Live job monitoring and statistics
- **Data Persistence**: SQLite database for job history
- **Responsive Design**: Works on desktop and mobile devices

## Support

Check the repository documentation for detailed setup instructions and troubleshooting.
