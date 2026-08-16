package com.huiyuan.util;

import android.app.Activity;
import android.content.Context;
import b.b.d.l;
import java.util.ArrayList;
import org.apache.cordova.CallbackContext;
import org.apache.cordova.CordovaPlugin;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/* JADX INFO: loaded from: classes.dex */
public class UtilPlugin extends CordovaPlugin {

    public class a implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ Activity f877b;
        public final /* synthetic */ String c;
        public final /* synthetic */ CallbackContext d;

        public a(UtilPlugin utilPlugin, Activity activity, String str, CallbackContext callbackContext) {
            this.f877b = activity;
            this.c = str;
            this.d = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                UtilHelper.openUrl(this.f877b, this.c);
                this.d.success("ok");
            } catch (Exception e) {
                this.d.error(e.getMessage());
            }
        }
    }

    public class b implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ Activity f878b;
        public final /* synthetic */ CallbackContext c;

        public b(UtilPlugin utilPlugin, Activity activity, CallbackContext callbackContext) {
            this.f878b = activity;
            this.c = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                JSONObject jSONObject = new JSONObject();
                jSONObject.put("is24HourFormat", UtilHelper.is24HourFormat(this.f878b.getApplicationContext()));
                this.c.success(jSONObject);
            } catch (Exception unused) {
            }
        }
    }

    public class c implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ Activity f879b;
        public final /* synthetic */ String c;
        public final /* synthetic */ String d;
        public final /* synthetic */ String e;
        public final /* synthetic */ String[] f;
        public final /* synthetic */ CallbackContext g;

        public c(UtilPlugin utilPlugin, Activity activity, String str, String str2, String str3, String[] strArr, CallbackContext callbackContext) {
            this.f879b = activity;
            this.c = str;
            this.d = str2;
            this.e = str3;
            this.f = strArr;
            this.g = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                UtilHelper.sendMail(this.f879b, this.c, this.d, this.e, this.f);
                this.g.success("ok");
            } catch (Exception e) {
                this.g.error(e.getMessage());
            }
        }
    }

    public class d implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ Activity f880b;
        public final /* synthetic */ String c;
        public final /* synthetic */ String d;
        public final /* synthetic */ CallbackContext e;

        public d(UtilPlugin utilPlugin, Activity activity, String str, String str2, CallbackContext callbackContext) {
            this.f880b = activity;
            this.c = str;
            this.d = str2;
            this.e = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                UtilHelper.shareUrl(this.f880b, this.c, this.d);
                this.e.success("ok");
            } catch (Exception e) {
                this.e.error(e.getMessage());
            }
        }
    }

    public class e implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ Activity f881b;
        public final /* synthetic */ CallbackContext c;

        public e(UtilPlugin utilPlugin, Activity activity, CallbackContext callbackContext) {
            this.f881b = activity;
            this.c = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                Context applicationContext = this.f881b.getApplicationContext();
                JSONObject jSONObject = new JSONObject();
                int deviceWidth = UtilHelper.getDeviceWidth(applicationContext);
                int deviceHeight = UtilHelper.getDeviceHeight(applicationContext);
                String appName = UtilHelper.getAppName(applicationContext);
                String appVersion = UtilHelper.getAppVersion(applicationContext);
                String sysLanguage = UtilHelper.getSysLanguage(applicationContext);
                String systemVersion = UtilHelper.getSystemVersion();
                String systemModel = UtilHelper.getSystemModel();
                String deviceBrand = UtilHelper.getDeviceBrand();
                jSONObject.put("deviceWidth", deviceWidth);
                jSONObject.put("deviceHeight", deviceHeight);
                jSONObject.put("appName", appName);
                jSONObject.put("versionName", appVersion);
                jSONObject.put("languageName", sysLanguage);
                jSONObject.put("systemVersion", systemVersion);
                jSONObject.put("systemModel", systemModel);
                jSONObject.put("deviceBrand", deviceBrand);
                this.c.success(jSONObject);
            } catch (Exception unused) {
            }
        }
    }

    public class f implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ Activity f882b;
        public final /* synthetic */ CallbackContext c;

        public f(UtilPlugin utilPlugin, Activity activity, CallbackContext callbackContext) {
            this.f882b = activity;
            this.c = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.c.success(UtilHelper.getSysLanguage(this.f882b.getBaseContext()));
        }
    }

    @Override // org.apache.cordova.CordovaPlugin
    public boolean execute(String str, JSONArray jSONArray, CallbackContext callbackContext) throws JSONException {
        if (str.equals("openUrl")) {
            String string = jSONArray.getString(0);
            Activity activity = this.cordova.getActivity();
            activity.runOnUiThread(new a(this, activity, string, callbackContext));
            return true;
        }
        if (str.equals("is24HourFormat")) {
            Activity activity2 = this.cordova.getActivity();
            activity2.runOnUiThread(new b(this, activity2, callbackContext));
            return true;
        }
        if (str.equals("sendMail")) {
            String string2 = jSONArray.getString(0);
            String string3 = jSONArray.getString(1);
            String string4 = jSONArray.getString(2);
            JSONArray jSONArray2 = jSONArray.getJSONArray(3);
            ArrayList arrayList = new ArrayList();
            if (jSONArray2 != null) {
                for (int i = 0; i < jSONArray2.length(); i++) {
                    String string5 = jSONArray2.getString(i);
                    if (!StringHelper.isEmpty(string5)) {
                        arrayList.add(string5);
                    }
                }
            }
            String[] strArr = new String[arrayList.size()];
            arrayList.toArray(strArr);
            Activity activity3 = this.cordova.getActivity();
            activity3.runOnUiThread(new c(this, activity3, string3, string4, string2, strArr, callbackContext));
            return true;
        }
        if (str.equals("shareUrl")) {
            String string6 = jSONArray.getString(0);
            String string7 = jSONArray.getString(1);
            Activity activity4 = this.cordova.getActivity();
            activity4.runOnUiThread(new d(this, activity4, string6, string7, callbackContext));
            return true;
        }
        if (str.equals("getSystemInfo")) {
            Activity activity5 = this.cordova.getActivity();
            activity5.runOnUiThread(new e(this, activity5, callbackContext));
            return true;
        }
        if (str.equals("getSysLanguage")) {
            Activity activity6 = this.cordova.getActivity();
            activity6.runOnUiThread(new f(this, activity6, callbackContext));
            return true;
        }
        if (!str.equals("setSysLanguage")) {
            if (!str.equals("addLanguage")) {
                return false;
            }
            String strA = l.a(jSONArray.getString(0), jSONArray.getJSONObject(1));
            if (StringHelper.isEmpty(strA)) {
                callbackContext.error(strA);
            } else {
                callbackContext.success("ok");
            }
            return true;
        }
        String string8 = jSONArray.getString(0);
        JSONObject jSONObject = jSONArray.getJSONObject(1);
        jSONArray.getBoolean(2);
        String strA2 = l.a(string8, jSONObject, true);
        if (StringHelper.isEmpty(strA2)) {
            callbackContext.error(strA2);
        } else {
            callbackContext.success("ok");
        }
        return true;
    }
}
