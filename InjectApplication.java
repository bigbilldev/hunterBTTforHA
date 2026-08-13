package com.huiyuan.ble;

import android.app.Application;
import android.os.StrictMode;
import b.b.a.j;

/* JADX INFO: loaded from: classes.dex */
public class InjectApplication extends Application {
    @Override // android.app.Application
    public void onCreate() {
        super.onCreate();
        j jVarB = j.b();
        getApplicationContext();
        jVarB.a();
        StrictMode.VmPolicy.Builder builder = new StrictMode.VmPolicy.Builder();
        StrictMode.setVmPolicy(builder.build());
        builder.detectFileUriExposure();
    }
}
