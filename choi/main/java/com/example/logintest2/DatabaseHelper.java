package com.example.logintest2;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class DatabaseHelper extends SQLiteOpenHelper {
   public DatabaseHelper(Context context) {
      super(context, "LoginSQLite.db", null, 1);
   }

   @Override
   public void onCreate(SQLiteDatabase sqLiteDatabase) {
      sqLiteDatabase.execSQL("CREATE TABLE session(id integer PRIMARY KEY, login text)");
      sqLiteDatabase.execSQL("CREATE TABLE user(id integer PRIMARY KEY AUTOINCREMENT, username text, password text)");
      sqLiteDatabase.execSQL("INSERT INTO session(id, login) VALUES(1, 'kosong')");

   }

   @Override
   public void onUpgrade(SQLiteDatabase sqLiteDatabase, int i, int i1) {
      sqLiteDatabase.execSQL("DROP TABLE IF EXISTS session");
      sqLiteDatabase.execSQL("DROP TABLE IF EXISTS user");
      onCreate(sqLiteDatabase);
   }

   //mengecek session
   public Boolean checkSession(String sessionValues){
      SQLiteDatabase sqLiteDatabase = this.getReadableDatabase();
      Cursor cursor = sqLiteDatabase.rawQuery(
              "SELECT * FROM session WHERE login = ?", new String[]{sessionValues}
      );
      if (cursor.getCount() > 0){
         return true;
      }else{
         return false;
      }
   }

   //upgrade session
   public Boolean upgradeSession(String sessionValues, int id){
      SQLiteDatabase sqLiteDatabase = this.getWritableDatabase();
      ContentValues contentValues = new ContentValues();
      contentValues.put("login", sessionValues);

      long update = sqLiteDatabase.update(
              "session", contentValues, "id=" +id, null
      );
      if (update == -1){
         return false;
      }else {
         return true;
      }
   }

   //insert user
   public Boolean insertUser(String username, String password){
      SQLiteDatabase sqLiteDatabase = this.getWritableDatabase();
      ContentValues contentValues = new ContentValues();
      contentValues.put("username", username);
      contentValues.put("password", password);

      long insert = sqLiteDatabase.insert(
              "user", null, contentValues
      );
      if (insert == -1){
         return false;
      }else{
         return true;
      }
   }

   //cek login
   public Boolean checktLogin(String username, String password){
      SQLiteDatabase sqLiteDatabase = this.getReadableDatabase();
      Cursor cursor = sqLiteDatabase.rawQuery(
              "SELECT * FROM user WHERE username = ? AND password = ?",
              new String[]{username, password});
      if (cursor.getCount() > 0){
         return true;
      }else {
         return false;
      }
   }
}