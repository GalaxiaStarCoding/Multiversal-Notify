/*
examples/teamtalk_bot.java

Example TeamTalk-side bot (Java console) that forwards events to a Prowl-compatible
Multiversal-Notify server.

Usage:
 - javac examples/teamtalk_bot.java
 - java -cp examples TeamTalkBot
 - Or add to a Maven/Gradle project as a class and run.

Configuration:
 - Set env vars M_NOTIFY_ENDPOINT and M_NOTIFY_APIKEY, or edit the defaults below.

Notes:
 - This example uses HttpURLConnection (no external deps). For Android or production,
   prefer OkHttp (better timeouts/retries) and integrate into your SDK callbacks instead
   of the simulator.
*/

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class TeamTalkBot {
    private static final String DEFAULT_ENDPOINT = "https://your-server.example.com/publicapi/add";
    private static final String NOTIFY_ENDPOINT = System.getenv().getOrDefault("M_NOTIFY_ENDPOINT", DEFAULT_ENDPOINT);
    private static final String API_KEY = System.getenv().getOrDefault("M_NOTIFY_APIKEY", "PUT_YOUR_API_KEY_HERE");
    private static final String DEFAULT_APPLICATION = "TeamTalk";
    private static final int DEFAULT_PRIORITY = 0; // -2 .. 2

    public static boolean sendNotification(String apikey, String application, String event, String description, int priority) {
        try {
            StringBuilder form = new StringBuilder();
            form.append("apikey=").append(URLEncoder.encode(apikey, "UTF-8"));
            form.append("&application=").append(URLEncoder.encode(application, "UTF-8"));
            form.append("&event=").append(URLEncoder.encode(event, "UTF-8"));
            form.append("&description=").append(URLEncoder.encode(description, "UTF-8"));
            form.append("&priority=").append(URLEncoder.encode(String.valueOf(priority), "UTF-8"));
            byte[] postData = form.toString().getBytes(StandardCharsets.UTF_8);

            URL url = new URL(NOTIFY_ENDPOINT);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setConnectTimeout(5000);
            conn.setReadTimeout(5000);
            conn.setRequestMethod("POST");
            conn.setDoOutput(true);
            conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
            conn.setRequestProperty("Content-Length", Integer.toString(postData.length));

            try (OutputStream os = conn.getOutputStream()) {
                os.write(postData);
                os.flush();
            }

            int code = conn.getResponseCode();
            if (code >= 200 && code < 300) {
                System.out.println("[notify] Sent: " + event + " -> " + code);
                return true;
            } else {
                System.out.println("[notify] Server returned: " + code);
                return false;
            }
        } catch (Exception e) {
            System.out.println("[notify] Failed to send notification: " + e.getMessage());
            return false;
        }
    }

    // Handlers to be called from TeamTalk SDK callbacks
    public static void handleUserJoin(String nickname, String channel) {
        String event = "User joined";
        String description = nickname + " joined " + channel;
        sendNotification(API_KEY, DEFAULT_APPLICATION, event, description, DEFAULT_PRIORITY);
    }

    public static void handleUserLeave(String nickname, String channel) {
        String event = "User left";
        String description = nickname + " left " + channel;
        sendNotification(API_KEY, DEFAULT_APPLICATION, event, description, DEFAULT_PRIORITY);
    }

    public static void handleTextMessage(String sender, String message, String channel) {
        String event = "Text message";
        String description = (channel != null) ? (sender + " in " + channel + ": " + message) : ("Private from " + sender + ": " + message);
        sendNotification(API_KEY, DEFAULT_APPLICATION, event, description, DEFAULT_PRIORITY);
    }

    // Simulator: emits events on a schedule so you can test the notification path
    public static void startSimulator() {
        ScheduledExecutorService exec = Executors.newSingleThreadScheduledExecutor();
        String[] users = {"Alice", "Bob", "Carol"};
        String[] channels = {"General", "Support"};

        Runnable task = new Runnable() {
            int i = 0;
            @Override
            public void run() {
                try {
                    String user = users[i % users.length];
                    String ch = channels[i % channels.length];
                    System.out.println("[sim] " + user + " joins " + ch);
                    handleUserJoin(user, ch);

                    Thread.sleep(2000);

                    String msg = "Hello from " + user + " (" + i + ")";
                    System.out.println("[sim] " + user + " says in " + ch + ": " + msg);
                    handleTextMessage(user, msg, ch);

                    if (i % 3 == 2) {
                        Thread.sleep(1000);
                        System.out.println("[sim] " + user + " leaves " + ch);
                        handleUserLeave(user, ch);
                    }
                    i++;
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        };

        exec.scheduleAtFixedRate(task, 0, 7, TimeUnit.SECONDS);
    }

    public static void main(String[] args) {
        System.out.println("TeamTalk -> Multiversal-Notify Java example bot");
        System.out.println("Edit NOTIFY_ENDPOINT and API_KEY or set env vars M_NOTIFY_ENDPOINT and M_NOTIFY_APIKEY.");
        startSimulator();

        // Keep the app running
        try {
            Thread.currentThread().join();
        } catch (InterruptedException e) {
            System.out.println("Exiting...");
        }
    }
}
