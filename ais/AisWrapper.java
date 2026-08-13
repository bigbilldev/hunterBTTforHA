package com.huiyuan.ble.ais;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattService;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Rect;
import android.net.Uri;
import android.os.Environment;
import android.os.StrictMode;
import android.util.Base64;
import b.b.a.a;
import b.b.a.h;
import b.b.a.i;
import b.b.a.k;
import b.b.a.m.b;
import b.b.a.m.d;
import b.b.a.m.e;
import b.b.a.m.g;
import b.b.a.n.c;
import b.b.a.n.d;
import b.b.d.f;
import com.huiyuan.ble.BleWrapper;
import com.huiyuan.ble.WrapperCallback;
import com.huiyuan.util.JsonHelper;
import com.huiyuan.util.StringHelper;
import com.huiyuan.util.UtilHelper;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/* JADX INFO: loaded from: classes.dex */
public class AisWrapper extends BleWrapper implements c {
    public static String R = "0000fcc0-0000-1000-8000-00805f9b34fb";
    public static String S = "0000ff80-0000-1000-8000-00805f9b34fb";
    public static HashMap<b, ArrayList<String>> T = new HashMap<b, ArrayList<String>>() { // from class: com.huiyuan.ble.ais.AisWrapper.1
        {
            put(b.First, new ArrayList<String>() { // from class: com.huiyuan.ble.ais.AisWrapper.1.1
                {
                    add(AisWrapper.R);
                }
            });
            put(b.Second, new ArrayList<String>() { // from class: com.huiyuan.ble.ais.AisWrapper.1.2
                {
                    add(AisWrapper.S);
                }
            });
        }
    };
    public HashMap<b, HashMap<String, d>> J;
    public String K;
    public ZoneImageTransfer L;
    public ZoneImageReceiver M;
    public IrrigationLogReceiver N;
    public b.b.a.n.b O;
    public Uri P;
    public e Q;

    /* JADX INFO: renamed from: com.huiyuan.ble.ais.AisWrapper$4, reason: invalid class name */
    public static /* synthetic */ class AnonymousClass4 {

        /* JADX INFO: renamed from: a, reason: collision with root package name */
        public static final /* synthetic */ int[] f813a;

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public static final /* synthetic */ int[] f814b = new int[d.b.values().length];

        static {
            try {
                f814b[d.b.tiOADClientReady.ordinal()] = 1;
            } catch (NoSuchFieldError unused) {
            }
            try {
                f814b[d.b.tiOADClientCompleteFeedbackOK.ordinal()] = 2;
            } catch (NoSuchFieldError unused2) {
            }
            try {
                f814b[d.b.tiOADClientFileIsNotForDevice.ordinal()] = 3;
            } catch (NoSuchFieldError unused3) {
            }
            try {
                f814b[d.b.tiOADClientCompleteDeviceDisconnectedDuringProgramming.ordinal()] = 4;
            } catch (NoSuchFieldError unused4) {
            }
            f813a = new int[g.values().length];
            try {
                f813a[g.Second_99.ordinal()] = 1;
            } catch (NoSuchFieldError unused5) {
            }
            try {
                f813a[g.Second_9B.ordinal()] = 2;
            } catch (NoSuchFieldError unused6) {
            }
            try {
                f813a[g.Second_9E.ordinal()] = 3;
            } catch (NoSuchFieldError unused7) {
            }
        }
    }

    public class IrrigationLogReceiver {
        public Thread e;
        public boolean d = false;
        public AtomicInteger c = new AtomicInteger(0);

        /* JADX INFO: renamed from: a, reason: collision with root package name */
        public int f815a = 0;
        public int f = 0;

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public JSONArray f816b = new JSONArray();

        public IrrigationLogReceiver() {
        }

        public boolean getRunning() {
            return this.d;
        }

        public boolean receive(JSONArray jSONArray) {
            if (jSONArray.length() <= 0) {
                return true;
            }
            for (int i = 0; i < jSONArray.length(); i++) {
                try {
                    this.f816b.put(jSONArray.getJSONObject(i));
                } catch (JSONException unused) {
                    return false;
                }
            }
            this.c.set(0);
            return true;
        }

        public void start() {
            if (this.d) {
                return;
            }
            this.d = true;
            if (this.e == null) {
                this.e = new Thread() { // from class: com.huiyuan.ble.ais.AisWrapper.IrrigationLogReceiver.1
                    @Override // java.lang.Thread, java.lang.Runnable
                    public void run() {
                        int iIncrementAndGet;
                        do {
                            try {
                                try {
                                    if (IrrigationLogReceiver.this.d && !Thread.interrupted()) {
                                        if (!(IrrigationLogReceiver.this.f815a < 1)) {
                                            int length = IrrigationLogReceiver.this.f816b.length() - IrrigationLogReceiver.this.f;
                                            if (IrrigationLogReceiver.this.f816b.length() >= IrrigationLogReceiver.this.f815a) {
                                                JSONArray jSONArray = new JSONArray();
                                                for (int i = 0; i < length; i++) {
                                                    if (IrrigationLogReceiver.this.f + i < IrrigationLogReceiver.this.f816b.length()) {
                                                        try {
                                                            jSONArray.put(IrrigationLogReceiver.this.f816b.get(IrrigationLogReceiver.this.f + i));
                                                        } catch (JSONException unused) {
                                                        }
                                                    }
                                                }
                                                Second_9E_Extend_Protocol second_9E_Extend_Protocol = new Second_9E_Extend_Protocol(null);
                                                second_9E_Extend_Protocol.completed = IrrigationLogReceiver.this.f + length;
                                                second_9E_Extend_Protocol.total = IrrigationLogReceiver.this.f815a;
                                                second_9E_Extend_Protocol.data = jSONArray;
                                                AisWrapper.this.a(second_9E_Extend_Protocol);
                                            } else if (length >= 50) {
                                                JSONArray jSONArray2 = new JSONArray();
                                                for (int i2 = 0; i2 < length; i2++) {
                                                    if (IrrigationLogReceiver.this.f + i2 < IrrigationLogReceiver.this.f816b.length()) {
                                                        try {
                                                            jSONArray2.put(IrrigationLogReceiver.this.f816b.get(IrrigationLogReceiver.this.f + i2));
                                                        } catch (JSONException unused2) {
                                                        }
                                                    }
                                                }
                                                Second_9E_Extend_Protocol second_9E_Extend_Protocol2 = new Second_9E_Extend_Protocol(null);
                                                second_9E_Extend_Protocol2.completed = IrrigationLogReceiver.this.f + length;
                                                second_9E_Extend_Protocol2.total = IrrigationLogReceiver.this.f815a;
                                                second_9E_Extend_Protocol2.data = jSONArray2;
                                                AisWrapper.this.a(second_9E_Extend_Protocol2);
                                            }
                                        }
                                        Thread.sleep(1000L);
                                        iIncrementAndGet = IrrigationLogReceiver.this.c.incrementAndGet();
                                        if (iIncrementAndGet > 3 && IrrigationLogReceiver.this.f815a < 1) {
                                            throw new b.b.a.e("超时", -1);
                                        }
                                    }
                                } catch (Exception e) {
                                    AisWrapper.this.a(g.Second_9E, e instanceof b.b.a.e ? (short) ((b.b.a.e) e).getErrCode() : (short) -2, e.getMessage());
                                }
                                IrrigationLogReceiver irrigationLogReceiver = IrrigationLogReceiver.this;
                                irrigationLogReceiver.d = false;
                                irrigationLogReceiver.e = null;
                                return;
                            } catch (Throwable th) {
                                IrrigationLogReceiver irrigationLogReceiver2 = IrrigationLogReceiver.this;
                                irrigationLogReceiver2.d = false;
                                irrigationLogReceiver2.e = null;
                                throw th;
                            }
                        } while (iIncrementAndGet <= 15);
                        throw new b.b.a.e("超时!", -2);
                    }
                };
                Thread thread = this.e;
                if (thread != null) {
                    thread.start();
                }
            }
        }

