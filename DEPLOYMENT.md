# Farmer Bot - Vercel Deployment Guide

## Prerequisites

Before deploying, ensure you have:
1. A [Vercel account](https://vercel.com/signup) (free)
2. A [GitHub](https://github.com), [GitLab](https://gitlab.com), or [Bitbucket](https://bitbucket.org) account
3. [OpenWeatherMap API Key](https://openweathermap.org/api) (free tier available)

---

## Step-by-Step Deployment Instructions

### Step 1: Prepare Your Repository

1. **Initialize Git Repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Farmer Bot ready for deployment"
   ```

2. **Create a New Repository** on GitHub/GitLab/Bitbucket

3. **Push Your Code**:
   ```bash
   git remote add origin <your-repository-url>
   git branch -M main
   git push -u origin main
   ```

### Step 2: Connect to Vercel

#### Option A: Deploy via Vercel Dashboard (Recommended)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Import your Git repository
4. Configure project:
   - **Framework Preset**: Select "Vite"
   - **Root Directory**: `./` (default)
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `dist` (default)

5. Click **"Deploy"**

#### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   cd "c:\Users\Admin\Desktop\fr bot"
   vercel
   ```

4. Follow the prompts:
   - Set up and deploy? **Yes**
   - Link to existing project? **No** (first time)
   - Project name: `farmer-bot` (or your preferred name)

### Step 3: Configure Environment Variables

1. In Vercel Dashboard, go to your project
2. Click **"Settings"** → **"Environment Variables"**
3. Add the following variable:
   - **Name**: `VITE_OPENWEATHER_API_KEY`
   - **Value**: Your OpenWeatherMap API key
   - **Environment**: Production (and Preview if needed)

4. Click **"Save"**

5. **Redeploy** the project for changes to take effect:
   - Go to **"Deployments"** tab
   - Click the three dots on the latest deployment
   - Select **"Redeploy"**

### Step 4: Verify Deployment

1. Visit your deployed URL (e.g., `https://farmer-bot.vercel.app`)
2. Test all features:
   - Dashboard loads correctly
   - Weather module displays data
   - Market prices show charts
   - Government schemes are listed
   - Disease detection uploads work

---

## Post-Deployment Configuration

### Custom Domain (Optional)

1. In Vercel Dashboard, go to **"Settings"** → **"Domains"**
2. Add your custom domain
3. Follow DNS configuration instructions

### Enable Analytics (Optional)

1. In Vercel Dashboard, go to **"Analytics"**
2. Enable Web Analytics for visitor insights

---

## Troubleshooting

### Build Failures

**Issue**: Build fails with "Cannot find module"
```bash
# Solution: Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue**: TypeScript errors during build
```bash
# Solution: Check TypeScript version compatibility
npm run build
# Fix any reported errors
```

### Runtime Issues

**Issue**: Weather data not loading
- Verify `VITE_OPENWEATHER_API_KEY` is set correctly
- Check API key is active on OpenWeatherMap
- Redeploy after fixing environment variables

**Issue**: 404 errors on page refresh
- The `vercel.json` rewrites configuration handles this
- Ensure `vercel.json` is committed to repository

### Performance Optimization

1. **Enable Compression**: Already enabled by Vercel by default
2. **Image Optimization**: Compress images before uploading for disease detection
3. **Lazy Loading**: Components are already code-split via React Router

---

## Updating Your Deployment

### Automatic Deployments
- Every push to `main` branch triggers automatic redeployment
- Preview deployments are created for pull requests

### Manual Updates
```bash
# Make changes to your code
git add .
git commit -m "Update description"
git push origin main
# Vercel automatically deploys the update
```

---

## Project Structure for Deployment

```
fr-bot/
├── dist/                 # Build output (generated)
├── node_modules/         # Dependencies (not committed)
├── public/              # Static assets
├── src/                 # Source code
│   ├── components/      # React components
│   ├── pages/          # Page components
│   ├── services/       # API services
│   ├── types/          # TypeScript types
│   ├── App.tsx         # Main app
│   └── main.tsx        # Entry point
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
├── index.html          # HTML template
├── package.json        # Dependencies & scripts
├── postcss.config.js   # PostCSS config
├── tailwind.config.js  # Tailwind config
├── tsconfig.json       # TypeScript config
├── vercel.json         # Vercel configuration
└── vite.config.ts      # Vite config
```

---

## Support & Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html#vercel)
- [OpenWeatherMap API Docs](https://openweathermap.org/api)
- [React Router Deployment](https://reactrouter.com/en/main/start/tutorial#deploying)

---

## Quick Reference Commands

```bash
# Local development
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Deploy to Vercel
vercel

# Deploy to production
vercel --prod
```

---

**Your Farmer Bot app is now ready for Vercel deployment!** 🚀
