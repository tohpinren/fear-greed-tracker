# GitHub Secrets Setup Guide

This guide walks you through setting up GitHub Secrets for the Fear and Greed Index Tracker.

## Step-by-Step Instructions

### 1. Navigate to Repository Settings

1. Go to your GitHub repository
2. Click on the **Settings** tab (top navigation bar)
3. In the left sidebar, click **Secrets and variables** → **Actions**

### 2. Add Required Secrets

Click **New repository secret** for each secret below:

#### SMTP_SERVER
- **Name**: `SMTP_SERVER`
- **Value**: Your SMTP server address
  - Gmail: `smtp.gmail.com`
  - SendGrid: `smtp.sendgrid.net`
  - Mailgun: `smtp.mailgun.org`

#### SMTP_PORT
- **Name**: `SMTP_PORT`
- **Value**: SMTP port number
  - Most services: `587` (TLS)
  - Alternative: `465` (SSL)

#### SMTP_USERNAME
- **Name**: `SMTP_USERNAME`
- **Value**: Your email address or SMTP username
  - Gmail: Your Gmail address (e.g., `yourname@gmail.com`)
  - SendGrid: `apikey`
  - Mailgun: Your Mailgun SMTP username

#### SMTP_PASSWORD
- **Name**: `SMTP_PASSWORD`
- **Value**: Your SMTP password or app password
  - Gmail: App Password (see Gmail setup below)
  - SendGrid: Your SendGrid API key
  - Mailgun: Your Mailgun SMTP password

#### NOTIFICATION_EMAIL
- **Name**: `NOTIFICATION_EMAIL`
- **Value**: Email address to receive notifications
  - Can be the same as SMTP_USERNAME or different

#### THRESHOLD (Optional)
- **Name**: `THRESHOLD`
- **Value**: Threshold for extreme fear (default: `25`). Notify when value <= THRESHOLD.
  - Only add this if you want to change from the default

## Gmail-Specific Setup

If using Gmail, follow these additional steps:

### 1. Enable 2-Factor Authentication

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", enable **2-Step Verification**

### 2. Generate App Password

1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select **Mail** as the app
3. Select **Other (Custom name)** as the device
4. Enter "GitHub Actions" as the name
5. Click **Generate**
6. Copy the 16-character password (no spaces)
7. Use this as your `SMTP_PASSWORD` secret

### 3. Gmail Secret Values

- `SMTP_SERVER`: `smtp.gmail.com`
- `SMTP_PORT`: `587`
- `SMTP_USERNAME`: Your Gmail address (e.g., `yourname@gmail.com`)
- `SMTP_PASSWORD`: The 16-character app password from step 2
- `NOTIFICATION_EMAIL`: Your email address (can be same as SMTP_USERNAME)

## SendGrid Setup

### 1. Create SendGrid Account

1. Sign up at [SendGrid](https://sendgrid.com/)
2. Verify your email address

### 2. Create API Key

1. Go to Settings → API Keys
2. Click **Create API Key**
3. Name it "GitHub Actions Tracker"
4. Select **Full Access** or **Mail Send** permissions
5. Copy the API key (you won't see it again!)

### 3. SendGrid Secret Values

- `SMTP_SERVER`: `smtp.sendgrid.net`
- `SMTP_PORT`: `587`
- `SMTP_USERNAME`: `apikey`
- `SMTP_PASSWORD`: Your SendGrid API key
- `NOTIFICATION_EMAIL`: Your email address

## Mailgun Setup

### 1. Create Mailgun Account

1. Sign up at [Mailgun](https://www.mailgun.com/)
2. Verify your domain or use the sandbox domain for testing

### 2. Get SMTP Credentials

1. Go to Sending → Domain Settings
2. Click on your domain
3. Find **SMTP credentials** section
4. Copy the SMTP username and password

### 3. Mailgun Secret Values

- `SMTP_SERVER`: `smtp.mailgun.org`
- `SMTP_PORT`: `587`
- `SMTP_USERNAME`: Your Mailgun SMTP username
- `SMTP_PASSWORD`: Your Mailgun SMTP password
- `NOTIFICATION_EMAIL`: Your verified email address

## Verification

After adding all secrets:

1. Go to the **Actions** tab in your repository
2. Click **Run workflow** → **Run workflow** (manual trigger)
3. Check the workflow logs to verify:
   - Script runs successfully
   - APIs are fetched correctly
   - Email configuration is valid (if threshold is met, email will be sent)

## Troubleshooting

### "Missing required email configuration" Error

- Verify all required secrets are set (SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, NOTIFICATION_EMAIL)
- Check for typos in secret names (case-sensitive)
- Ensure secret values don't have extra spaces

### "Failed to send email notification" Error

- Verify SMTP credentials are correct
- For Gmail: Ensure you're using an App Password, not your regular password
- Check that 2FA is enabled for Gmail
- Verify SMTP server and port are correct
- Check workflow logs for detailed error messages

### Test Email Sending

To test email sending without waiting for extreme fear:

1. Temporarily set `THRESHOLD` secret to `100` (so any value triggers)
2. Run workflow manually
3. Check your email for notification
4. Set threshold back to `25`

## Security Notes

- **Never commit secrets to the repository**
- Secrets are encrypted and only accessible to GitHub Actions
- Use App Passwords instead of your main account password
- Rotate passwords periodically
- Review workflow logs regularly for any issues

## Next Steps

Once secrets are configured:

1. The workflow will run automatically every 6 hours
2. You can manually trigger it from the Actions tab
3. Check the `data/` directory for historical data
4. Monitor email notifications when thresholds are met
