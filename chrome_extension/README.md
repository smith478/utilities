# Installation instructions

In Chrome:
- Go to chrome://extensions
- Enable "Developer mode" (toggle in top-right)
- Click "Load unpacked" and select the `auto-populate` directory

# Publish to Chrome Web Store

To publish your Chrome extension to the Chrome Web Store, follow these steps:

1. Prepare Your Extension for Upload
Ensure your extension is packaged properly:

Your extension folder should include:

manifest.json

All HTML/JS/CSS/image files used

Zip the folder (right-click > "Compress" or use a terminal).

2. Create a Developer Account
Go to the Chrome Web Store Developer Dashboard:

Sign in with your Google account.

Pay a one-time $5 USD registration fee to create a developer account.

3. Upload Your Extension
Go to the Developer Dashboard.

Click "Add a new item".

Upload your zipped extension file.

Fill out required listing details:

Name

Description

Screenshots or promo images

Categories

Website (optional but recommended)

Privacy practices

4. Set Permissions and Privacy
Ensure the permissions in your manifest.json are accurate.

Provide a clear privacy policy if your extension handles user data.

5. Submit for Review
Click “Publish to Chrome Web Store” or “Submit for review.”

Google will review your extension (usually takes a few days).

You'll get an email if it’s approved or if changes are needed.

6. Manage Updates
To push updates, zip your updated code and upload it via the dashboard.

The extension will auto-update for users based on the manifest.json version number.