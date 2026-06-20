package com.multiversalnotify.app;

import android.content.Context;
import android.util.Log;
import com.google.firebase.messaging.FirebaseMessaging;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.FormBody;
import okhttp3.Response;

import java.io.IOException;

public class RegistrationService {
    private static final String TAG = "MVNotifyReg";
    private static final OkHttpClient http = new OkHttpClient();

    // TODO: Replace with your server URL or pull from resources
    private static final String SERVER_REGISTER_URL = "http://your-server.example.com/devices/register";

    public static void registerTokenIfNeeded(Context ctx) {
        FirebaseMessaging.getInstance().getToken().addOnCompleteListener(task -> {
            if (!task.isSuccessful()) {
                Log.w(TAG, "Fetching FCM registration token failed", task.getException());
                return;
            }
            String token = task.getResult();
            Log.d(TAG, "FCM Token obtained: " + token);
            postTokenToServer(ctx, token);
        });
    }

    public static void postTokenToServer(Context ctx, String token) {
        // apikey could be stored in SharedPreferences or obtained via UI
        String apikey = "my-team-apikey";

        FormBody form = new FormBody.Builder()
                .add("apikey", apikey)
                .add("device_token", token)
                .build();

        Request req = new Request.Builder()
                .url(SERVER_REGISTER_URL)
                .post(form)
                .build();

        new Thread(() -> {
            try (Response resp = http.newCall(req).execute()) {
                if (resp.isSuccessful()) {
                    Log.d(TAG, "Token registered: " + resp.code());
                } else {
                    Log.w(TAG, "Failed to register token: " + resp.code() + " " + resp.message());
                }
            } catch (IOException e) {
                Log.e(TAG, "Registration error", e);
            }
        }).start();
    }
}
