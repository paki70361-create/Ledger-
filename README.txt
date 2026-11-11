MY PERSONAL LEDGER — ANDROID PROJECT

This is the Android-ready Kivy source project. It is not a compiled APK yet.

Features:
- Name, amount, Given/Received and transaction reason
- Automatic date and time
- Total given, total received and net balance
- Search by person or reason
- Delete transactions
- SQLite storage in the app's private Android data folder

BUILD AN APK (Ubuntu / Linux)
1. Install Python 3, Java JDK 17, Git, and required Buildozer packages.
2. Install Buildozer: pip install buildozer
3. Open a terminal in this project folder.
4. Run: buildozer android debug
5. The APK will be created in the bin/ folder.

For a first build, Buildozer downloads Android SDK/NDK components and may take some time.
The APK can then be copied to your Android phone and installed. You may need to allow
installation from your browser or file manager.

Project package: org.personaltools.mypersonalledger
Minimum Android version: Android 6.0 (API 23)
Target API: 35

Note: This source ZIP is not itself installable on Android. It must be compiled into an APK.
