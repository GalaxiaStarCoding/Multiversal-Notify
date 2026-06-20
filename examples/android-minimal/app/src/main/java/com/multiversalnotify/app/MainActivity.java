package com.multiversalnotify.app;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        TextView tv = findViewById(R.id.textView);
        tv.setText("Multiversal-Notify Android example\nConfigure google-services.json and build.");

        // Kick off token registration (runs async)
        RegistrationService.registerTokenIfNeeded(this);
    }
}
