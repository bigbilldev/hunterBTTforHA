package com.huiyuan.util;

import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import b.b.d.p;
import com.gun0912.tedpermission.TedPermissionActivity;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.UUID;

/* JADX INFO: loaded from: classes.dex */
public class PermissionActivity extends AppCompatActivity {
    public static HashMap<String, p> g = new HashMap<>();

    /* JADX INFO: renamed from: b, reason: collision with root package name */
    public String[] f871b;
    public String c;
    public int d;
    public p e;
    public String f;

    public static void a(Context context, Intent intent, p pVar) {
        String string = UUID.randomUUID().toString();
        intent.putExtra("id", string);
        synchronized (g) {
            g.put(string, pVar);
        }
        context.startActivity(intent);
    }

    @Override // androidx.appcompat.app.AppCompatActivity, androidx.fragment.app.FragmentActivity, androidx.activity.ComponentActivity, androidx.core.app.ComponentActivity, android.app.Activity
    public void onCreate(Bundle bundle) {
        overridePendingTransition(0, 0);
        super.onCreate(bundle);
        this.f = getIntent().getStringExtra("id");
        if (this.f != null) {
            this.e = null;
            synchronized (g) {
                if (g.containsKey(this.f)) {
                    this.e = g.remove(this.f);
                }
            }
        }
        this.d = getIntent().getIntExtra("requestCode", 256);
        this.c = getIntent().getStringExtra("func");
        this.f871b = getIntent().getStringArrayExtra(TedPermissionActivity.EXTRA_PERMISSIONS);
        if (Build.VERSION.SDK_INT >= 23) {
            requestPermissions(this.f871b, this.d);
        }
    }

    @Override // androidx.fragment.app.FragmentActivity, android.app.Activity, a.f.a.a.b
    public void onRequestPermissionsResult(int i, String[] strArr, int[] iArr) {
        String[] strArr2;
        super.onRequestPermissionsResult(i, strArr, iArr);
        finish();
        if (this.c == null || (strArr2 = this.f871b) == null || strArr2.length <= 0) {
            return;
        }
        ArrayList<String> arrayList = new ArrayList<>();
        for (int i2 = 0; i2 < iArr.length; i2++) {
            if (iArr[i2] == -1) {
                arrayList.add(strArr[i2]);
            }
        }
        if (arrayList.isEmpty()) {
            this.e.onPermissionGranted(this.c);
        } else {
            this.e.onPermissionDenied(this.c, arrayList);
        }
    }
}
