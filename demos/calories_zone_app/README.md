# Calories Zone

Calories Zone is a local-first Android calorie calculator built with Kotlin and Jetpack Compose. It estimates BMR, maintenance calories, target calories for cutting or bulking, and a macro split. The app now also saves a profile on-device and logs meals locally so you can use it without a backend.

## What is included

- A Compose screen for profile setup, calorie targets, and local meal logging
- Mifflin-St Jeor calorie calculations
- Macro targets for protein, carbs, and fat
- Local profile persistence with Android shared preferences
- Local meal logging with daily totals and target tracking
- A local `RuleBasedAiGuidanceEngine` you can later replace with an on-device or remote model
- A unit test for the calorie calculator

## Build

1. Install Android SDK platform 35 if it is missing.
2. Run `./gradlew testDebugUnitTest`.
3. Run `./gradlew assembleDebug`.

The debug APK will be generated at `app/build/outputs/apk/debug/app-debug.apk`.

## Use it on your mobile

1. Build the APK with `./gradlew assembleDebug`.
2. Install it with `adb install -r app/build/outputs/apk/debug/app-debug.apk` or copy the APK to your phone and open it.
3. Open the app, generate a plan, tap `Save profile`, and start logging meals.

## Browser preview

If you want a quick local review in a browser before testing the Android build:

1. Run `cd preview && python3 -m http.server 4173`.
2. Open `http://127.0.0.1:4173/` in a browser.

This preview mirrors the app flow, but it is not the Android runtime.

## Simple local LLM path

If you want a simple on-device AI setup, keep the calorie math and storage exactly as they are and use a small model only for text interaction, such as turning `2 eggs and toast` into a meal draft.

- Good practical options on Android are Google AI Edge or MediaPipe LLM Inference, or `llama.cpp` for Android.
- Stay with a small quantized model in the `1B` to `3B` range if you want usable speed on phones.
- Do not let the model do the calorie math or persistence logic. Let it produce a draft meal, then feed that into your existing app logic.

## Play Store and payments

To ship on Google Play, you will need:

1. A signed release app bundle generated with `./gradlew bundleRelease`.
2. A Play Console app listing, screenshots, privacy policy, and Data safety form.
3. Clear disclosure if you add AI features or health-related recommendations.

### Build a signed upload bundle

1. Create an upload keystore locally:
	`keytool -genkeypair -v -storetype PKCS12 -keystore zomba-upload-key.jks -alias zomba-upload -keyalg RSA -keysize 2048 -validity 10000`
2. Export these environment variables in the same shell before building:
	`export ZOMBA_UPLOAD_STORE_FILE=/absolute/path/to/zomba-upload-key.jks`
	`export ZOMBA_UPLOAD_STORE_PASSWORD=your-store-password`
	`export ZOMBA_UPLOAD_KEY_ALIAS=zomba-upload`
	`export ZOMBA_UPLOAD_KEY_PASSWORD=your-key-password`
3. Build the signed bundle with `./gradlew bundleRelease`.
4. Upload `app/build/outputs/bundle/release/app-release.aab` in Play Console.

Without those signing credentials and an actual Play Console account, the bundle can be built but cannot be uploaded.

For payments:

- If you sell digital features inside the app, such as premium guidance or premium meal analysis, you must use Google Play Billing.
- A normal external payment gateway is not the correct path for digital in-app products on Android.
- If you sell physical goods or off-app services, different rules apply, but that is a separate product decision.

## Where to extend next

- Replace `RuleBasedAiGuidanceEngine` in `app/src/main/java/com/zomba/cal/domain/AiGuidanceEngine.kt` with an on-device meal-parser or chat adapter.
- Keep network and secret handling outside the UI layer if you later switch to a remote model.
- Add Google Play Billing only after you define the premium product and product IDs in Play Console.
