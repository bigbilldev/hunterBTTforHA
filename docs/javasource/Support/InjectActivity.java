package com.huiyuan.ble;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import com.huiyuan.ble.ais.AisProtocol;
import com.huiyuan.ble.ais.AisWrapper;
import com.huiyuan.util.StringHelper;
import org.apache.cordova.CordovaActivity;
import org.json.JSONObject;

/* JADX INFO: loaded from: classes.dex */
public class InjectActivity extends CordovaActivity implements WrapperCallback, b.b.a.m.e {

    /* JADX INFO: renamed from: b, reason: collision with root package name */
    public AisWrapper f795b;

    public class a implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ JSONObject f796b;

        public a(JSONObject jSONObject) {
            this.f796b = jSONObject;
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                InjectActivity.this.a("onOADBinFileInfo(" + this.f796b.toString() + ");");
            } catch (Exception unused) {
            }
        }
    }

    public class b implements Runnable {
        public b() {
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                InjectActivity.this.a("onOADBinFileError();");
            } catch (Exception unused) {
            }
        }
    }

    public class c implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ String f798b;

        public c(String str) {
            this.f798b = str;
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                InjectActivity.this.a("onOADError(" + this.f798b.toString() + ");");
            } catch (Exception unused) {
            }
        }
    }

    public class d implements Runnable {
        public d() {
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                InjectActivity.this.a("onOADSuccess();");
            } catch (Exception unused) {
            }
        }
    }

    public class e implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CordovaActivity f800b;
        public final /* synthetic */ String c;

        public e(InjectActivity injectActivity, CordovaActivity cordovaActivity, String str) {
            this.f800b = cordovaActivity;
            this.c = str;
        }

        @Override // java.lang.Runnable
        public void run() {
            CordovaActivity cordovaActivity = this.f800b;
            StringBuilder sbA = b.a.a.a.a.a("javascript:(function(){try{");
            sbA.append(this.c);
            sbA.append("}catch(e){}})();");
            cordovaActivity.loadUrl(sbA.toString());
        }
    }

    public class f implements Runnable {
        public f() {
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                InjectActivity.this.a("onConnected()");
            } catch (Exception unused) {
            }
        }
    }

    public class g implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ int f802b;
        public final /* synthetic */ String c;

        public g(int i, String str) {
            this.f802b = i;
            this.c = str;
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                InjectActivity injectActivity = InjectActivity.this;
                StringBuilder sb = new StringBuilder();
                sb.append("onDeviceError(");
                sb.append(this.f802b);
                sb.append(",'");
                sb.append(StringHelper.isEmpty(this.c) ? "" : this.c.replaceAll("'", "\\\\'"));
                sb.append("')");
                injectActivity.a(sb.toString());
            } catch (Exception unused) {
            }
        }
    }

    public class h implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ String f803b;
        public final /* synthetic */ String c;

        public h(String str, String str2) {
            this.f803b = str;
            this.c = str2;
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                InjectActivity.this.a("onReceiveNotify('" + this.f803b + "'," + this.c + ")");
            } catch (Exception unused) {
            }
        }
    }

    public class i implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ String f804b;

        public i(String str) {
            this.f804b = str;
        }

        @Override // java.lang.Runnable
        public void run() {
            InjectActivity.b(InjectActivity.this, this.f804b);
        }
    }

    public class j implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ String f805b;

        public j(String str) {
            this.f805b = str;
        }

        @Override // java.lang.Runnable
        public void run() {
            InjectActivity.b(InjectActivity.this, this.f805b);
        }
    }

    public class k implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ boolean f806b;

        public k(boolean z) {
            this.f806b = z;
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                InjectActivity.this.a("onBleState(" + String.valueOf(this.f806b) + ")");
            } catch (Exception unused) {
            }
        }
    }

    public class l implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ float f807b;
        public final /* synthetic */ int c;
        public final /* synthetic */ int d;

        public l(float f, int i, int i2) {
            this.f807b = f;
            this.c = i;
            this.d = i2;
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                InjectActivity.this.a("onOADProgressUpdate(" + this.f807b + "," + this.c + "," + this.d + ");");
            } catch (Exception unused) {
            }
        }
    }

    public class m implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ String f808b;

        public m(String str) {
            this.f808b = str;
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                InjectActivity.this.a("onOADStatusUpdate('" + this.f808b.replaceAll("'", "\\\\'") + "');");
            } catch (Exception unused) {
            }
        }
    }

    public static /* synthetic */ void b(InjectActivity injectActivity, String str) {
    }

    @Override // b.b.a.m.e
    public void b(AisWrapper aisWrapper, String str) {
        runOnUiThread(new m(str));
    }

    @Override // com.huiyuan.ble.WrapperCallback
    public Activity getWrapperActivity() {
        return this;
    }

    @Override // org.apache.cordova.CordovaActivity, android.app.Activity
    public void onActivityResult(int i2, int i3, Intent intent) {
        super.onActivityResult(i2, i3, intent);
        this.f795b.onActivityResult(i2, i3, intent);
    }

    @Override // com.huiyuan.ble.WrapperCallback
    public void onBleState(boolean z) {
        runOnUiThread(new k(z));
    }

    @Override // com.huiyuan.ble.WrapperCallback
    public void onConnectFailed(String str, BleWrapper bleWrapper) {
    }

    @Override // com.huiyuan.ble.WrapperCallback
    public void onConnected(String str, BleWrapper bleWrapper) {
        runOnUiThread(new f());
    }

    @Override // org.apache.cordova.CordovaActivity, android.app.Activity
    public void onCreate(Bundle bundle) {
        super.onCreate(bundle);
        setRequestedOrientation(1);
        Bundle extras = getIntent().getExtras();
        if (extras != null && extras.getBoolean("cdvStartInBackground", false)) {
            moveTaskToBack(true);
        }
        loadUrl(this.launchUrl);
        this.f795b = new AisWrapper(getApplicationContext(), this, this);
    }

    @Override // com.huiyuan.ble.WrapperCallback
    public void onDeviceError(String str, BleWrapper bleWrapper, int i2, String str2) {
        runOnUiThread(new g(i2, str2));
    }

    @Override // com.huiyuan.ble.WrapperCallback
    public void onDeviceFound(String str, b.b.a.d dVar) {
    }

    @Override // com.huiyuan.ble.WrapperCallback
    public void onDisconnected(String str, BleWrapper bleWrapper) {
    }

    @Override // com.huiyuan.ble.WrapperCallback
    public void onReceiveNotification(String str, BleWrapper bleWrapper, String str2, b.b.a.a aVar) {
        String strC = aVar.c();
        StringBuilder sb = new StringBuilder();
        sb.append("会话：");
        sb.append(str2);
        sb.append("主动接收到");
        sb.append(aVar instanceof AisProtocol ? ((AisProtocol) aVar).d() : aVar.b().f637a.toString());
        sb.append("的应用协议数据\nJSON格式：\n");
        sb.append(strC);
        sb.append("\n十六进制格式：\n");
        sb.append(StringHelper.toHexString(aVar.a(), " "));
        sb.toString();
        runOnUiThread(new h(str2, strC));
    }

    @Override // com.huiyuan.ble.WrapperCallback
    public void onReceiveUartProtocolData(String str, BleWrapper bleWrapper, String str2, b.b.a.a aVar, boolean z) {
        String strC = aVar.c();
        StringBuilder sb = new StringBuilder();
        sb.append("会话：");
        sb.append(str2);
        sb.append("接收");
        sb.append(z ? "[成功]" : "[失败]");
        sb.append(aVar instanceof AisProtocol ? ((AisProtocol) aVar).d() : aVar.b().f637a.toString());
        sb.append("的应用协议数据\nJSON格式：\n");
        sb.append(strC);
        sb.append("\n十六进制格式：\n");
        sb.append(StringHelper.toHexString(aVar.a(), " "));
        runOnUiThread(new i(sb.toString()));
    }

    @Override // com.huiyuan.ble.WrapperCallback
    public void onSendUartProtocolData(String str, BleWrapper bleWrapper, String str2, b.b.a.a aVar, boolean z) {
        StringBuilder sb = new StringBuilder();
        sb.append("会话：");
        sb.append(str2);
        sb.append("发送");
        sb.append(z ? "[成功]" : "[失败]");
        sb.append(aVar instanceof AisProtocol ? ((AisProtocol) aVar).d() : aVar.b().f637a.toString());
        sb.append("的应用协议数据\nJSON格式：\n");
        sb.append(aVar.c());
        sb.append("\n十六进制格式：\n");
        sb.append(StringHelper.toHexString(aVar.a(), " "));
        runOnUiThread(new j(sb.toString()));
    }

    public final void a(String str) {
        runOnUiThread(new e(this, this, str));
    }

    @Override // b.b.a.m.e
    public void b(AisWrapper aisWrapper) {
        runOnUiThread(new b());
    }

    public AisWrapper a() {
        return this.f795b;
    }

    @Override // b.b.a.m.e
    public void a(AisWrapper aisWrapper, float f2, int i2, int i3) {
        runOnUiThread(new l(f2, i2, i3));
    }

    @Override // b.b.a.m.e
    public void a(JSONObject jSONObject) {
        runOnUiThread(new a(jSONObject));
    }

    @Override // b.b.a.m.e
    public void a(AisWrapper aisWrapper, String str) {
        runOnUiThread(new c(str));
    }

    @Override // b.b.a.m.e
    public void a(AisWrapper aisWrapper) {
        runOnUiThread(new d());
    }
}