        public void stop() {
            if (this.d) {
                this.d = false;
                Thread thread = this.e;
                if (thread != null) {
                    thread.interrupt();
                }
            }
        }
    }

    public class ZoneImageReceiver {

        /* JADX INFO: renamed from: a, reason: collision with root package name */
        public byte f818a;

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public int f819b;
        public Thread f;
        public boolean e = false;
        public AtomicInteger d = new AtomicInteger(0);
        public b.b.d.c c = new b.b.d.c();

        public ZoneImageReceiver(byte b2, int i) {
            this.f818a = b2;
            this.f819b = i;
        }

        public boolean getRunning() {
            return this.e;
        }

        public boolean receive(byte b2, short s, short s2, byte[] bArr) {
            if (b2 == this.f818a && s == this.f819b && bArr != null) {
                b.b.d.c cVar = this.c;
                if (s2 == cVar.c + bArr.length) {
                    cVar.a(bArr);
                    this.d.set(0);
                    return true;
                }
            }
            return false;
        }

        public void start() {
            if (this.e) {
                return;
            }
            this.e = true;
            if (this.f == null) {
                this.f = new Thread() { // from class: com.huiyuan.ble.ais.AisWrapper.ZoneImageReceiver.1
                    @Override // java.lang.Thread, java.lang.Runnable
                    public void run() {
                        do {
                            try {
                                try {
                                    if (ZoneImageReceiver.this.e && !Thread.interrupted()) {
                                        if (ZoneImageReceiver.this.f819b < 1) {
                                            throw new b.b.a.e("不存在图片数据!");
                                        }
                                        if (ZoneImageReceiver.this.c.c >= ZoneImageReceiver.this.f819b) {
                                            String str = Environment.getExternalStorageDirectory().toString() + "/zoneImage" + ((int) ZoneImageReceiver.this.f818a) + "_" + new SimpleDateFormat("yyyyMMddHHmmss").format(new Date()) + ".jpg";
                                            FileOutputStream fileOutputStream = new FileOutputStream(new File(str));
                                            fileOutputStream.write(ZoneImageReceiver.this.c.a());
                                            fileOutputStream.close();
                                            AisWrapper.this.a(ZoneImageReceiver.this.f818a == 1 ? g.Second_99 : g.Second_9B, str);
                                        } else {
                                            Thread.sleep(1000L);
                                        }
                                    }
                                } catch (Exception e) {
                                    e.getMessage();
                                    AisWrapper.this.a(ZoneImageReceiver.this.f818a == 1 ? g.Second_99 : g.Second_9B, (short) -2, e.getMessage());
                                }
                                ZoneImageReceiver zoneImageReceiver = ZoneImageReceiver.this;
                                zoneImageReceiver.e = false;
                                zoneImageReceiver.f = null;
                                return;
                            } catch (Throwable th) {
                                ZoneImageReceiver zoneImageReceiver2 = ZoneImageReceiver.this;
                                zoneImageReceiver2.e = false;
                                zoneImageReceiver2.f = null;
                                throw th;
                            }
                        } while (ZoneImageReceiver.this.d.incrementAndGet() <= 15);
                        throw new b.b.a.e("超时!");
                    }
                };
                Thread thread = this.f;
                if (thread != null) {
                    thread.start();
                }
            }
        }

        public void stop() {
            if (this.e) {
                this.e = false;
                Thread thread = this.f;
                if (thread != null) {
                    thread.interrupt();
                }
            }
        }
    }

    public class ZoneImageTransfer {
        public int c;
        public byte d;
        public String f;
        public byte g;
        public byte[] h;
        public Thread i;

        /* JADX INFO: renamed from: a, reason: collision with root package name */
        public boolean f821a = false;
        public boolean e = false;

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public int f822b = 0;

        public ZoneImageTransfer(byte b2, byte[] bArr, f fVar) {
            this.g = b2;
            this.h = bArr;
            this.d = (byte) (bArr.length % 17);
            this.c = bArr.length / 17;
            if (this.d > 0) {
                this.c++;
            }
        }

        public boolean getRunning() {
            return this.f821a;
        }

        public void start() {
            if (this.f821a) {
                return;
            }
            this.f821a = true;
            if (this.i == null) {
                this.i = new Thread() { // from class: com.huiyuan.ble.ais.AisWrapper.ZoneImageTransfer.1
                    /* JADX WARN: Code restructure failed: missing block: B:56:0x0175, code lost:
                    
                        throw new b.b.a.e("非法阀门编号!");
                     */
                    /* JADX WARN: Multi-variable type inference failed */
                    /* JADX WARN: Type inference failed for: r6v0 */
                    /* JADX WARN: Type inference failed for: r6v14 */
                    /* JADX WARN: Type inference failed for: r6v15 */
                    @Override // java.lang.Thread, java.lang.Runnable
                    /*
                        Code decompiled incorrectly, please refer to instructions dump.
                        To view partially-correct code enable 'Show inconsistent code' option in preferences
                    */
                    public void run() {
                        /*
                            Method dump skipped, instruction units count: 395
                            To view this dump change 'Code comments level' option to 'DEBUG'
                        */
                        throw new UnsupportedOperationException("Method not decompiled: com.huiyuan.ble.ais.AisWrapper.ZoneImageTransfer.AnonymousClass1.run():void");
                    }
                };
                Thread thread = this.i;
                if (thread != null) {
                    thread.start();
                }
            }
        }

        public void stop() {
            if (this.f821a) {
                this.f821a = false;
                Thread thread = this.i;
                if (thread != null) {
                    thread.interrupt();
                }
            }
        }
    }

