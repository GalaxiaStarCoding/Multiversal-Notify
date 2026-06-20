# README for android-minimal

This is a minimal Android project (Java) illustrating FCM registration and
posting the device token to the Multiversal-Notify server (/devices/register).

Steps to build and run

1. Install Android SDK and Java. Use Android Studio or command-line Gradle.
2. Copy your Firebase google-services.json into examples/android-minimal/app/
   (the file must match the applicationId com.multiversalnotify.app or change
   applicationId in app/build.gradle and ensure google-services.json matches).
3. Edit RegistrationService.SERVER_REGISTER_URL to point to your running server
   (e.g., http://10.0.2.2:5000/devices/register when using Android emulator).
4. Open Android Studio and import the project directory (examples/android-minimal).
5. Build and run on device or emulator.

Notes
- This example uses the Firebase Messaging library and OkHttp. For production
  you should handle API keys securely and allow users to input/obtain their
  apikeys rather than hardcoding them.
- You must add google-services.json from your Firebase project for the app to
  successfully obtain an FCM registration token.
