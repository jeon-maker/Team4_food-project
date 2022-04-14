package com.example.logintest2;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity {
    Button btnLogout;
    DatabaseHelper databaseHelper;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.homepage);

        databaseHelper = new DatabaseHelper(this);
        btnLogout = findViewById(R.id.btnLogout);

        //cek session
        Boolean checkSession = databaseHelper.checkSession("ada");
        if (checkSession == false){
            Intent loginIntent = new Intent(MainActivity.this, FormLogin.class);
            startActivity(loginIntent);
            finish();
        }

        btnLogout.setOnClickListener(view -> {
            Boolean updateSession = databaseHelper.upgradeSession("kosong", 1);
            if (updateSession == true){
                Toast.makeText(getApplicationContext(), "Berhasil keluar", Toast.LENGTH_SHORT).show();
                Intent loginIntent = new Intent(MainActivity.this, FormLogin.class);
                startActivity(loginIntent);
                finish();
            }
        });

    }
}