    public AisWrapper(Context context, WrapperCallback wrapperCallback, e eVar) {
        super(i.AIS.toString(), context, wrapperCallback);
        this.J = new HashMap<b, HashMap<String, b.b.a.m.d>>() { // from class: com.huiyuan.ble.ais.AisWrapper.2
            {
                put(b.First, new HashMap<String, b.b.a.m.d>() { // from class: com.huiyuan.ble.ais.AisWrapper.2.1
                    {
                        put("BatteryService", new b.b.a.m.d("BatteryService", "0000180f-0000-1000-8000-00805f9b34fb", new h(false, "BatteryLevel", "00002a19-0000-1000-8000-00805f9b34fb")));
                        put("ble-c0", new b.b.a.m.d("ble-c0", "0000fcc0-0000-1000-8000-00805f9b34fb", new b.b.a.m.f(g.First_c1), new b.b.a.m.f(g.First_c2), new b.b.a.m.f(g.First_c3), new b.b.a.m.f(g.First_c4), new b.b.a.m.f(g.First_d1, true), new b.b.a.m.f(g.First_d2, true), new b.b.a.m.f(g.First_d3), new b.b.a.m.f(g.First_d4), new b.b.a.m.f(g.First_d5), new b.b.a.m.f(g.First_d6, true), new b.b.a.m.f(g.First_d7), new b.b.a.m.f(g.First_d8), new b.b.a.m.f(g.First_d9, true), new b.b.a.m.f(g.First_e1, true), new b.b.a.m.f(g.First_e2), new b.b.a.m.f(g.First_e3), new b.b.a.m.f(g.First_e4), new b.b.a.m.f(g.First_e5), new b.b.a.m.f(g.First_e6, true), new b.b.a.m.f(g.First_e7, true), new b.b.a.m.f(g.First_e8), new b.b.a.m.f(g.First_e9), new b.b.a.m.f(g.First_ea), new b.b.a.m.f(g.First_eb, true), new b.b.a.m.f(g.First_f1), new b.b.a.m.f(g.First_f2)));
                    }
                });
                put(b.Second, new HashMap<String, b.b.a.m.d>() { // from class: com.huiyuan.ble.ais.AisWrapper.2.2
                    {
                        put("BatteryService", new b.b.a.m.d("BatteryService", "0000180f-0000-1000-8000-00805f9b34fb", new h(false, "BatteryLevel", "00002a19-0000-1000-8000-00805f9b34fb")));
                        put("GenericAccess", new b.b.a.m.d("GenericAccess", "00001800-0000-1000-8000-00805f9b34fb", new h(false, "DeviceName", "00002a00-0000-1000-8000-00805f9b34fb")));
                        put("DeviceInformation", new b.b.a.m.d("DeviceInformation", "0000180a-0000-1000-8000-00805f9b34fb", new h(false, "FirmwareVersion", "00002a26-0000-1000-8000-00805f9b34fb"), new h(false, "ManufacturerName", "00002a29-0000-1000-8000-00805f9b34fb")));
                        put("ble-80", new b.b.a.m.d("ble-80", "0000ff80-0000-1000-8000-00805f9b34fb", new b.b.a.m.f(g.Second_81), new b.b.a.m.f(g.Second_82, true), new b.b.a.m.f(g.Second_83), new b.b.a.m.f(g.Second_84), new b.b.a.m.f(g.Second_85), new b.b.a.m.f(g.Second_86), new b.b.a.m.f(g.Second_87), new b.b.a.m.f(g.Second_88), new b.b.a.m.f(g.Second_89), new b.b.a.m.f(g.Second_8a, true), new b.b.a.m.f(g.Second_8b), new b.b.a.m.f(g.Second_8c), new b.b.a.m.f(g.Second_8d), new b.b.a.m.f(g.Second_8e), new b.b.a.m.f(g.Second_8f, true), new b.b.a.m.f(g.Second_90), new b.b.a.m.f(g.Second_91), new b.b.a.m.f(g.Second_92), new b.b.a.m.f(g.Second_93), new b.b.a.m.f(g.Second_94), new b.b.a.m.f(g.Second_95), new b.b.a.m.f(g.Second_96), new b.b.a.m.f(g.Second_97), new b.b.a.m.f(g.Second_98), new b.b.a.m.f(g.Second_99, true), new b.b.a.m.f(g.Second_9A), new b.b.a.m.f(g.Second_9B, true), new b.b.a.m.f(g.Second_9C), new b.b.a.m.f(g.Second_9D), new b.b.a.m.f(g.Second_A2, true), new b.b.a.m.f(g.Second_9E, true), new b.b.a.m.f(g.Second_A3, true), new b.b.a.m.f(g.Second_9F), new b.b.a.m.f(g.Second_A0), new b.b.a.m.f(g.Second_A1)));
                    }
                });
            }
        };
        this.Q = eVar;
    }

    @Override // com.huiyuan.ble.BleWrapper
    public void b(BleWrapper bleWrapper, String str, a aVar, boolean z, f fVar) {
        if (aVar instanceof Second_9D_Protocol) {
            IrrigationLogReceiver irrigationLogReceiver = this.N;
            if (irrigationLogReceiver != null) {
                irrigationLogReceiver.stop();
            }
            this.N = new IrrigationLogReceiver();
            this.N.start();
        }
        super.b(bleWrapper, str, aVar, z, fVar);
    }

    @Override // com.huiyuan.ble.BleWrapper
    public void connect(String str) throws b.b.a.e {
        String strJoin;
        String str2;
        Matcher matcher = Pattern.compile("^([^-]+)-([a-fA-F0-9]+)$", 2).matcher(str);
        if (matcher.matches()) {
            String strGroup = matcher.group(1);
            String strGroup2 = matcher.group(2);
            ArrayList arrayList = new ArrayList();
            int i = 0;
            while (i < strGroup2.length()) {
                int i2 = i + 1;
                if (i2 % 2 == 0) {
                    arrayList.add(strGroup2.substring(i - 1, i2));
                }
                i = i2;
            }
            strJoin = UtilHelper.join(":", arrayList);
            str2 = strGroup;
        } else {
            strJoin = "";
            str2 = str;
        }
        if (!StringHelper.isEmpty(strJoin)) {
            if (!this.A.containsKey(strJoin)) {
                this.A.put(strJoin, new b.b.a.m.a(str2.startsWith("BTT") ? b.First : b.Second, str2, strJoin, 0, new k(this.f779b)));
            }
            str = strJoin;
        }
        super.connect(str);
    }

    public void continueZoneImageSend(f fVar) {
        ZoneImageTransfer zoneImageTransfer = this.L;
        if (zoneImageTransfer == null || zoneImageTransfer.getRunning()) {
            if (fVar != null) {
                fVar.error(this.L == null ? "不存在发送任务!" : "发送任务正在运行中!");
            }
        } else {
            this.L.start();
            if (fVar != null) {
                fVar.success("ok");
            }
        }
    }

