package com.choi.dietdiaryapp;

import android.content.SharedPreferences;
import android.support.v7.preference.PreferenceManager;

import com.choi.dietdiaryapp.helpers.DailyReminderServiceHelper;
import com.choi.dietdiaryapp.helpers.DriveBackupServiceHelper;
import com.choi.dietdiaryapp.preference.PreferenceKeys;
import com.choi.dietdiaryapp.utils.Base62;
import com.choi.dietdiaryapp.utils.TimeBasedRandomGenerator;
import com.crashlytics.android.Crashlytics;

import net.danlew.android.joda.JodaTimeAndroid;

import io.fabric.sdk.android.Fabric;

public class Application extends android.app.Application {
    public static final String APP_DIR = "DietDiaryApp";

    @Override
    public void onCreate() {
        super.onCreate();

        if (BuildConfig.CRASHLYTICS_ENABLED) {
            Fabric.with(this, new Crashlytics());
        }

        JodaTimeAndroid.init(this);

        SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(this);
        if (null == preferences.getString(PreferenceKeys.KEY_APP_ID, null)) {
            String id = Base62.encode(TimeBasedRandomGenerator.generate());

            SharedPreferences.Editor editor = preferences.edit();
            editor.putString(PreferenceKeys.KEY_APP_ID, id);
            editor.apply();
        }

        DailyReminderServiceHelper.setup(this, preferences);
        DriveBackupServiceHelper.setup(this);
    }
}
