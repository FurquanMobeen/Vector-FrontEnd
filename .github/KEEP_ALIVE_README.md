# Keep-Alive Setup for Streamlit App

This directory contains a GitHub Action that automatically keeps your Streamlit Community Cloud app awake by visiting it periodically.

## 📋 How It Works

1. **GitHub Action** ([keep-alive.yml](workflows/keep-alive.yml)) runs on a schedule (every 6 hours by default)
2. **Python Script** ([keep_alive.py](keep_alive.py)) uses Playwright to:
   - Launch a headless Chrome browser
   - Navigate to your Streamlit app
   - Wait for the app to fully load
   - Maintain the connection for 10 seconds
   - Take a screenshot for verification

## 🚀 Setup Instructions

### Step 1: Add Your Streamlit App URL

You have two options:

#### Option A: Use GitHub Secrets (Recommended)

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `STREAMLIT_APP_URL`
5. Value: Your Streamlit app URL (e.g., `https://your-app-name.streamlit.app`)
6. Click **Add secret**

#### Option B: Update the Script Directly

Edit [keep_alive.py](keep_alive.py) and replace the placeholder URL:

```python
app_url = os.getenv(
    "STREAMLIT_APP_URL",
    "https://your-actual-app.streamlit.app"  # Change this line
)
```

### Step 2: Enable GitHub Actions

1. Push these files to your repository
2. Go to the **Actions** tab in your GitHub repository
3. If prompted, enable GitHub Actions for your repository

### Step 3: Test the Workflow

1. Go to **Actions** tab
2. Select **Keep Streamlit App Alive** workflow
3. Click **Run workflow** → **Run workflow** button
4. Wait for the workflow to complete
5. Check the logs to verify it worked

### Step 4: Verify the Schedule

The workflow runs automatically every 6 hours. You can check the next scheduled run in the Actions tab.

## ⚙️ Configuration Options

### Adjust the Schedule

Edit [keep-alive.yml](workflows/keep-alive.yml) and modify the cron expression:

```yaml
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
```

**Common schedules:**
- Every 4 hours: `'0 */4 * * *'`
- Every 8 hours: `'0 */8 * * *'`
- Every 12 hours: `'0 */12 * * *'`
- Twice a day (6am & 6pm UTC): `'0 6,18 * * *'`

**Note:** Streamlit Community Cloud typically puts apps to sleep after ~7 days of inactivity, so running every 6-12 hours should be sufficient.

### Change Timeout

Edit [keep_alive.py](keep_alive.py) and modify the timeout parameter:

```python
success = keep_alive(app_url, timeout=90000)  # 90 seconds
```

## 📸 Screenshots

Each run saves a screenshot of your app as an artifact:

1. Go to **Actions** tab
2. Click on a completed workflow run
3. Scroll down to **Artifacts**
4. Download `streamlit-screenshot-XXX`

This helps you verify the app loaded correctly.

## 🔍 Troubleshooting

### Workflow Fails with "Timeout error"

- Your app might be taking longer than 60 seconds to load
- Increase the `timeout` parameter in `keep_alive.py`

### Workflow Fails with "Playwright container not found"

- The script still considers this a success
- Your app might have loaded but uses a different structure

### "Using placeholder URL" Error

- You haven't set the `STREAMLIT_APP_URL` secret or updated the script
- Follow Step 1 above to configure the URL

### Action Doesn't Run on Schedule

- GitHub Actions can be delayed by up to 15 minutes during high load
- Make sure your repository is public (scheduled workflows don't run on private repos in free tier)
- Check if Actions are enabled in your repository settings

## 📊 Monitoring

To monitor your keep-alive workflow:

1. **Check Recent Runs:** Go to Actions → Keep Streamlit App Alive
2. **View Logs:** Click on any run to see detailed logs
3. **Check Screenshots:** Download artifacts to see what the app looked like
4. **Enable Notifications:** Go to your GitHub notification settings to get alerts on failures

## 💡 Tips

- The free tier of GitHub Actions provides 2,000 minutes per month, which is plenty for keep-alive tasks
- Each run typically takes 30-60 seconds
- Consider running less frequently (every 8-12 hours) to conserve Action minutes
- If your app still goes to sleep, it might be due to Streamlit's resource limits, not inactivity

## 🛑 Disabling Keep-Alive

To disable the keep-alive functionality:

1. Go to **.github/workflows/keep-alive.yml**
2. Delete the file, or
3. Add this at the top of the file:
   ```yaml
   # Disabled
   on: []
   ```

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Playwright Documentation](https://playwright.dev/python/)
- [Streamlit Community Cloud](https://streamlit.io/cloud)
- [Cron Expression Reference](https://crontab.guru/)
