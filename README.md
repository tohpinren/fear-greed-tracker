# Fear and Greed Index Tracker

Automated tracker for monitoring CNN Fear and Greed Index and Crypto Fear and Greed Index. Sends email notifications when either index reaches **extreme fear** levels (value ≤ 25).

## Features

- **Dual Index Tracking**: Monitors both CNN Fear and Greed Index and Crypto Fear and Greed Index
- **Email Notifications**: Sends separate alerts when each index reaches **extreme fear** (value ≤ 25). No notifications for extreme greed.
- **Historical Data**: Stores index values and ratings in JSON format
- **Cooldown Protection**: Prevents notification spam with 24-hour cooldown between alerts
- **Free Infrastructure**: Runs entirely on GitHub Actions (free tier)
- **Automated Scheduling**: Checks indices every 6 hours automatically

## Architecture

The tracker uses GitHub Actions as a free compute platform:
- Scheduled workflow runs every 6 hours
- Python script fetches data from both APIs
- Checks thresholds and sends email notifications via SMTP
- Commits historical data back to the repository

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd fear-greed-tracker
```

### 2. Set Up Email Configuration

You'll need SMTP credentials to send email notifications. Here are free options:

#### Option 1: Gmail (Recommended)

1. Enable 2-Factor Authentication on your Gmail account
2. Go to [Google Account Settings](https://myaccount.google.com/apppasswords)
3. Generate an App Password for "Mail"
4. Use these settings:
   - SMTP Server: `smtp.gmail.com`
   - SMTP Port: `587`
   - Username: Your Gmail address
   - Password: The generated App Password

#### Option 2: SendGrid

1. Sign up at [SendGrid](https://sendgrid.com/)
2. Create an API key
3. Use these settings:
   - SMTP Server: `smtp.sendgrid.net`
   - SMTP Port: `587`
   - Username: `apikey`
   - Password: Your API key

### 3. Configure GitHub Secrets

Go to your repository on GitHub → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:

- `SMTP_SERVER`: Your SMTP server address (e.g., `smtp.gmail.com`)
- `SMTP_PORT`: SMTP port (e.g., `587`)
- `SMTP_USERNAME`: Email address to send from
- `SMTP_PASSWORD`: SMTP password or app password
- `NOTIFICATION_EMAIL`: Your email address to receive notifications
- `THRESHOLD`: (Optional) Threshold value for extreme greed (default: `75`)

### 4. Test Locally (Optional)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your SMTP credentials

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run in dry-run mode (no emails sent):
   ```bash
   python tracker.py --dry-run
   ```

5. Test with real email (remove `--dry-run`):
   ```bash
   python tracker.py
   ```

### 5. Enable GitHub Actions

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit: Fear and Greed tracker"
   git push
   ```

2. Go to Actions tab in your GitHub repository

3. The workflow will run automatically every 6 hours

4. You can also trigger it manually using "Run workflow" button

## Configuration

### Threshold

The default threshold for extreme fear is **25** (notify when value ≤ 25). You can change this by:
- Setting `THRESHOLD` GitHub Secret (for GitHub Actions)
- Setting `THRESHOLD` environment variable (for local runs)
- Modifying the default in `tracker.py`

### Check Frequency

The tracker runs every 6 hours by default. To change this, edit `.github/workflows/fear-greed-tracker.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
```

Cron format examples:
- `'0 */6 * * *'` - Every 6 hours
- `'0 */4 * * *'` - Every 4 hours
- `'0 * * * *'` - Every hour
- `'0 9 * * *'` - Once daily at 9 AM UTC

### Notification Cooldown

Notifications have a 24-hour cooldown to prevent spam. If an index stays in extreme fear, you'll only receive one notification per day per index.

## File Structure

```
fear-greed-tracker/
├── .github/
│   └── workflows/
│       └── fear-greed-tracker.yml    # GitHub Actions workflow
├── data/
│   ├── cnn_fear_greed_history.json   # CNN index history
│   ├── crypto_fear_greed_history.json # Crypto index history
│   └── notifications_log.json        # Notification log
├── tracker.py                        # Main tracker script
├── email_notifier.py                 # Email notification module
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
```

## Data Storage

Historical data is stored in JSON format in the `data/` directory:

- **cnn_fear_greed_history.json**: CNN Fear and Greed Index history
- **crypto_fear_greed_history.json**: Crypto Fear and Greed Index history
- **notifications_log.json**: Log of all notifications sent

Each history file contains:
```json
{
  "last_updated": "2026-02-06T13:00:00Z",
  "history": [
    {
      "timestamp": "2026-02-06T13:00:00Z",
      "value": 32.94,
      "rating": "fear",
      "notified": false
    }
  ],
  "last_notification": "2026-02-05T10:00:00Z"
}
```

## Monitoring

### Check Workflow Status

1. Go to the **Actions** tab in your GitHub repository
2. View recent workflow runs
3. Click on a run to see detailed logs

### View Historical Data

Check the `data/` directory in your repository for historical index values and notification logs.

### Email Notifications

When an index reaches extreme fear (≤25), you'll receive an email with:
- Index name
- Current value
- Rating
- Timestamp

## Troubleshooting

### Emails Not Sending

1. Verify GitHub Secrets are set correctly
2. Check workflow logs in Actions tab for error messages
3. For Gmail: Ensure you're using an App Password, not your regular password
4. Test locally with `python tracker.py` to debug

### API Errors

- The tracker handles API failures gracefully
- Check workflow logs for specific error messages
- APIs may have rate limits; the tracker respects these

### Workflow Not Running

1. Ensure GitHub Actions is enabled in repository settings
2. Check that the workflow file is in `.github/workflows/`
3. Verify the cron schedule syntax is correct
4. Use "Run workflow" button to test manually

## GitHub Actions Free Tier

- **Private repos**: 2,000 minutes/month
- **Public repos**: Unlimited minutes
- **This tracker**: ~4 runs/day × 1-2 min = ~240 minutes/month
- Well within free tier limits

## License

This project is open source and available for personal use.

## Disclaimer

This tool is for informational purposes only. The Fear and Greed Index data does not constitute investment advice. Always conduct your own research and consult with financial advisors before making investment decisions.
