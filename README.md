# My Money Manager (MMK + THB)

A simple Kivy Android app to track income and expenses separately in Myanmar Kyat (MMK) and Thai Baht (THB).

## Features
- Add income and expenses
- Separate MMK and THB balances
- View totals and recent transactions
- Saves data locally on the phone in the app's private storage
- Does not combine currencies or apply an exchange rate

## Build an APK using GitHub Actions
This project includes `.github/workflows/build-apk.yml`.

1. Create or sign in to a GitHub account.
2. Create a new repository and upload the contents of this folder.
3. Open the repository's **Actions** tab.
4. Select **Build Android APK**.
5. Press **Run workflow** and wait for the build to finish.
6. Open the completed workflow run, find **Artifacts**, and download `My-Money-Manager-APK`.
7. Extract the ZIP on your Android phone and install the APK. Android may ask you to allow installation from that source.

The APK is a debug build for testing, not a Play Store release.

## Important
- Transactions are stored locally in the app's private storage.
- Uninstalling the app or clearing its data may remove the saved records. Export/backup is not included in this first version.
- Test with small sample entries first and keep your own backup of important records.
