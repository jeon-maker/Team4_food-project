package com.example.logintest2;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

public class FormLogin extends AppCompatActivity {
   DatabaseHelper databaseHelper;
   Button btnLogin, btnRegister;
   EditText username, password;

   @Override
   protected void onCreate(@Nullable Bundle savedInstanceState){
      super.onCreate(savedInstanceState);
      setContentView(R.layout.form_login);

      databaseHelper = new DatabaseHelper(this);
      ambilId();
      //register
      btnRegister.setOnClickListener(view -> {
         Intent registerIntent = new Intent(FormLogin.this, FormRegister.class);
         startActivity(registerIntent);
         finish();
      });

      //login
      btnLogin.setOnClickListener(view -> {
         String strUsername = username.getText().toString();
         String strPassword = password.getText().toString();

         if (strUsername.equals("") || strPassword.equals("")){
            if (strUsername.equals("")){
               Toast.makeText(
                       getApplicationContext(),
                       "Username tidak boleh kosong",
                       Toast.LENGTH_SHORT).show();
            } else {
               Toast.makeText(
                       getApplicationContext(),
                       "Password tidak boleh kosong",
                       Toast.LENGTH_SHORT).show();
            }
         } else {
            Boolean masuk = databaseHelper.checktLogin(strUsername, strPassword);
            if (masuk == true) {
               Boolean updateSession = databaseHelper.upgradeSession("ada", 1);
               if (updateSession == true) {
                  Toast.makeText(
                          getApplicationContext(),
                          "Berhasil masuk",
                          Toast.LENGTH_SHORT).show();

                  Intent mainIntent = new Intent(FormLogin.this, MainActivity.class);
                  startActivity(mainIntent);
                  finish();
               }
            } else {
               Toast.makeText(getApplicationContext(), "Gagal masuk", Toast.LENGTH_SHORT).show();
            }
         }
      });
   }

   void ambilId(){
      btnLogin = findViewById(R.id.btnLogin2);
      btnRegister = findViewById(R.id.btnRegister);
      username = findViewById(R.id.EditTxtUsername);
      password = findViewById(R.id.EditTxtPassword);
   }
}
