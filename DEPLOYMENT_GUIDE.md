# StudyMeet - Vercel Deployment Guide

This guide will help you deploy your StudyMeet app to Vercel through GitHub integration.

## Prerequisites

- GitHub account
- Vercel account (free tier available)
- MongoDB Atlas account (free tier available)

## Step-by-Step Deployment

### 1. Database Setup (MongoDB Atlas)

First, set up your production database:

1. **Create MongoDB Atlas Account**
   - Go to [mongodb.com/atlas](https://mongodb.com/atlas)
   - Sign up for a free account
   - Create a new project (e.g., "StudyMeet")

2. **Create a Cluster**
   - Click "Create Cluster"
   - Choose "Free Shared" tier
   - Select your preferred region
   - Click "Create Cluster" (takes 2-3 minutes)

3. **Create Database User**
   - Go to "Database Access" in the left sidebar
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Username: `studymeet-user` (or your preference)
   - Generate a secure password and save it
   - Select "Read and write to any database"
   - Click "Add User"

4. **Configure Network Access**
   - Go to "Network Access" in the left sidebar
   - Click "Add IP Address"
   - Select "Allow Access from Anywhere" (0.0.0.0/0)
   - Click "Confirm"

5. **Get Connection String**
   - Go back to "Clusters"
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database user password
   - Save this connection string for later

### 2. GitHub Repository Setup

1. **Create GitHub Repository**
   - Go to [github.com](https://github.com)
   - Click "New repository"
   - Name: `studymeet` (or your preference)
   - Make it public or private
   - Don't initialize with README (we already have one)
   - Click "Create repository"

2. **Push Your Code**
   ```bash
   # In your project directory
   git init
   git add .
   git commit -m "Initial StudyMeet deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/studymeet.git
   git push -u origin main
   ```

### 3. Vercel Deployment

1. **Create Vercel Account**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with your GitHub account (recommended)

2. **Import Project**
   - Click "New Project" on Vercel dashboard
   - Import your GitHub repository
   - Vercel will automatically detect the configuration

3. **Configure Build Settings**
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave default)
   - **Build Command**: `npm run build` (will auto-detect)
   - **Output Directory**: `frontend/build`
   - **Install Command**: `npm run install-deps`

4. **Environment Variables**
   Click "Environment Variables" section and add:
   
   | Name | Value |
   |------|-------|
   | `MONGO_URL` | Your MongoDB Atlas connection string |
   | `DB_NAME` | `studymeet_db` |

   Example MONGO_URL:
   ```
   mongodb+srv://studymeet-user:YOUR_PASSWORD@cluster0.abc123.mongodb.net/studymeet_db
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete (2-3 minutes)
   - Your app will be available at `https://your-project-name.vercel.app`

### 4. Post-Deployment Configuration

1. **Update Frontend Environment**
   - In your GitHub repository, update `frontend/.env`:
   ```env
   REACT_APP_BACKEND_URL=https://your-project-name.vercel.app
   ```

2. **Commit and Push**
   ```bash
   git add frontend/.env
   git commit -m "Update production API URL"
   git push
   ```

3. **Automatic Redeployment**
   - Vercel will automatically redeploy when you push to main branch
   - Wait for redeployment to complete

### 5. Testing Your Deployment

1. **Visit Your App**
   - Go to `https://your-project-name.vercel.app`
   - You should see the StudyMeet homepage

2. **Test Core Features**
   - Sign in with a username
   - Create a study session
   - Join and leave sessions
   - Search and filter functionality

3. **Check API Endpoints**
   - Health check: `https://your-project-name.vercel.app/api/health`
   - Should return: `{"status": "healthy", "timestamp": "..."}`

## Troubleshooting

### Common Issues

**1. Build Failures**
- Check the build logs in Vercel dashboard
- Ensure all dependencies are in `requirements.txt` and `package.json`

**2. Database Connection Issues**
- Verify MongoDB Atlas connection string
- Check that IP addresses are whitelisted (0.0.0.0/0)
- Ensure database user has proper permissions

**3. API Endpoints Not Working**
- Check that `vercel.json` is configured correctly
- Verify environment variables are set in Vercel
- Check function logs in Vercel dashboard

**4. Frontend Not Loading**
- Ensure `REACT_APP_BACKEND_URL` points to your Vercel domain
- Check browser console for errors
- Verify build output directory is correct

### Logs and Debugging

1. **Function Logs**
   - Go to Vercel dashboard → Your project → Functions tab
   - View logs for each API endpoint

2. **Build Logs**
   - Go to Deployments tab
   - Click on any deployment to see build logs

3. **Real-time Logs**
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Login and view logs
   vercel login
   vercel logs --follow
   ```

## Custom Domain (Optional)

1. **Add Custom Domain**
   - Go to project settings in Vercel
   - Click "Domains"
   - Add your custom domain
   - Update DNS records as instructed

2. **SSL Certificate**
   - Vercel automatically provides SSL certificates
   - Your app will be available at `https://yourdomain.com`

## Environment Management

### Production vs Development

- **Production**: Uses Vercel environment variables
- **Development**: Uses local `.env` files

### Adding New Environment Variables

1. **Via Vercel Dashboard**
   - Project Settings → Environment Variables
   - Add new variable
   - Redeploy to apply changes

2. **Via Vercel CLI**
   ```bash
   vercel env add VARIABLE_NAME
   # Enter the value when prompted
   ```

## Scaling and Performance

1. **Function Limits**
   - Vercel free tier: 100GB-hours per month
   - Each function can run for max 10 seconds
   - Upgrade to Pro for higher limits

2. **Database Optimization**
   - Use MongoDB Atlas free tier (512MB storage)
   - Add indexes for better query performance
   - Monitor usage in Atlas dashboard

3. **Static Asset Optimization**
   - Vercel automatically optimizes static assets
   - Use Vercel Image Optimization for images

## Monitoring and Analytics

1. **Vercel Analytics**
   - Enable in project settings
   - View traffic and performance metrics

2. **Function Metrics**
   - Monitor function execution time
   - Track error rates and invocations

3. **MongoDB Atlas Monitoring**
   - Monitor cluster performance
   - Set up alerts for high usage

## Backup and Recovery

1. **Database Backups**
   - MongoDB Atlas automatically creates backups
   - Free tier: 2-day retention
   - Pro tier: Point-in-time recovery

2. **Code Backup**
   - GitHub serves as code backup
   - Consider forking for additional safety

## Support and Resources

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **MongoDB Atlas Docs**: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)
- **GitHub Issues**: Create issues in your repository for bugs
- **Community**: Vercel and MongoDB have active communities

---

**Your StudyMeet app is now live and ready for users! 🚀**

Share your app URL and start building your study community!