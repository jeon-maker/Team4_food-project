package com.example.logintest2;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

public class FormRegister extends AppCompatActivity {
   DatabaseHelper databaseHelper;
   Button btnDaftar, btnLogin;
   EditText username, password, passwordConfirm;

   @Override
   protected void onCreate(@Nullable Bundle savedInstanceState) {
      super.onCreate(savedInstanceState);
      setContentView(R.layout.form_register);

      databaseHelper = new DatabaseHelper(this);
      ambilId();

      //login
      btnLogin.setOnClickListener(view -> {
         Intent loginIntent = new Intent(FormRegister.this, FormLogin.class);
         startActivity(loginIntent);
         finish();
      });

      //daftar
      btnDaftar.setOnClickListener(view -> {
         String strUsername = username.getText().toString();
         String strPassword = password.getText().toString();
         String strPasswordConfirm = passwordConfirm.getText().toString();

         if (strUsername.equals("") || strPassword.equals("")) {
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
         }
         else {
            if (strPassword.equals(strPasswordConfirm)) {
               Boolean daftar = databaseHelper.insertUser(strUsername, strPassword);
               if (daftar == true) {
                  Toast.makeText(getApplicationContext(), "Daftar Berhasil", Toast.LENGTH_SHORT).show();
                  Intent loginIntent = new Intent(FormRegister.this, FormLogin.class);
                  startActivity(loginIntent);
                  finish();
               } else {
                  Toast.makeText(getApplicationContext(), "Daftar gagal", Toast.LENGTH_SHORT).show();
               }
            } else {
               Toast.makeText(
                       getApplicationContext(),
                       "Password tidak cocok",
                       Toast.LENGTH_SHORT).show();
            }
         }
      });
   }

   void ambilId() {
      btnLogin = findViewById(R.id.btnLoginn);
      btnDaftar = findViewById(R.id.btnDaftar);
      username = findViewById(R.id.EditTxtUsername1);
      password = findViewById(R.id.EditTxtPass);
      passwordConfirm = findViewById(R.id.EditTxtPassConfirm);
   }
}