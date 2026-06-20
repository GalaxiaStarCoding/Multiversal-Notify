/*
examples/teamtalk_bot.cs

Example TeamTalk-side bot in C# that forwards events to a Prowl-compatible
Multiversal-Notify server (or any Prowl-like endpoint).

Usage:
- dotnet new console -n TeamTalkBot
- Replace Program.cs with this file or add it to the project.
- dotnet add package System.Net.Http (if needed; included in modern SDKs)
- Set environment variables M_NOTIFY_ENDPOINT and M_NOTIFY_APIKEY or edit the
  constants below.
- dotnet run

This is an example only — integrate the SendNotification calls into your
TeamTalk binding/event callbacks for production usage.
*/

using System;
using System.Net.Http;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Threading;
using System.Net;

class TeamTalkBot
{
    // Configuration
    private static readonly string NOTIFY_ENDPOINT = Environment.GetEnvironmentVariable("M_NOTIFY_ENDPOINT") ?? "https://your-server.example.com/publicapi/add";
    private static readonly string API_KEY = Environment.GetEnvironmentVariable("M_NOTIFY_APIKEY") ?? "PUT_YOUR_API_KEY_HERE";
    private const string DEFAULT_APPLICATION = "TeamTalk";
    private const int DEFAULT_PRIORITY = 0; // -2 .. 2

    private static readonly HttpClient http = new HttpClient();

    static async Task<bool> SendNotification(string apikey, string application, string evt, string description, int priority = DEFAULT_PRIORITY)
    {
        try
        {
            var values = new List<KeyValuePair<string, string>> {
                new KeyValuePair<string, string>("apikey", apikey),
                new KeyValuePair<string, string>("application", application),
                new KeyValuePair<string, string>("event", evt),
                new KeyValuePair<string, string>("description", description),
                new KeyValuePair<string, string>("priority", priority.ToString())
            };

            using (var content = new FormUrlEncodedContent(values))
            {
                var resp = await http.PostAsync(NOTIFY_ENDPOINT, content);
                resp.EnsureSuccessStatusCode();
                Console.WriteLine($"[notify] Sent: {evt} -> {(int)resp.StatusCode}");
                return true;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[notify] Failed: {ex.Message}");
            return false;
        }
    }

    // Example handlers
    public static Task HandleUserJoin(string nickname, string channel)
    {
        var evt = "User joined";
        var desc = $"{nickname} joined {channel}";
        return SendNotification(API_KEY, DEFAULT_APPLICATION, evt, desc);
    }

    public static Task HandleUserLeave(string nickname, string channel)
    {
        var evt = "User left";
        var desc = $"{nickname} left {channel}";
        return SendNotification(API_KEY, DEFAULT_APPLICATION, evt, desc);
    }

    public static Task HandleTextMessage(string sender, string message, string channel = null)
    {
        var evt = "Text message";
        var desc = channel != null ? $"{sender} in {channel}: {message}" : $"Private from {sender}: {message}";
        return SendNotification(API_KEY, DEFAULT_APPLICATION, evt, desc);
    }

    // Simulator: replace this with real TeamTalk SDK hooks
    public static void StartSimulator(CancellationToken token)
    {
        Task.Run(async () => {
            var users = new[] { "Alice", "Bob", "Carol" };
            var channels = new[] { "General", "Support" };
            int i = 0;
            while (!token.IsCancellationRequested)
            {
                var user = users[i % users.Length];
                var ch = channels[i % channels.Length];
                Console.WriteLine($"[sim] {user} joins {ch}");
                await HandleUserJoin(user, ch);
                await Task.Delay(2000, token);

                var msg = $"Hello from {user} ({i})";
                Console.WriteLine($"[sim] {user} says in {ch}: {msg}");
                await HandleTextMessage(user, msg, ch);
                await Task.Delay(3000, token);

                if (i % 3 == 2)
                {
                    Console.WriteLine($"[sim] {user} leaves {ch}");
                    await HandleUserLeave(user, ch);
                    await Task.Delay(1000, token);
                }
                i++;
            }
        }, token);
    }

    static async Task Main(string[] args)
    {
        Console.WriteLine("TeamTalk -> Multiversal-Notify C# example bot");
        Console.WriteLine("Edit NOTIFY_ENDPOINT and API_KEY or set env vars M_NOTIFY_ENDPOINT and M_NOTIFY_APIKEY.");

        using (var cts = new CancellationTokenSource())
        {
            StartSimulator(cts.Token);
            Console.WriteLine("Simulator running. Press Ctrl+C to exit.");
            try
            {
                await Task.Delay(-1, cts.Token);
            }
            catch (TaskCanceledException) { }
        }
    }
}