    public String getAllDemoProtocolJson() {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<b, HashMap<String, b.b.a.m.d>> entry : this.J.entrySet()) {
            sb.append(entry.getKey().toString() + "代产品\n");
            for (Map.Entry<String, b.b.a.m.d> entry2 : entry.getValue().entrySet()) {
                StringBuilder sbA = b.a.a.a.a.a("服务：");
                sbA.append(entry2.getKey());
                sb.append(sbA.toString());
                for (Map.Entry entry3 : entry2.getValue().c.entrySet()) {
                    if (entry2.getKey().startsWith("ble-")) {
                        StringBuilder sbA2 = b.a.a.a.a.a("应用协议");
                        sbA2.append(((AisProtocol) ((b.b.a.m.c) entry3.getValue()).a()).d().toString());
                        sbA2.append("\n");
                        sb.append(sbA2.toString());
                    } else {
                        StringBuilder sbA3 = b.a.a.a.a.a("系统协议");
                        sbA3.append(((b.b.a.m.c) entry3.getValue()).f638b);
                        sbA3.append("\n");
                        sb.append(sbA3.toString());
                    }
                    sb.append(((b.b.a.m.c) entry3.getValue()).a().c());
                    sb.append("\n\n");
                }
            }
        }
        return sb.toString();
    }

    public b getCurrentAisType() throws b.b.a.e {
        if (this.t == null || this.u == null || !getConnected()) {
            throw new b.b.a.e("设备未连接!");
        }
        return getCurrentDevice().e;
    }

    public b.b.a.m.a getCurrentDevice() {
        return (b.b.a.m.a) this.u;
    }

    public String getCurrentDeviceJson() {
        try {
            if (this.u == null) {
                return "{}";
            }
            JSONObject jSONObject = new JSONObject();
            jSONObject.put("name", this.u.f639a);
            jSONObject.put("address", this.u.f640b);
            jSONObject.put("type", getCurrentDevice().e);
            jSONObject.put("rssi", this.u.c);
            return jSONObject.toString();
        } catch (Exception unused) {
            return "{}";
        }
    }

    public ArrayList<String> getCurrentProtocolTypes() {
        ArrayList<String> arrayList = new ArrayList<>();
        if (this.t != null && this.u != null && getConnected()) {
            for (Map.Entry<String, b.b.a.m.d> entry : this.J.get(getCurrentDevice().e).entrySet()) {
                for (Map.Entry entry2 : entry.getValue().c.entrySet()) {
                    if (!entry.getKey().startsWith("ble-")) {
                        arrayList.add(((b.b.a.m.c) entry2.getValue()).f638b);
                    } else if (((b.b.a.m.c) entry2.getValue()).a() == null) {
                        String str = ((String) entry2.getKey()) + " 对应的特征集为空！";
                    } else {
                        arrayList.add(((AisProtocol) ((b.b.a.m.c) entry2.getValue()).a()).d().toString());
                    }
                }
            }
        }
        return arrayList;
    }

    public String getDevicesJson() {
        try {
            JSONArray jSONArray = new JSONArray();
            synchronized (this.A) {
                try {
                    Iterator<Map.Entry<String, b.b.a.d>> it = this.A.entrySet().iterator();
                    while (it.hasNext()) {
                        b.b.a.m.a aVar = (b.b.a.m.a) it.next().getValue();
                        JSONObject jSONObject = new JSONObject();
                        jSONObject.put("name", aVar.f639a);
                        jSONObject.put("address", aVar.f640b);
                        jSONObject.put("type", aVar.e);
                        jSONObject.put("rssi", aVar.c);
                        k kVar = aVar.d;
                        boolean z = false;
                        jSONObject.put("connected", this.d != null && this.d.isEnabled() && kVar.f649b);
                        if (kVar.f649b || System.currentTimeMillis() - kVar.f648a <= kVar.c) {
                            z = true;
                        }
                        jSONObject.put("isOnline", z);
                        jSONArray.put(jSONObject);
                    }
                } catch (Throwable th) {
                    throw th;
                }
            }
            return jSONArray.toString();
        } catch (Exception unused) {
            return "[]";
        }
    }

    public void localOADUpdate(String str, f fVar) {
        if (StringHelper.isEmpty(str)) {
            if (fVar != null) {
                fVar.error("binPath为空!");
                return;
            }
            return;
        }
        try {
            if (!new File(str).exists()) {
                throw new Exception("文件不存在!");
            }
            a(str, fVar);
        } catch (Exception e) {
            if (fVar != null) {
                fVar.error(e.getMessage());
            }
        }
    }

    @Override // b.b.a.n.c
    public void oadProgressUpdate(float f, int i) {
        e eVar = this.Q;
        if (eVar != null) {
            eVar.a(this, f, i, this.O.m);
        }
    }

    @Override // b.b.a.n.c
    public void oadStatusUpdate(d.b bVar) {
        e eVar;
        e eVar2 = this.Q;
        if (eVar2 != null) {
            eVar2.b(this, b.b.a.n.d.a(bVar));
        }
        int iOrdinal = bVar.ordinal();
        if (iOrdinal != 9) {
            if (iOrdinal == 10) {
                e eVar3 = this.Q;
                if (eVar3 != null) {
                    eVar3.b(this);
                    return;
                }
                return;
            }
            if (iOrdinal != 22) {
                if (iOrdinal == 25 && (eVar = this.Q) != null) {
                    eVar.a(this, bVar.toString());
                    return;
                }
                return;
            }
            e eVar4 = this.Q;
            if (eVar4 != null) {
                eVar4.a(this);
                return;
            }
            return;
        }
        b.b.a.n.b bVar2 = this.O;
        bVar2.f665a = new b.b.a.n.f(this.P, bVar2.f666b);
        byte[] bArr = bVar2.f665a.c.f681a;
        byte[] bArrC = b.b.a.n.d.c(bVar2.j);
        boolean z = true;
        for (int i = 0; i < 8; i++) {
            if (bArr[i] != bArrC[i]) {
                z = false;
            }
        }
        if (z) {
            new Thread(bVar2.o).start();
        } else {
            c cVar = bVar2.c;
            if (cVar != null) {
                cVar.oadStatusUpdate(d.b.tiOADClientFileIsNotForDevice);
            }
        }
        b.b.a.n.e eVar5 = null;
        Uri uri = this.P;
        Context context = this.c;
        new ArrayList();
        try {
            InputStream inputStreamOpenInputStream = context.getContentResolver().openInputStream(uri);
            byte[] bArr2 = new byte[inputStreamOpenInputStream.available()];
            String str = "Read " + inputStreamOpenInputStream.read(bArr2) + " bytes from file";
            b.b.a.n.e eVar6 = new b.b.a.n.e(bArr2);
            try {
                eVar6.a();
            } catch (IOException unused) {
            }
            eVar5 = eVar6;
        } catch (IOException unused2) {
        }
        if (this.Q != null) {
            try {
                JSONObject jSONObjectA = eVar5.a(eVar5);
                jSONObjectA.put("blockSize", this.O.l);
                if (this.Q != null) {
                    this.Q.a(jSONObjectA);
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }

    public void read(String str, f fVar) {
        if (this.t == null || this.u == null || !getConnected()) {
            return;
        }
        try {
            g gVarValueOf = g.valueOf(str);
            if (gVarValueOf != g.System) {
                str = gVarValueOf.getUUIDStr();
            }
        } catch (IllegalArgumentException unused) {
        }
        if (StringHelper.isEmpty(str)) {
            return;
        }
        for (Map.Entry<String, b.b.a.m.d> entry : this.J.get(getCurrentDevice().e).entrySet()) {
            b.b.a.c cVar = null;
            if (!entry.getValue().c.containsKey(str)) {
                Iterator it = entry.getValue().c.entrySet().iterator();
                while (true) {
                    if (!it.hasNext()) {
                        break;
                    }
                    Map.Entry entry2 = (Map.Entry) it.next();
                    if (((b.b.a.m.c) entry2.getValue()).f638b.equalsIgnoreCase(str)) {
                        cVar = (b.b.a.c) entry2.getValue();
                        break;
                    }
                }
            } else {
                cVar = (b.b.a.c) entry.getValue().c.get(str);
            }
            if (cVar != null) {
                if (cVar.a() != null) {
                    cVar.a().a(this, fVar);
                    return;
                }
                return;
            }
        }
    }

    public void remoteOADUpdate(String str, f fVar) {
        if (StringHelper.isEmpty(str)) {
            if (fVar != null) {
                fVar.error("url为空!");
                return;
            }
            return;
        }
        StrictMode.setThreadPolicy(new StrictMode.ThreadPolicy.Builder().detectDiskReads().detectDiskWrites().detectNetwork().penaltyLog().build());
        try {
            HttpURLConnection httpURLConnection = (HttpURLConnection) new URL(str).openConnection();
            httpURLConnection.setDoInput(true);
            httpURLConnection.connect();
            String str2 = Environment.getExternalStorageDirectory().toString() + "/oad.bin";
            FileOutputStream fileOutputStream = new FileOutputStream(new File(str2));
            InputStream inputStream = httpURLConnection.getInputStream();
            byte[] bArr = new byte[256];
            while (true) {
                int i = inputStream.read(bArr);
                if (i < 0) {
                    break;
                } else {
                    fileOutputStream.write(bArr, 0, i);
                }
            }
            fileOutputStream.close();
            a(str2, fVar);
            if (fVar != null) {
                fVar.success("ok");
            }
        } catch (Exception e) {
            if (fVar != null) {
                fVar.error(e.getMessage());
            }
        }
    }

    public void saveZoneImage(byte b2, String str, int i, int i2, f fVar) {
        saveZoneImage(b2, str, i, i2, true, fVar);
    }

    public void send(AisProtocol aisProtocol, f fVar) {
        a aVarA;
        if (this.t == null || this.u == null || aisProtocol == null || !getConnected()) {
            return;
        }
        String string = aisProtocol.d() == g.System ? aisProtocol.b() != null ? aisProtocol.b().f637a.toString() : "" : aisProtocol.d().getUUIDStr();
        if (StringHelper.isEmpty(string)) {
            return;
        }
        for (Map.Entry<String, b.b.a.m.d> entry : this.J.get(getCurrentDevice().e).entrySet()) {
            if (entry.getValue().c.containsKey(string)) {
                b.b.a.c cVar = (b.b.a.c) entry.getValue().c.get(string);
                if (cVar == null || (aVarA = cVar.a()) == null) {
                    return;
                }
                aisProtocol.a(aVarA.b());
                cVar.a().a(this, aisProtocol.a(), fVar);
                return;
            }
        }
    }

    public void sendZoneImage(byte b2, String str, int i, int i2, f fVar) {
        sendZoneImage(b2, str, i, i2, true, fVar);
    }

    public void startScan(f fVar) {
        startScan("", fVar);
    }

    public void saveZoneImage(byte b2, String str, int i, int i2, boolean z, f fVar) {
        Bitmap bitmapDecodeByteArray;
        Bitmap bitmapCreateBitmap;
        Bitmap bitmapCreateBitmap2;
        if (b2 <= 0) {
            if (fVar != null) {
                fVar.error("阀门编号非法!");
                return;
            }
            return;
        }
        if (z) {
            bitmapDecodeByteArray = BitmapFactory.decodeFile(str);
        } else {
            byte[] bArrDecode = Base64.decode(str, 0);
            bitmapDecodeByteArray = BitmapFactory.decodeByteArray(bArrDecode, 0, bArrDecode.length);
        }
        if (bitmapDecodeByteArray == null) {
            if (fVar != null) {
                fVar.error("非法的图片!");
                return;
            }
            return;
        }
        if (i < 1) {
            i = 340;
        }
        if (i2 < 1) {
            i2 = 130;
        }
        int width = bitmapDecodeByteArray.getWidth();
        int height = bitmapDecodeByteArray.getHeight();
        float f = width / height;
        float f2 = i / i2;
        if (i > width) {
            bitmapCreateBitmap2 = (i2 <= height || f2 > f) ? Bitmap.createBitmap(bitmapDecodeByteArray, 0, 0, width, (i2 * width) / i) : Bitmap.createBitmap(bitmapDecodeByteArray, 0, 0, (i * height) / i2, height);
        } else if (i2 > height) {
            bitmapCreateBitmap2 = Bitmap.createBitmap(bitmapDecodeByteArray, 0, 0, (i * height) / i2, height);
        } else {
            if (f2 > f) {
                int i3 = (i2 * width) / i;
                Bitmap bitmapCreateBitmap3 = Bitmap.createBitmap(bitmapDecodeByteArray, 0, 0, width, i3);
                bitmapCreateBitmap = Bitmap.createBitmap(i, i2, Bitmap.Config.ARGB_8888);
                new Canvas(bitmapCreateBitmap).drawBitmap(bitmapCreateBitmap3, new Rect(0, 0, width, i3), new Rect(0, 0, i, i2), new Paint());
            } else {
                int i4 = (i * height) / i2;
                Bitmap bitmapCreateBitmap4 = Bitmap.createBitmap(bitmapDecodeByteArray, 0, 0, i4, height);
                bitmapCreateBitmap = Bitmap.createBitmap(i, i2, Bitmap.Config.ARGB_8888);
                new Canvas(bitmapCreateBitmap).drawBitmap(bitmapCreateBitmap4, new Rect(0, 0, i4, height), new Rect(0, 0, i, i2), new Paint());
            }
            bitmapCreateBitmap2 = bitmapCreateBitmap;
        }
        try {
            String str2 = Environment.getExternalStorageDirectory().toString() + "/zoneImage" + ((int) b2) + "_" + new SimpleDateFormat("yyyyMMddHHmmss").format(new Date()) + ".jpg";
            FileOutputStream fileOutputStream = new FileOutputStream(new File(str2));
            bitmapCreateBitmap2.compress(Bitmap.CompressFormat.JPEG, 80, fileOutputStream);
            fileOutputStream.close();
            if (fVar != null) {
                JSONObject jSONObject = new JSONObject();
                jSONObject.put("imgPath", str2);
                fVar.success(jSONObject);
            }
        } catch (Exception e) {
            StringBuilder sbA = b.a.a.a.a.a("错误信息：");
            sbA.append(e.getMessage());
            sbA.toString();
        }
    }

    public void sendZoneImage(byte b2, String str, int i, int i2, boolean z, f fVar) {
        Bitmap bitmapDecodeByteArray;
        String str2;
        Bitmap bitmapCreateBitmap;
        Bitmap bitmapCreateBitmap2;
        String str3;
        ZoneImageTransfer zoneImageTransfer = this.L;
        if (zoneImageTransfer != null && zoneImageTransfer.getRunning()) {
            if (fVar != null) {
                fVar.error("图片数据正在发送!");
                return;
            }
            return;
        }
        byte[] byteArray = null;
        this.L = null;
        if (b2 <= 0) {
            if (fVar != null) {
                fVar.error("阀门编号非法!");
                return;
            }
            return;
        }
        if (z) {
            bitmapDecodeByteArray = BitmapFactory.decodeFile(str);
        } else {
            byte[] bArrDecode = Base64.decode(str, 0);
            bitmapDecodeByteArray = BitmapFactory.decodeByteArray(bArrDecode, 0, bArrDecode.length);
        }
        boolean zIsEmpty = StringHelper.isEmpty(str);
        if (bitmapDecodeByteArray == null && !zIsEmpty) {
            if (fVar != null) {
                fVar.error("非法的图片!");
                return;
            }
            return;
        }
        if (bitmapDecodeByteArray != null) {
            if (i < 1) {
                i = 784;
            }
            if (i2 < 1) {
                i2 = 300;
            }
            int width = bitmapDecodeByteArray.getWidth();
            int height = bitmapDecodeByteArray.getHeight();
            float f = width / height;
            float f2 = i / i2;
            if (i > width) {
                bitmapCreateBitmap2 = (i2 <= height || f2 > f) ? Bitmap.createBitmap(bitmapDecodeByteArray, 0, 0, width, (i2 * width) / i) : Bitmap.createBitmap(bitmapDecodeByteArray, 0, 0, (i * height) / i2, height);
            } else if (i2 > height) {
                bitmapCreateBitmap2 = Bitmap.createBitmap(bitmapDecodeByteArray, 0, 0, (i * height) / i2, height);
            } else {
                if (f2 > f) {
                    int i3 = (i2 * width) / i;
                    Bitmap bitmapCreateBitmap3 = Bitmap.createBitmap(bitmapDecodeByteArray, 0, 0, width, i3);
                    bitmapCreateBitmap = Bitmap.createBitmap(i, i2, Bitmap.Config.ARGB_8888);
                    new Canvas(bitmapCreateBitmap).drawBitmap(bitmapCreateBitmap3, new Rect(0, 0, width, i3), new Rect(0, 0, i, i2), new Paint());
                } else {
                    int i4 = (i * height) / i2;
                    Bitmap bitmapCreateBitmap4 = Bitmap.createBitmap(bitmapDecodeByteArray, 0, 0, i4, height);
                    bitmapCreateBitmap = Bitmap.createBitmap(i, i2, Bitmap.Config.ARGB_8888);
                    new Canvas(bitmapCreateBitmap).drawBitmap(bitmapCreateBitmap4, new Rect(0, 0, i4, height), new Rect(0, 0, i, i2), new Paint());
                }
                bitmapCreateBitmap2 = bitmapCreateBitmap;
            }
            try {
                str3 = Environment.getExternalStorageDirectory().toString() + "/tmpZoneImage" + ((int) b2) + ".jpg";
                str2 = Environment.getExternalStorageDirectory().toString() + "/zoneImage" + ((int) b2) + ".jpg";
            } catch (Exception e) {
                e = e;
                str2 = null;
            }
            try {
                ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
                bitmapCreateBitmap2.compress(Bitmap.CompressFormat.JPEG, 60, byteArrayOutputStream);
                byteArray = byteArrayOutputStream.toByteArray();
                byteArrayOutputStream.close();
                FileOutputStream fileOutputStream = new FileOutputStream(new File(str3));
                fileOutputStream.write(byteArray, 0, byteArray.length);
                fileOutputStream.close();
            } catch (Exception e2) {
                e = e2;
                StringBuilder sbA = b.a.a.a.a.a("错误信息：");
                sbA.append(e.getMessage());
                sbA.toString();
            }
        } else {
            str2 = null;
        }
        if ((byteArray == null || byteArray.length < 1) && !zIsEmpty) {
            if (fVar != null) {
                fVar.error("图片数据为空!");
                return;
            }
            return;
        }
        if (byteArray != null && byteArray.length > 40960 && !zIsEmpty) {
            if (fVar != null) {
                fVar.error("图片数据超过40K！");
                return;
            }
            return;
        }
        if (byteArray == null) {
            byteArray = new byte[0];
        }
        this.L = new ZoneImageTransfer(b2, byteArray, fVar);
        this.L.start();
        if (fVar != null) {
            try {
                JSONObject jSONObject = new JSONObject();
                jSONObject.put("imgPath", str2);
                fVar.success(jSONObject);
            } catch (JSONException e3) {
                fVar.error(e3.getMessage());
            }
        }
    }

    public void startScan(final String str, f fVar) {
        startScan(new b.b.d.a<BleWrapper>() { // from class: com.huiyuan.ble.ais.AisWrapper.3
            @Override // b.b.d.a
            public void apply(BleWrapper bleWrapper) {
                AisWrapper.this.K = str;
            }
        }, fVar);
    }

    @Override // com.huiyuan.ble.BleWrapper
    public void a(boolean z) {
        if (!z) {
            synchronized (this.A) {
                Iterator<Map.Entry<String, b.b.a.d>> it = this.A.entrySet().iterator();
                while (it.hasNext()) {
                    ((b.b.a.m.a) it.next().getValue()).d.f649b = false;
                }
            }
        }
        WrapperCallback wrapperCallback = this.f778a;
        if (wrapperCallback != null) {
            wrapperCallback.onBleState(z);
        }
    }

    /* JADX WARN: Code restructure failed: missing block: B:10:0x003e, code lost:
    
        r2 = true;
     */
    /* JADX WARN: Code restructure failed: missing block: B:11:0x0045, code lost:
    
        if (com.huiyuan.util.StringHelper.isEmpty(r11.K) != false) goto L13;
     */
    /* JADX WARN: Code restructure failed: missing block: B:12:0x0047, code lost:
    
        r2 = r1.getKey().toString().equalsIgnoreCase(r11.K);
     */
    /* JADX WARN: Code restructure failed: missing block: B:13:0x0057, code lost:
    
        if (r2 == false) goto L36;
     */
    /* JADX WARN: Code restructure failed: missing block: B:14:0x0059, code lost:
    
        r2 = r13.getAddress();
        r3 = null;
        r9 = r11.A;
     */
    /* JADX WARN: Code restructure failed: missing block: B:15:0x0060, code lost:
    
        monitor-enter(r9);
     */
    /* JADX WARN: Code restructure failed: missing block: B:17:0x0067, code lost:
    
        if (r11.A.containsKey(r2) == false) goto L21;
     */
    /* JADX WARN: Code restructure failed: missing block: B:18:0x0069, code lost:
    
        r1 = (b.b.a.m.a) r11.A.get(r2);
        r1.f639a = r14;
        r1.c = r15;
        r1.d.a();
     */
    /* JADX WARN: Code restructure failed: missing block: B:19:0x007b, code lost:
    
        r12 = move-exception;
     */
    /* JADX WARN: Code restructure failed: missing block: B:21:0x007d, code lost:
    
        r10 = new b.b.a.m.a(r1.getKey(), r14, r2, r15, new b.b.a.k(r11.f779b));
        r11.A.put(r2, r10);
        r3 = r10;
     */
    /* JADX WARN: Code restructure failed: missing block: B:22:0x009a, code lost:
    
        monitor-exit(r9);
     */
    /* JADX WARN: Code restructure failed: missing block: B:23:0x009b, code lost:
    
        if (r3 == null) goto L37;
     */
    /* JADX WARN: Code restructure failed: missing block: B:24:0x009d, code lost:
    
        b(r3);
     */
    /* JADX WARN: Code restructure failed: missing block: B:26:0x00a3, code lost:
    
        throw r12;
     */
    /* JADX WARN: Code restructure failed: missing block: B:36:0x0016, code lost:
    
        continue;
     */
    @Override // com.huiyuan.ble.BleWrapper
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct code enable 'Show inconsistent code' option in preferences
    */
    public void a(android.os.ParcelUuid r12, android.bluetooth.BluetoothDevice r13, java.lang.String r14, int r15) {
        /*
            r11 = this;
            java.util.UUID r12 = r12.getUuid()
            java.lang.String r12 = r12.toString()
            java.lang.String r12 = r12.toLowerCase()
            java.util.HashMap<b.b.a.m.b, java.util.ArrayList<java.lang.String>> r0 = com.huiyuan.ble.ais.AisWrapper.T
            java.util.Set r0 = r0.entrySet()
            java.util.Iterator r0 = r0.iterator()
        L16:
            boolean r1 = r0.hasNext()
            if (r1 == 0) goto La4
            java.lang.Object r1 = r0.next()
            java.util.Map$Entry r1 = (java.util.Map.Entry) r1
            java.lang.Object r2 = r1.getValue()
            java.util.ArrayList r2 = (java.util.ArrayList) r2
            java.util.Iterator r2 = r2.iterator()
        L2c:
            boolean r3 = r2.hasNext()
            if (r3 == 0) goto L16
            java.lang.Object r3 = r2.next()
            java.lang.String r3 = (java.lang.String) r3
            boolean r3 = r12.equalsIgnoreCase(r3)
            if (r3 == 0) goto L2c
            r2 = 1
            java.lang.String r3 = r11.K
            boolean r3 = com.huiyuan.util.StringHelper.isEmpty(r3)
            if (r3 != 0) goto L57
            java.lang.Object r2 = r1.getKey()
            b.b.a.m.b r2 = (b.b.a.m.b) r2
            java.lang.String r2 = r2.toString()
            java.lang.String r3 = r11.K
            boolean r2 = r2.equalsIgnoreCase(r3)
        L57:
            if (r2 == 0) goto L16
            java.lang.String r2 = r13.getAddress()
            r3 = 0
            java.util.HashMap<java.lang.String, b.b.a.d> r9 = r11.A
            monitor-enter(r9)
            java.util.HashMap<java.lang.String, b.b.a.d> r4 = r11.A     // Catch: java.lang.Throwable -> L7b
            boolean r4 = r4.containsKey(r2)     // Catch: java.lang.Throwable -> L7b
            if (r4 == 0) goto L7d
            java.util.HashMap<java.lang.String, b.b.a.d> r1 = r11.A     // Catch: java.lang.Throwable -> L7b
            java.lang.Object r1 = r1.get(r2)     // Catch: java.lang.Throwable -> L7b
            b.b.a.m.a r1 = (b.b.a.m.a) r1     // Catch: java.lang.Throwable -> L7b
            r1.f639a = r14     // Catch: java.lang.Throwable -> L7b
            r1.c = r15     // Catch: java.lang.Throwable -> L7b
            b.b.a.k r1 = r1.d     // Catch: java.lang.Throwable -> L7b
            r1.a()     // Catch: java.lang.Throwable -> L7b
            goto L9a
        L7b:
            r12 = move-exception
            goto La2
        L7d:
            b.b.a.m.a r10 = new b.b.a.m.a     // Catch: java.lang.Throwable -> L7b
            java.lang.Object r1 = r1.getKey()     // Catch: java.lang.Throwable -> L7b
            r4 = r1
            b.b.a.m.b r4 = (b.b.a.m.b) r4     // Catch: java.lang.Throwable -> L7b
            b.b.a.k r8 = new b.b.a.k     // Catch: java.lang.Throwable -> L7b
            int r1 = r11.f779b     // Catch: java.lang.Throwable -> L7b
            r8.<init>(r1)     // Catch: java.lang.Throwable -> L7b
            r3 = r10
            r5 = r14
            r6 = r2
            r7 = r15
            r3.<init>(r4, r5, r6, r7, r8)     // Catch: java.lang.Throwable -> L7b
            java.util.HashMap<java.lang.String, b.b.a.d> r1 = r11.A     // Catch: java.lang.Throwable -> L7b
            r1.put(r2, r10)     // Catch: java.lang.Throwable -> L7b
            r3 = r10
        L9a:
            monitor-exit(r9)     // Catch: java.lang.Throwable -> L7b
            if (r3 == 0) goto L16
            r11.b(r3)
            goto L16
        La2:
            monitor-exit(r9)     // Catch: java.lang.Throwable -> L7b
            throw r12
        La4:
            return
        */
        throw new UnsupportedOperationException("Method not decompiled: com.huiyuan.ble.ais.AisWrapper.a(android.os.ParcelUuid, android.bluetooth.BluetoothDevice, java.lang.String, int):void");
    }

    public void send(String str, f fVar) {
        String string = "";
        try {
            try {
                string = JsonHelper.fromJsonToFieldValue(str, "protocolType", true, AisProtocol.class).toString();
                g gVarValueOf = g.valueOf(string);
                if (gVarValueOf != g.System) {
                    string = gVarValueOf.getUUIDStr();
                }
            } catch (Exception unused) {
                return;
            }
        } catch (IllegalArgumentException unused2) {
        }
        if (this.t == null || this.u == null || !getConnected() || StringHelper.isEmpty(string)) {
            return;
        }
        for (Map.Entry<String, b.b.a.m.d> entry : this.J.get(getCurrentDevice().e).entrySet()) {
            b.b.a.c cVar = null;
            if (entry.getValue().c.containsKey(string)) {
                cVar = (b.b.a.c) entry.getValue().c.get(string);
            } else {
                Iterator it = entry.getValue().c.entrySet().iterator();
                while (true) {
                    if (!it.hasNext()) {
                        break;
                    }
                    Map.Entry entry2 = (Map.Entry) it.next();
                    if (((b.b.a.m.c) entry2.getValue()).f638b.equalsIgnoreCase(string)) {
                        cVar = (b.b.a.c) entry2.getValue();
                        break;
                    }
                }
            }
            if (cVar != null) {
                a aVarA = cVar.a();
                if (aVarA != null) {
                    aVarA.a(str);
                    cVar.a().a(this, aVarA.a(), fVar);
                    return;
                }
                return;
            }
        }
    }

    @Override // com.huiyuan.ble.BleWrapper
    public void a(BleWrapper bleWrapper, BluetoothGatt bluetoothGatt) throws b.b.a.e {
        for (Map.Entry<String, b.b.a.m.d> entry : this.J.get(getCurrentDevice().e).entrySet()) {
            if (!Thread.interrupted()) {
                b.b.a.m.d value = entry.getValue();
                BluetoothGattService service = bluetoothGatt.getService(value.f637a);
                if (service != null) {
                    for (Map.Entry entry2 : value.c.entrySet()) {
                        if (getConnected()) {
                            a aVarA = ((b.b.a.c) entry2.getValue()).a();
                            if (aVarA != null) {
                                aVarA.a(this, service);
                            }
                        } else {
                            throw new b.b.a.e("连接丢失!");
                        }
                    }
                }
            } else {
                throw new b.b.a.e("手动中断初始化");
            }
        }
    }

    @Override // com.huiyuan.ble.BleWrapper
    public a a(String str) {
        for (Map.Entry<String, b.b.a.m.d> entry : this.J.get(getCurrentDevice().e).entrySet()) {
            if (entry.getValue().c.containsKey(str)) {
                return ((b.b.a.m.c) entry.getValue().c.get(str)).a();
            }
        }
        return null;
    }

    public void send(String str, String str2, f fVar) {
        this.B = str;
        send(str2, fVar);
    }

    /* JADX WARN: Type inference fix 'apply assigned field type' failed
    java.lang.UnsupportedOperationException: ArgType.getObject(), call class: class jadx.core.dex.instructions.args.ArgType$UnknownArg
    	at jadx.core.dex.instructions.args.ArgType.getObject(ArgType.java:593)
    	at jadx.core.dex.attributes.nodes.ClassTypeVarsAttr.getTypeVarsMapFor(ClassTypeVarsAttr.java:35)
    	at jadx.core.dex.nodes.utils.TypeUtils.replaceClassGenerics(TypeUtils.java:177)
    	at jadx.core.dex.visitors.typeinference.FixTypesVisitor.insertExplicitUseCast(FixTypesVisitor.java:397)
    	at jadx.core.dex.visitors.typeinference.FixTypesVisitor.tryFieldTypeWithNewCasts(FixTypesVisitor.java:359)
    	at jadx.core.dex.visitors.typeinference.FixTypesVisitor.applyFieldType(FixTypesVisitor.java:309)
    	at jadx.core.dex.visitors.typeinference.FixTypesVisitor.visit(FixTypesVisitor.java:94)
     */
    public final void a(g gVar, short s, String str) {
        a aVar;
        int iOrdinal = gVar.ordinal();
        if (iOrdinal == 25) {
            Second_99_Fail_Protocol second_99_Fail_Protocol = new Second_99_Fail_Protocol(null);
            second_99_Fail_Protocol.state = s;
            second_99_Fail_Protocol.errMsg = str;
            aVar = second_99_Fail_Protocol;
        } else if (iOrdinal == 27) {
            Second_9B_Fail_Protocol second_9B_Fail_Protocol = new Second_9B_Fail_Protocol(null);
            second_9B_Fail_Protocol.state = s;
            second_9B_Fail_Protocol.errMsg = str;
            aVar = second_9B_Fail_Protocol;
        } else if (iOrdinal != 31) {
            aVar = null;
        } else {
            Second_9E_Fail_Protocol second_9E_Fail_Protocol = new Second_9E_Fail_Protocol(null);
            second_9E_Fail_Protocol.state = s;
            second_9E_Fail_Protocol.errMsg = str;
            aVar = second_9E_Fail_Protocol;
        }
        if (aVar != null) {
            String str2 = this.B;
            WrapperCallback wrapperCallback = this.f778a;
            if (wrapperCallback != null) {
                wrapperCallback.onReceiveNotification(this.v, this, str2, aVar);
            }
        }
    }

    /* JADX WARN: Type inference fix 'apply assigned field type' failed
    java.lang.UnsupportedOperationException: ArgType.getObject(), call class: class jadx.core.dex.instructions.args.ArgType$UnknownArg
    	at jadx.core.dex.instructions.args.ArgType.getObject(ArgType.java:593)
    	at jadx.core.dex.attributes.nodes.ClassTypeVarsAttr.getTypeVarsMapFor(ClassTypeVarsAttr.java:35)
    	at jadx.core.dex.nodes.utils.TypeUtils.replaceClassGenerics(TypeUtils.java:177)
    	at jadx.core.dex.visitors.typeinference.FixTypesVisitor.insertExplicitUseCast(FixTypesVisitor.java:397)
    	at jadx.core.dex.visitors.typeinference.FixTypesVisitor.tryFieldTypeWithNewCasts(FixTypesVisitor.java:359)
    	at jadx.core.dex.visitors.typeinference.FixTypesVisitor.applyFieldType(FixTypesVisitor.java:309)
    	at jadx.core.dex.visitors.typeinference.FixTypesVisitor.visit(FixTypesVisitor.java:94)
     */
    public final void a(g gVar, String str) {
        a aVar;
        int iOrdinal = gVar.ordinal();
        if (iOrdinal == 25) {
            Second_99_Success_Protocol second_99_Success_Protocol = new Second_99_Success_Protocol(null);
            second_99_Success_Protocol.imgPath = str;
            aVar = second_99_Success_Protocol;
        } else if (iOrdinal != 27) {
            aVar = null;
        } else {
            Second_9B_Success_Protocol second_9B_Success_Protocol = new Second_9B_Success_Protocol(null);
            second_9B_Success_Protocol.imgPath = str;
            aVar = second_9B_Success_Protocol;
        }
        if (aVar != null) {
            String str2 = this.B;
            WrapperCallback wrapperCallback = this.f778a;
            if (wrapperCallback != null) {
                wrapperCallback.onReceiveNotification(this.v, this, str2, aVar);
            }
        }
    }

    public final void a(a aVar) {
        if (aVar != null) {
            String str = this.B;
            WrapperCallback wrapperCallback = this.f778a;
            if (wrapperCallback != null) {
                wrapperCallback.onReceiveNotification(this.v, this, str, aVar);
            }
        }
    }

    /* JADX WARN: Type inference fix 'apply assigned field type' failed
    java.lang.UnsupportedOperationException: ArgType.getObject(), call class: class jadx.core.dex.instructions.args.ArgType$UnknownArg
    	at jadx.core.dex.instructions.args.ArgType.getObject(ArgType.java:593)
    	at jadx.core.dex.attributes.nodes.ClassTypeVarsAttr.getTypeVarsMapFor(ClassTypeVarsAttr.java:35)
    	at jadx.core.dex.nodes.utils.TypeUtils.replaceClassGenerics(TypeUtils.java:177)
    	at jadx.core.dex.visitors.typeinference.FixTypesVisitor.insertExplicitUseCast(FixTypesVisitor.java:397)
    	at jadx.core.dex.visitors.typeinference.FixTypesVisitor.tryFieldTypeWithNewCasts(FixTypesVisitor.java:359)
    	at jadx.core.dex.visitors.typeinference.FixTypesVisitor.applyFieldType(FixTypesVisitor.java:309)
    	at jadx.core.dex.visitors.typeinference.FixTypesVisitor.visit(FixTypesVisitor.java:94)
     */
    @Override // com.huiyuan.ble.BleWrapper
    public void a(BleWrapper bleWrapper, String str, a aVar) {
        if (aVar instanceof Second_99_Protocol) {
            Second_99_Protocol second_99_Protocol = (Second_99_Protocol) aVar;
            ZoneImageReceiver zoneImageReceiver = this.M;
            if (zoneImageReceiver != null && zoneImageReceiver.receive((byte) 1, second_99_Protocol.totalBytes, second_99_Protocol.completeBytes, second_99_Protocol.currentData)) {
                WrapperCallback wrapperCallback = this.f778a;
                if (wrapperCallback != null) {
                    wrapperCallback.onReceiveNotification(this.v, bleWrapper, str, aVar);
                    return;
                }
                return;
            }
            ZoneImageReceiver zoneImageReceiver2 = this.M;
            if (zoneImageReceiver2 != null) {
                zoneImageReceiver2.stop();
            }
            a(g.Second_99, (short) -1, "阀门1图片数据接收器接收校验错误!");
            return;
        }
        if (aVar instanceof Second_9B_Protocol) {
            Second_9B_Protocol second_9B_Protocol = (Second_9B_Protocol) aVar;
            ZoneImageReceiver zoneImageReceiver3 = this.M;
            if (zoneImageReceiver3 != null && zoneImageReceiver3.receive((byte) 2, second_9B_Protocol.totalBytes, second_9B_Protocol.completeBytes, second_9B_Protocol.currentData)) {
                WrapperCallback wrapperCallback2 = this.f778a;
                if (wrapperCallback2 != null) {
                    wrapperCallback2.onReceiveNotification(this.v, bleWrapper, str, aVar);
                    return;
                }
                return;
            }
            ZoneImageReceiver zoneImageReceiver4 = this.M;
            if (zoneImageReceiver4 != null) {
                zoneImageReceiver4.stop();
            }
            a(g.Second_9B, (short) -1, "阀门2图片数据接收器接收校验错误!");
            return;
        }
        if (aVar instanceof Second_A2_Protocol) {
            Second_A2_Protocol second_A2_Protocol = (Second_A2_Protocol) aVar;
            IrrigationLogReceiver irrigationLogReceiver = this.N;
            if (irrigationLogReceiver != null) {
                int i = second_A2_Protocol.totalRecords;
                if (i > 0) {
                    irrigationLogReceiver.f815a = i;
                    irrigationLogReceiver.f = 0;
                    return;
                } else {
                    irrigationLogReceiver.stop();
                    a(g.Second_9E, (short) 0, "未查询到浇灌日志记录!");
                    return;
                }
            }
            return;
        }
        if (aVar instanceof Second_9E_Protocol) {
            Second_9E_Protocol second_9E_Protocol = (Second_9E_Protocol) aVar;
            JSONArray jSONArray = new JSONArray();
            byte b2 = second_9E_Protocol.zoneId1;
            if (b2 > 0 && b2 < 3) {
                try {
                    JSONObject jSONObject = new JSONObject();
                    jSONObject.put("zone", (int) second_9E_Protocol.zoneId1);
                    jSONObject.put("timestamp", second_9E_Protocol.timestamp1);
                    jSONObject.put("infiltrate", second_9E_Protocol.infiltrateSecond1);
                    jSONObject.put("run", second_9E_Protocol.runSecond1);
                    jSONArray.put(jSONObject);
                } catch (JSONException unused) {
                }
            }
            byte b3 = second_9E_Protocol.zoneId2;
            if (b3 > 0 && b3 < 3) {
                try {
                    JSONObject jSONObject2 = new JSONObject();
                    jSONObject2.put("zone", (int) second_9E_Protocol.zoneId2);
                    jSONObject2.put("timestamp", second_9E_Protocol.timestamp2);
                    jSONObject2.put("infiltrate", second_9E_Protocol.infiltrateSecond2);
                    jSONObject2.put("run", second_9E_Protocol.runSecond2);
                    jSONArray.put(jSONObject2);
                } catch (JSONException unused2) {
                }
            }
            IrrigationLogReceiver irrigationLogReceiver2 = this.N;
            if (irrigationLogReceiver2 == null || !irrigationLogReceiver2.receive(jSONArray)) {
                IrrigationLogReceiver irrigationLogReceiver3 = this.N;
                if (irrigationLogReceiver3 != null) {
                    irrigationLogReceiver3.stop();
                }
                a(g.Second_9E, (short) -1, "日志接收器接收校验错误!");
                return;
            }
            return;
        }
        WrapperCallback wrapperCallback3 = this.f778a;
        if (wrapperCallback3 != null) {
            wrapperCallback3.onReceiveNotification(this.v, bleWrapper, str, aVar);
        }
    }

    @Override // com.huiyuan.ble.BleWrapper
    public void a(BleWrapper bleWrapper, String str, a aVar, boolean z, f fVar) {
        if (aVar instanceof Second_98_Protocol) {
            Second_98_Protocol second_98_Protocol = (Second_98_Protocol) aVar;
            ZoneImageReceiver zoneImageReceiver = this.M;
            if (zoneImageReceiver != null) {
                zoneImageReceiver.stop();
            }
            this.M = new ZoneImageReceiver((byte) 1, second_98_Protocol.totalBytes);
            this.M.start();
        } else if (aVar instanceof Second_9A_Protocol) {
            Second_9A_Protocol second_9A_Protocol = (Second_9A_Protocol) aVar;
            ZoneImageReceiver zoneImageReceiver2 = this.M;
            if (zoneImageReceiver2 != null) {
                zoneImageReceiver2.stop();
            }
            this.M = new ZoneImageReceiver((byte) 2, second_9A_Protocol.totalBytes);
            this.M.start();
        }
        super.a(bleWrapper, str, aVar, z, fVar);
    }

    public final void a(String str, f fVar) throws b.b.a.e {
        if (this.t == null || this.u == null || !getConnected()) {
            if (fVar != null) {
                fVar.error("蓝牙未连接！");
                return;
            }
            return;
        }
        this.O = new b.b.a.n.b(this.c);
        BluetoothDevice remoteDevice = this.d.getRemoteDevice(this.u.f640b);
        if (remoteDevice != null) {
            this.P = Uri.fromFile(new File(str));
            b.b.a.n.b bVar = this.O;
            bVar.c = this;
            bVar.i = new b.b.a.n.a.a(remoteDevice, bVar.f666b);
            new Thread(bVar.n).start();
            if (fVar != null) {
                fVar.success("ok");
                return;
            }
            return;
        }
        throw new b.b.a.e("指定设备未找到!");
    }
}
