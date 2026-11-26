package com.huiyuan.ble;

import a.b.a.u;
import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattDescriptor;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.location.LocationManager;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.os.ParcelUuid;
import android.view.View;
import b.a.a.a.a;
import b.b.a.d;
import b.b.a.e;
import b.b.a.g;
import b.b.a.k;
import b.b.a.l;
import b.b.d.f;
import b.b.d.g;
import b.b.d.h;
import b.b.d.i;
import b.b.d.p;
import b.b.d.r;
import b.c.a.b;
import com.huiyuan.util.JsonHelper;
import com.huiyuan.util.PermissionHelper;
import com.huiyuan.util.StringHelper;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import org.apache.cordova.inappbrowser.InAppBrowser;

/* JADX INFO: loaded from: classes.dex */
public abstract class BleWrapper implements i {
    public static final Lock H = new ReentrantLock();
    public static final HashMap<Integer, BluetoothGatt> I;
    public HashMap<String, d> A;
    public String B;
    public f C;
    public f D;
    public Runnable E;
    public BluetoothGattCallback F;
    public Runnable G;

    /* JADX INFO: renamed from: a, reason: collision with root package name */
    public WrapperCallback f778a;

    /* JADX INFO: renamed from: b, reason: collision with root package name */
    public int f779b;
    public Context c;
    public BluetoothAdapter d;
    public BleWrapper e;
    public ArrayList<g> f;
    public g g;
    public Thread h;
    public boolean i;
    public Thread j;
    public int k;
    public boolean l;
    public long m;
    public long n;
    public boolean o;
    public Thread p;
    public BluetoothLeScanner q;
    public ScanCallback r;
    public BluetoothAdapter.LeScanCallback s;
    public BluetoothGatt t;
    public d u;
    public String v;
    public Activity w;
    public DynamicBleConnectReceiver x;
    public boolean y;
    public boolean z;

    /* JADX INFO: renamed from: com.huiyuan.ble.BleWrapper$10, reason: invalid class name */
    public static /* synthetic */ class AnonymousClass10 {

        /* JADX INFO: renamed from: a, reason: collision with root package name */
        public static final /* synthetic */ int[] f781a = new int[g.a.values().length];

        static {
            try {
                f781a[g.a.ENABLE_NOTIFICATION_ASYNC.ordinal()] = 1;
            } catch (NoSuchFieldError unused) {
            }
            try {
                f781a[g.a.ENABLE_NOTIFICATION_SYNC.ordinal()] = 2;
            } catch (NoSuchFieldError unused2) {
            }
            try {
                f781a[g.a.DISABLE_NOTIFICATION_ASYNC.ordinal()] = 3;
            } catch (NoSuchFieldError unused3) {
            }
            try {
                f781a[g.a.DISABLE_NOTIFICATION_SYNC.ordinal()] = 4;
            } catch (NoSuchFieldError unused4) {
            }
            try {
                f781a[g.a.READ_ASYNC.ordinal()] = 5;
            } catch (NoSuchFieldError unused5) {
            }
            try {
                f781a[g.a.READ_SYNC.ordinal()] = 6;
            } catch (NoSuchFieldError unused6) {
            }
            try {
                f781a[g.a.WRITE_ASYNC.ordinal()] = 7;
            } catch (NoSuchFieldError unused7) {
            }
            try {
                f781a[g.a.WRITE_SYNC.ordinal()] = 8;
            } catch (NoSuchFieldError unused8) {
            }
        }
    }

    /* JADX INFO: renamed from: com.huiyuan.ble.BleWrapper$3, reason: invalid class name */
    public class AnonymousClass3 extends ScanCallback {

        /* JADX INFO: renamed from: a, reason: collision with root package name */
        public final /* synthetic */ BleWrapper f783a;

        @Override // android.bluetooth.le.ScanCallback
        public void onBatchScanResults(List<ScanResult> list) {
            super.onBatchScanResults(list);
            BleWrapper bleWrapper = this.f783a;
            bleWrapper.m = 0L;
            f fVar = bleWrapper.C;
            if (fVar != null) {
                fVar.success("ok");
                this.f783a.C = null;
            }
            for (ScanResult scanResult : list) {
                BluetoothDevice device = scanResult.getDevice();
                l lVarA = l.a(scanResult.getScanRecord().getBytes());
                this.f783a.a(device, lVarA.f, scanResult.getRssi(), lVarA.f651b);
            }
        }

        @Override // android.bluetooth.le.ScanCallback
        public void onScanFailed(int i) {
            super.onScanFailed(i);
            f fVar = this.f783a.C;
            if (fVar != null) {
                fVar.error("error");
                this.f783a.C = null;
            }
        }

        @Override // android.bluetooth.le.ScanCallback
        public void onScanResult(int i, ScanResult scanResult) {
            super.onScanResult(i, scanResult);
            BleWrapper bleWrapper = this.f783a;
            bleWrapper.m = 0L;
            f fVar = bleWrapper.C;
            if (fVar != null) {
                fVar.success("ok");
                this.f783a.C = null;
            }
            BluetoothDevice device = scanResult.getDevice();
            l lVarA = l.a(scanResult.getScanRecord().getBytes());
            this.f783a.a(device, lVarA.f, scanResult.getRssi(), lVarA.f651b);
        }
    }

    public class DynamicBleConnectReceiver extends BroadcastReceiver {
        public /* synthetic */ DynamicBleConnectReceiver(AnonymousClass1 anonymousClass1) {
        }

        /* JADX WARN: Failed to restore switch over string. Please report as a decompilation issue */
        @Override // android.content.BroadcastReceiver
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (action != null) {
                byte b2 = -1;
                switch (action.hashCode()) {
                    case -1530327060:
                        if (action.equals("android.bluetooth.adapter.action.STATE_CHANGED")) {
                            b2 = 1;
                        }
                        break;
                    case -301431627:
                        if (action.equals("android.bluetooth.device.action.ACL_CONNECTED")) {
                            b2 = 2;
                        }
                        break;
                    case -223687943:
                        if (action.equals("android.bluetooth.device.action.PAIRING_REQUEST")) {
                            b2 = 0;
                        }
                        break;
                    case 1821585647:
                        if (action.equals("android.bluetooth.device.action.ACL_DISCONNECTED")) {
                            b2 = 3;
                        }
                        break;
                }
                if (b2 != 0) {
                    if (b2 != 1) {
                        return;
                    }
                    switch (intent.getIntExtra("android.bluetooth.adapter.extra.STATE", 0)) {
                        case 10:
                            BleWrapper.this.a(false);
                            break;
                        case 12:
                            BleWrapper.this.a(true);
                            break;
                    }
                }
                BluetoothDevice bluetoothDevice = (BluetoothDevice) intent.getParcelableExtra("android.bluetooth.device.extra.DEVICE");
                int intExtra = intent.getIntExtra("android.bluetooth.device.extra.PAIRING_VARIANT", Integer.MIN_VALUE);
                if (bluetoothDevice != null) {
                    try {
                        switch (bluetoothDevice.getBondState()) {
                            case 10:
                            case 11:
                            case 12:
                            default:
                                if (intExtra == 0) {
                                    String strA = BleWrapper.this.a();
                                    u.a((Class<? extends BluetoothDevice>) bluetoothDevice.getClass(), bluetoothDevice, strA);
                                    String str = "配对码【" + strA + "】配对设备===>>>>成功";
                                    ((Boolean) bluetoothDevice.getClass().getMethod("cancelPairingUserInput", new Class[0]).invoke(bluetoothDevice, new Object[0])).booleanValue();
                                    abortBroadcast();
                                }
                                if (intExtra != 0) {
                                    String str2 = "设置配对确认标志，type=" + intExtra;
                                    try {
                                        u.a(bluetoothDevice.getClass(), bluetoothDevice, true);
                                        break;
                                    } catch (Exception unused) {
                                    }
                                    abortBroadcast();
                                    return;
                                }
                                return;
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                        String str3 = "连接错误，反射异常：" + e;
                    }
                    e.printStackTrace();
                    String str32 = "连接错误，反射异常：" + e;
                }
            }
        }
    }

    static {
        H.newCondition();
        I = new HashMap<>();
    }

    public BleWrapper(String str, Context context, WrapperCallback wrapperCallback) {
        this(str, context, wrapperCallback, 5000);
    }

    public static int a(BluetoothGatt bluetoothGatt) {
        try {
            Field declaredField = bluetoothGatt.getClass().getDeclaredField("mClientIf");
            declaredField.setAccessible(true);
            return ((Integer) declaredField.get(bluetoothGatt)).intValue();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
            return 0;
        } catch (IllegalArgumentException e2) {
            e2.printStackTrace();
            return 0;
        } catch (NoSuchFieldException e3) {
            e3.printStackTrace();
            return 0;
        } catch (SecurityException e4) {
            e4.printStackTrace();
            return 0;
        }
    }

    public static void b(final BluetoothGatt bluetoothGatt) {
        try {
            int iA = a(bluetoothGatt);
            new Handler(Looper.getMainLooper()).post(new Runnable() { // from class: com.huiyuan.ble.BleWrapper.1
                @Override // java.lang.Runnable
                public void run() {
                    bluetoothGatt.disconnect();
                }
            });
            bluetoothGatt.close();
            Method method = BluetoothGatt.class.getMethod("refresh", new Class[0]);
            if (method != null) {
                method.setAccessible(true);
                ((Boolean) method.invoke(bluetoothGatt, new Object[0])).booleanValue();
            }
            String str = "成功关闭蓝牙连接并刷新，clientId=" + iA;
        } catch (Exception e) {
            StringBuilder sbA = a.a("关闭蓝牙连接并刷新失败，错误信息：");
            sbA.append(e.getMessage());
            sbA.toString();
        }
    }

    public static BluetoothGatt c(BluetoothGatt bluetoothGatt) {
        if (bluetoothGatt != null) {
            int iA = a(bluetoothGatt);
            boolean z = false;
            HashMap map = new HashMap();
            synchronized (I) {
                for (Map.Entry<Integer, BluetoothGatt> entry : I.entrySet()) {
                    int iIntValue = entry.getKey().intValue();
                    BluetoothGatt value = entry.getValue();
                    if (iA != iIntValue) {
                        map.put(Integer.valueOf(iIntValue), value);
                    } else if (bluetoothGatt.equals(value)) {
                        z = true;
                    } else {
                        map.put(Integer.valueOf(iIntValue), value);
                    }
                }
                if (!z) {
                    I.put(Integer.valueOf(iA), bluetoothGatt);
                }
            }
            for (Map.Entry entry2 : map.entrySet()) {
                int iIntValue2 = ((Integer) entry2.getKey()).intValue();
                b((BluetoothGatt) entry2.getValue());
                if (iIntValue2 != iA) {
                    synchronized (I) {
                        if (I.containsKey(Integer.valueOf(iIntValue2))) {
                            I.remove(Integer.valueOf(iIntValue2));
                        }
                    }
                }
            }
        }
        return bluetoothGatt;
    }

    public static boolean enterLock(Lock lock, Condition condition, long j, TimeUnit timeUnit) {
        lock.lock();
        try {
            return condition.await(j, timeUnit);
        } catch (InterruptedException e) {
            e.printStackTrace();
            return false;
        }
    }

    public static void leaveLock(Lock lock, Condition condition) {
        lock.lock();
        try {
            condition.signal();
        } finally {
            lock.unlock();
        }
    }

    public b.b.a.a a(String str) {
        return null;
    }

    public String a() {
        return "";
    }

    public void a(ParcelUuid parcelUuid, BluetoothDevice bluetoothDevice, String str, int i) {
    }

    public void a(BleWrapper bleWrapper, BluetoothGatt bluetoothGatt) {
    }

    public boolean b() {
        return true;
    }

    public boolean commitTransactionToBT(g gVar) {
        if (gVar.c == null) {
            if (gVar.d == g.a.GET_RSSI) {
                return this.e.t.readRemoteRssi();
            }
            return false;
        }
        switch (gVar.d.ordinal()) {
            case 1:
            case 2:
                return this.e.t.readCharacteristic(gVar.c);
            case 3:
            case 4:
                gVar.c.setValue(gVar.e);
                return this.e.t.writeCharacteristic(gVar.c);
            case 5:
            case 6:
                this.e.t.setCharacteristicNotification(gVar.c, true);
                BluetoothGattDescriptor descriptor = gVar.c.getDescriptor(UUID.fromString("00002902-0000-1000-8000-00805f9b34fb"));
                if (descriptor == null) {
                    StringBuilder sbA = a.a("Set Notification failed for :");
                    sbA.append(gVar.c.getUuid().toString());
                    sbA.toString();
                } else {
                    descriptor.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE);
                    this.e.t.writeDescriptor(descriptor);
                }
                return true;
            case 7:
            case 8:
                this.e.t.setCharacteristicNotification(gVar.c, false);
                BluetoothGattDescriptor descriptor2 = gVar.c.getDescriptor(UUID.fromString("00002902-0000-1000-8000-00805f9b34fb"));
                descriptor2.setValue(BluetoothGattDescriptor.DISABLE_NOTIFICATION_VALUE);
                this.e.t.writeDescriptor(descriptor2);
                return true;
            default:
                return false;
        }
    }

    public void connect() throws e {
        d value;
        synchronized (this.A) {
            value = !this.A.isEmpty() ? this.A.entrySet().iterator().next().getValue() : null;
        }
        if (value == null) {
            throw new e("无可连接的设备列表!", -1);
        }
        a(value);
    }

    public void connectByAddress(String str) throws e {
        d dVar;
        synchronized (this.A) {
            dVar = this.A.containsKey(str) ? this.A.get(str) : null;
        }
        if (dVar == null) {
            throw new e("指定设备不存在!", -1);
        }
        a(dVar);
    }

    public void connectByName(String str) throws e {
        d value;
        synchronized (this.A) {
            Iterator<Map.Entry<String, d>> it = this.A.entrySet().iterator();
            while (true) {
                if (!it.hasNext()) {
                    value = null;
                    break;
                }
                Map.Entry<String, d> next = it.next();
                if (str.equalsIgnoreCase(next.getValue().f639a)) {
                    value = next.getValue();
                    break;
                }
            }
        }
        if (value == null) {
            throw new e("指定设备不存在!", -1);
        }
        a(value);
    }

    public void disconnect() {
        disconnect(this.t);
        this.t = null;
    }

    public boolean getConnected() {
        return this.y;
    }

    public void getDeviceRssi(f fVar) {
        synchronized (this) {
            if (this.t != null && this.u != null && getConnected()) {
                getDeviceRssiSync(fVar);
            } else if (fVar != null) {
                fVar.error("获取失败");
            }
        }
    }

    public void getDeviceRssiSync(f fVar) {
        g gVar = new g(this, null, g.a.GET_RSSI, null, fVar);
        this.f.add(gVar);
        while (!gVar.g) {
            try {
                Thread.sleep(20L, 0);
            } catch (InterruptedException unused) {
            }
        }
    }

    public int get_currentConnectionPriority() {
        return this.k;
    }

    public void onActivityResult(int i, int i2, Intent intent) {
        if (i == 2001) {
            this.z = false;
        }
    }

    public void onDestory() {
        Activity activity;
        DynamicBleConnectReceiver dynamicBleConnectReceiver;
        stopScan();
        if (c() && (activity = this.w) != null && (dynamicBleConnectReceiver = this.x) != null) {
            activity.unregisterReceiver(dynamicBleConnectReceiver);
        }
        disconnect();
    }

    public int readCharacteristicAsync(BluetoothGattCharacteristic bluetoothGattCharacteristic, f fVar) {
        g gVar = new g(this, bluetoothGattCharacteristic, g.a.READ_SYNC, null, fVar);
        this.f.add(gVar);
        while (!gVar.g) {
            try {
                Thread.sleep(20L, 0);
            } catch (InterruptedException unused) {
            }
        }
        return 0;
    }

    public int readCharacteristicSync(BluetoothGattCharacteristic bluetoothGattCharacteristic, f fVar) {
        g gVar = new g(this, bluetoothGattCharacteristic, g.a.READ_SYNC, null, fVar);
        this.f.add(gVar);
        while (!gVar.g) {
            try {
                Thread.sleep(20L, 0);
            } catch (InterruptedException unused) {
            }
        }
        return 0;
    }

    public boolean refreshDeviceCache() {
        return false;
    }

    public boolean requestMTUChange(int i) {
        BluetoothGatt bluetoothGatt = this.t;
        if (bluetoothGatt != null) {
            return bluetoothGatt.requestMtu(i);
        }
        return false;
    }

    public int setCharacteristicNotificationAsync(BluetoothGattCharacteristic bluetoothGattCharacteristic, boolean z) {
        this.f.add(new g(this, bluetoothGattCharacteristic, z ? g.a.ENABLE_NOTIFICATION_ASYNC : g.a.DISABLE_NOTIFICATION_ASYNC, null, null));
        return 0;
    }

    public int setCharacteristicNotificationSync(BluetoothGattCharacteristic bluetoothGattCharacteristic, boolean z) {
        g gVar = new g(this, bluetoothGattCharacteristic, z ? g.a.ENABLE_NOTIFICATION_SYNC : g.a.DISABLE_NOTIFICATION_SYNC, null, null);
        this.f.add(gVar);
        while (!gVar.g) {
            try {
                Thread.sleep(20L, 0);
            } catch (InterruptedException unused) {
            }
        }
        return 0;
    }

    public boolean setCurrentConnectionPriority(int i) {
        if (!this.t.requestConnectionPriority(i)) {
            return false;
        }
        this.k = i;
        return true;
    }

    public void setSessionId(String str) {
        this.B = str;
    }

    public void startScan(b.b.d.a<BleWrapper> aVar, final f fVar) {
        if (this.d != null) {
            if (Build.VERSION.SDK_INT >= 23) {
                boolean zIsProviderEnabled = ((LocationManager) this.c.getSystemService(InAppBrowser.LOCATION)).isProviderEnabled("gps");
                if (!zIsProviderEnabled && !this.z) {
                    this.z = true;
                    g.b bVar = new g.b(this.f778a.getWrapperActivity());
                    bVar.f705b.setText(b.b.d.l.a("system prompt", "plugin", "gps", "set.title"));
                    bVar.f705b.setVisibility(0);
                    bVar.c.setText(b.b.d.l.a("please enable gps", "plugin", "gps", "set.message"));
                    String strA = b.b.d.l.a("Ok", "btn", "ok");
                    View.OnClickListener onClickListener = new View.OnClickListener() { // from class: com.huiyuan.ble.BleWrapper.4
                        @Override // android.view.View.OnClickListener
                        public void onClick(View view) {
                            BleWrapper.this.f778a.getWrapperActivity().startActivityForResult(new Intent("android.settings.LOCATION_SOURCE_SETTINGS"), 2001);
                        }
                    };
                    bVar.d.setText(strA);
                    bVar.e = onClickListener;
                    bVar.d.setOnClickListener(new h(bVar));
                    bVar.f.setContentView(bVar.f704a);
                    bVar.f.setCancelable(true);
                    bVar.f.setCanceledOnTouchOutside(false);
                    bVar.f.show();
                }
                if (!zIsProviderEnabled) {
                    if (fVar != null) {
                        fVar.error("require location permission");
                        return;
                    }
                    return;
                }
            }
            if (aVar != null) {
                aVar.apply(this);
            }
            if (!this.d.isEnabled()) {
                this.d.enable();
            }
            this.C = fVar;
            new PermissionHelper(this.c, r.f716a.get("ble")).setPermissionHandler(new p() { // from class: com.huiyuan.ble.BleWrapper.7
                @Override // b.b.d.p
                public void onPermissionDenied(String str, ArrayList<String> arrayList) {
                    f fVar2 = fVar;
                    if (fVar2 != null) {
                        fVar2.error("grant denied");
                    }
                }

                @Override // b.b.d.p
                public void onPermissionGranted(String str) {
                    BleWrapper.a(BleWrapper.this, fVar);
                }
            }).check(b.DEFAULT_IDENTIFIER);
        }
    }

    public void stopScan() {
        stopScan(false);
    }

    public int writeCharacteristicAsync(BluetoothGattCharacteristic bluetoothGattCharacteristic, byte[] bArr, f fVar) {
        b.b.a.g gVar = new b.b.a.g(this, bluetoothGattCharacteristic, g.a.WRITE_SYNC, bArr, fVar);
        this.f.add(gVar);
        while (!gVar.g) {
            try {
                Thread.sleep(20L, 0);
            } catch (InterruptedException unused) {
            }
        }
        return 0;
    }

    public int writeCharacteristicSync(BluetoothGattCharacteristic bluetoothGattCharacteristic, byte[] bArr, f fVar) {
        b.b.a.g gVar = new b.b.a.g(this, bluetoothGattCharacteristic, g.a.WRITE_SYNC, bArr, fVar);
        this.f.add(gVar);
        while (!gVar.g) {
            try {
                Thread.sleep(20L, 0);
            } catch (InterruptedException unused) {
            }
        }
        return 0;
    }

    public BleWrapper(String str, Context context, WrapperCallback wrapperCallback, int i) {
        WrapperCallback wrapperCallback2;
        this.k = 0;
        this.m = 0L;
        this.n = 0L;
        this.o = false;
        this.z = false;
        this.E = new Runnable() { // from class: com.huiyuan.ble.BleWrapper.5
            @Override // java.lang.Runnable
            public void run() {
                BleWrapper bleWrapper;
                try {
                    try {
                        BleWrapper.this.o = true;
                        BleWrapper.this.n = System.currentTimeMillis();
                        while (BleWrapper.this.o && !Thread.interrupted()) {
                            if (System.currentTimeMillis() - BleWrapper.this.n > 60000) {
                                try {
                                    BleWrapper.this.stopScan(true);
                                    BleWrapper.a(BleWrapper.this, (f) null);
                                } catch (Exception e) {
                                    e.printStackTrace();
                                }
                                BleWrapper.this.n = System.currentTimeMillis();
                            }
                            try {
                                Thread.sleep(500L);
                            } catch (InterruptedException unused) {
                            }
                        }
                        bleWrapper = BleWrapper.this;
                        bleWrapper.o = false;
                    } catch (Throwable th) {
                        BleWrapper bleWrapper2 = BleWrapper.this;
                        bleWrapper2.o = false;
                        bleWrapper2.n = 0L;
                        bleWrapper2.p = null;
                        throw th;
                    }
                } catch (Exception e2) {
                    e2.printStackTrace();
                    bleWrapper = BleWrapper.this;
                    bleWrapper.o = false;
                }
                bleWrapper.n = 0L;
                bleWrapper.p = null;
            }
        };
        this.F = new BluetoothGattCallback() { // from class: com.huiyuan.ble.BleWrapper.8
            @Override // android.bluetooth.BluetoothGattCallback
            public void onCharacteristicChanged(BluetoothGatt bluetoothGatt, BluetoothGattCharacteristic bluetoothGattCharacteristic) {
                super.onCharacteristicChanged(bluetoothGatt, bluetoothGattCharacteristic);
                String str2 = bluetoothGattCharacteristic.getUuid().toString() + "收到通知";
                String lowerCase = bluetoothGattCharacteristic.getUuid().toString().toLowerCase();
                b.b.a.a aVarA = BleWrapper.this.a(lowerCase);
                byte[] value = bluetoothGattCharacteristic.getValue();
                if (value != null) {
                    String str3 = "主动从蓝牙设备特征对象uuid=" + lowerCase + "接收到了" + value.length + "字节通告数据:" + StringHelper.toHexString(value, ",");
                    if (aVarA != null) {
                        aVarA.a(value);
                        BleWrapper bleWrapper = BleWrapper.this;
                        BleWrapper bleWrapper2 = bleWrapper.e;
                        bleWrapper.a(bleWrapper2, bleWrapper2.B, aVarA);
                    }
                }
            }

            /* JADX WARN: Removed duplicated region for block: B:19:0x007e  */
            /* JADX WARN: Removed duplicated region for block: B:34:0x00d1  */
            @Override // android.bluetooth.BluetoothGattCallback
            /*
                Code decompiled incorrectly, please refer to instructions dump.
                To view partially-correct code enable 'Show inconsistent code' option in preferences
            */
            public void onCharacteristicRead(android.bluetooth.BluetoothGatt r16, android.bluetooth.BluetoothGattCharacteristic r17, int r18) throws java.lang.Throwable {
                /*
                    Method dump skipped, instruction units count: 243
                    To view this dump change 'Code comments level' option to 'DEBUG'
                */
                throw new UnsupportedOperationException("Method not decompiled: com.huiyuan.ble.BleWrapper.AnonymousClass8.onCharacteristicRead(android.bluetooth.BluetoothGatt, android.bluetooth.BluetoothGattCharacteristic, int):void");
            }

            /* JADX WARN: Removed duplicated region for block: B:17:0x005a  */
            /* JADX WARN: Removed duplicated region for block: B:32:0x00ad  */
            @Override // android.bluetooth.BluetoothGattCallback
            /*
                Code decompiled incorrectly, please refer to instructions dump.
                To view partially-correct code enable 'Show inconsistent code' option in preferences
            */
            public void onCharacteristicWrite(android.bluetooth.BluetoothGatt r13, android.bluetooth.BluetoothGattCharacteristic r14, int r15) throws java.lang.Throwable {
                /*
                    Method dump skipped, instruction units count: 207
                    To view this dump change 'Code comments level' option to 'DEBUG'
                */
                throw new UnsupportedOperationException("Method not decompiled: com.huiyuan.ble.BleWrapper.AnonymousClass8.onCharacteristicWrite(android.bluetooth.BluetoothGatt, android.bluetooth.BluetoothGattCharacteristic, int):void");
            }

            @Override // android.bluetooth.BluetoothGattCallback
            public void onConnectionStateChange(BluetoothGatt bluetoothGatt, int i2, int i3) {
                super.onConnectionStateChange(bluetoothGatt, i2, i3);
                if (i2 != 0) {
                    BleWrapper.this.e.y = false;
                    StringBuilder sbA = a.a("Device ");
                    sbA.append(bluetoothGatt.getDevice().getAddress().toString());
                    sbA.append(" GATT SERVICE FAIL");
                    sbA.toString();
                    BleWrapper.a(BleWrapper.this, bluetoothGatt, true);
                    return;
                }
                if (i3 == 2) {
                    StringBuilder sbA2 = a.a("Device ");
                    sbA2.append(bluetoothGatt.getDevice().getAddress().toString());
                    sbA2.append(" CONNECTED");
                    sbA2.toString();
                    BleWrapper bleWrapper = BleWrapper.this;
                    bleWrapper.e.y = true;
                    if (bleWrapper.refreshDeviceCache()) {
                        try {
                            Thread.sleep(1000L);
                        } catch (InterruptedException unused) {
                        }
                    }
                    BleWrapper bleWrapper2 = BleWrapper.this.e;
                    BleWrapper.c(bluetoothGatt);
                    bleWrapper2.t = bluetoothGatt;
                    BleWrapper.this.e.t.discoverServices();
                    return;
                }
                if (i3 == 3) {
                    StringBuilder sbA3 = a.a("Device ");
                    sbA3.append(bluetoothGatt.getDevice().getAddress().toString());
                    sbA3.append(" DISCONNECTING");
                    sbA3.toString();
                    BleWrapper.this.e.y = false;
                    return;
                }
                if (i3 == 0) {
                    BleWrapper.this.e.y = false;
                    StringBuilder sbA4 = a.a("Device ");
                    sbA4.append(bluetoothGatt.getDevice().getAddress().toString());
                    sbA4.append(" DISCONNECTED");
                    sbA4.toString();
                    BleWrapper.a(BleWrapper.this, bluetoothGatt, true);
                }
            }

            @Override // android.bluetooth.BluetoothGattCallback
            public void onDescriptorRead(BluetoothGatt bluetoothGatt, BluetoothGattDescriptor bluetoothGattDescriptor, int i2) {
                super.onDescriptorRead(bluetoothGatt, bluetoothGattDescriptor, i2);
            }

            @Override // android.bluetooth.BluetoothGattCallback
            public void onDescriptorWrite(BluetoothGatt bluetoothGatt, BluetoothGattDescriptor bluetoothGattDescriptor, int i2) {
                super.onDescriptorWrite(bluetoothGatt, bluetoothGattDescriptor, i2);
                BleWrapper bleWrapper = BleWrapper.this;
                b.b.a.g gVar = bleWrapper.g;
                if (gVar != null && !gVar.g) {
                    gVar.g = true;
                    bleWrapper.f.remove(gVar);
                    BleWrapper.this.g = null;
                }
                String str2 = bluetoothGattDescriptor.getUuid().toString() + "完成特征描述的写入";
            }

            @Override // android.bluetooth.BluetoothGattCallback
            public void onMtuChanged(BluetoothGatt bluetoothGatt, int i2, int i3) {
                String str2 = "onMtuChanged: Got new MTU setting : MTU = " + i2 + "status = " + i3;
                super.onMtuChanged(bluetoothGatt, i2, i3);
            }

            @Override // android.bluetooth.BluetoothGattCallback
            public void onPhyRead(BluetoothGatt bluetoothGatt, int i2, int i3, int i4) {
                super.onPhyRead(bluetoothGatt, i2, i3, i4);
                StringBuilder sbA = a.a("onPhyRead : New TX PHY: ");
                String str2 = "Coded";
                sbA.append(i2 == 2 ? "2M" : i2 == 1 ? "1M" : i2 == 3 ? "Coded" : "Unknown");
                sbA.toString();
                StringBuilder sb = new StringBuilder();
                sb.append("onPhyRead : New RX PHY: ");
                if (i3 == 2) {
                    str2 = "2M";
                } else if (i3 == 1) {
                    str2 = "1M";
                } else if (i3 != 3) {
                    str2 = "Unknown";
                }
                sb.append(str2);
                sb.toString();
                String str3 = "onPhyRead : Status :" + i4;
            }

            @Override // android.bluetooth.BluetoothGattCallback
            public void onPhyUpdate(BluetoothGatt bluetoothGatt, int i2, int i3, int i4) {
                super.onPhyUpdate(bluetoothGatt, i2, i3, i4);
                StringBuilder sbA = a.a("onPhyUpdate : New TX PHY: ");
                String str2 = "Coded";
                sbA.append(i2 == 2 ? "2M" : i2 == 1 ? "1M" : i2 == 3 ? "Coded" : "Unknown");
                sbA.toString();
                StringBuilder sb = new StringBuilder();
                sb.append("onPhyUpdate : New RX PHY: ");
                if (i3 == 2) {
                    str2 = "2M";
                } else if (i3 == 1) {
                    str2 = "1M";
                } else if (i3 != 3) {
                    str2 = "Unknown";
                }
                sb.append(str2);
                sb.toString();
                String str3 = "onPhyRead : Status :" + i4;
            }

            @Override // android.bluetooth.BluetoothGattCallback
            public void onReadRemoteRssi(BluetoothGatt bluetoothGatt, int i2, int i3) throws Throwable {
                Throwable th;
                boolean z;
                Exception e;
                super.onReadRemoteRssi(bluetoothGatt, i2, i3);
                b.b.a.g gVar = BleWrapper.this.g;
                if (gVar == null || gVar.g) {
                    return;
                }
                boolean z2 = false;
                if (i3 == 0) {
                    try {
                        String str2 = "当前信号强度=" + i2;
                    } catch (Exception e2) {
                        e = e2;
                        z = false;
                    } catch (Throwable th2) {
                        th = th2;
                        z = false;
                    }
                    try {
                        BleWrapper.this.u.c = i2;
                        z2 = true;
                    } catch (Exception e3) {
                        e = e3;
                        z = true;
                        try {
                            e.printStackTrace();
                            z2 = z;
                        } catch (Throwable th3) {
                            th = th3;
                            BleWrapper bleWrapper = BleWrapper.this;
                            b.b.a.g gVar2 = bleWrapper.g;
                            f fVar = gVar2.h;
                            gVar2.g = true;
                            bleWrapper.f.remove(gVar2);
                            BleWrapper bleWrapper2 = BleWrapper.this;
                            bleWrapper2.g = null;
                            BleWrapper bleWrapper3 = bleWrapper2.e;
                            bleWrapper2.a(i2, z, fVar);
                            throw th;
                        }
                    } catch (Throwable th4) {
                        th = th4;
                        z = true;
                        BleWrapper bleWrapper4 = BleWrapper.this;
                        b.b.a.g gVar22 = bleWrapper4.g;
                        f fVar2 = gVar22.h;
                        gVar22.g = true;
                        bleWrapper4.f.remove(gVar22);
                        BleWrapper bleWrapper22 = BleWrapper.this;
                        bleWrapper22.g = null;
                        BleWrapper bleWrapper32 = bleWrapper22.e;
                        bleWrapper22.a(i2, z, fVar2);
                        throw th;
                    }
                }
                BleWrapper bleWrapper5 = BleWrapper.this;
                b.b.a.g gVar3 = bleWrapper5.g;
                f fVar3 = gVar3.h;
                gVar3.g = true;
                bleWrapper5.f.remove(gVar3);
                BleWrapper bleWrapper6 = BleWrapper.this;
                bleWrapper6.g = null;
                BleWrapper bleWrapper7 = bleWrapper6.e;
                bleWrapper6.a(i2, z2, fVar3);
            }

            @Override // android.bluetooth.BluetoothGattCallback
            public void onReliableWriteCompleted(BluetoothGatt bluetoothGatt, int i2) {
                super.onReliableWriteCompleted(bluetoothGatt, i2);
            }

            @Override // android.bluetooth.BluetoothGattCallback
            public void onServicesDiscovered(final BluetoothGatt bluetoothGatt, int i2) {
                super.onServicesDiscovered(bluetoothGatt, i2);
                StringBuilder sbA = a.a("Device ");
                sbA.append(bluetoothGatt.getDevice().getAddress().toString());
                sbA.append(" SERVICES DISCOVERED Status:");
                sbA.append(i2);
                sbA.toString();
                if (i2 != 0) {
                    StringBuilder sbA2 = a.a("Device ");
                    sbA2.append(bluetoothGatt.getDevice().getAddress().toString());
                    sbA2.append("Service Discovery FAILED !");
                    sbA2.toString();
                    return;
                }
                BleWrapper bleWrapper = BleWrapper.this;
                bleWrapper.h = new Thread(bleWrapper.G, "BluetoothLEDevice Transaction Handler");
                BleWrapper.this.h.start();
                String str2 = "Transaction Handler Thread : " + BleWrapper.this.h.toString();
                BleWrapper.this.j = new Thread(new Runnable() { // from class: com.huiyuan.ble.BleWrapper.8.1
                    @Override // java.lang.Runnable
                    public void run() {
                        BleWrapper bleWrapper2;
                        StringBuilder sb;
                        String message = "";
                        try {
                            try {
                                BleWrapper.this.a(BleWrapper.this.e, bluetoothGatt);
                                bleWrapper2 = BleWrapper.this;
                                bleWrapper2.j = null;
                            } catch (Exception e) {
                                e.printStackTrace();
                                message = e.getMessage();
                                BleWrapper.this.y = false;
                                bleWrapper2 = BleWrapper.this;
                                bleWrapper2.j = null;
                                if (!bleWrapper2.y) {
                                    BleWrapper.a(bleWrapper2, bluetoothGatt, true);
                                    sb = new StringBuilder();
                                }
                                bleWrapper2.b(bleWrapper2.e);
                            }
                            if (!bleWrapper2.y) {
                                BleWrapper.a(bleWrapper2, bluetoothGatt, true);
                                sb = new StringBuilder();
                                sb.append("初始化特征出错,错误信息：");
                                sb.append(message);
                                sb.toString();
                                return;
                            }
                            bleWrapper2.b(bleWrapper2.e);
                        } catch (Throwable th) {
                            BleWrapper bleWrapper3 = BleWrapper.this;
                            bleWrapper3.j = null;
                            if (bleWrapper3.y) {
                                bleWrapper3.b(bleWrapper3.e);
                            } else {
                                BleWrapper.a(bleWrapper3, bluetoothGatt, true);
                                String str3 = "初始化特征出错,错误信息：" + message;
                            }
                            throw th;
                        }
                    }
                }, "BluetoothLEDevice Init Handler");
                BleWrapper.this.j.start();
            }
        };
        this.G = new Runnable() { // from class: com.huiyuan.ble.BleWrapper.9
            @Override // java.lang.Runnable
            public void run() {
                BleWrapper bleWrapper;
                try {
                    try {
                        BleWrapper.this.i = true;
                        BleWrapper.this.f.clear();
                        BleWrapper.this.g = null;
                        String str2 = "deviceTransactionHandler started for device : " + BleWrapper.this.e.u.f640b.toString();
                        while (BleWrapper.this.i && !Thread.interrupted()) {
                            if (BleWrapper.this.g != null) {
                                long time = BleWrapper.this.g.f.getTime() - new Date().getTime();
                                if (Math.abs(time) > 5000) {
                                    String str3 = "Transaction has used more than " + (Math.abs(time) / 1000) + " seconds to complete !";
                                    if (BleWrapper.this.g.f642b >= 1) {
                                        if (BleWrapper.this.g.h != null) {
                                            BleWrapper.this.g.h.error("timeout");
                                        }
                                        new Thread(new Runnable() { // from class: com.huiyuan.ble.BleWrapper.9.1
                                            @Override // java.lang.Runnable
                                            public void run() {
                                                BleWrapper.this.e.disconnect();
                                            }
                                        }).start();
                                        throw new e("transcation timeout", -1);
                                    }
                                    BleWrapper.this.g.f642b++;
                                    BleWrapper.this.g = null;
                                } else {
                                    try {
                                        Thread.sleep(100L, 0);
                                    } catch (InterruptedException unused) {
                                    }
                                }
                            } else {
                                if (BleWrapper.this.f.size() > 0) {
                                    BleWrapper.this.g = BleWrapper.this.f.get(0);
                                    BleWrapper.this.g.f = new Date();
                                    if (!BleWrapper.this.commitTransactionToBT(BleWrapper.this.g)) {
                                        if (BleWrapper.this.g.f641a >= 3) {
                                            if (BleWrapper.this.g.h != null) {
                                                BleWrapper.this.g.h.error("error");
                                            }
                                            new Thread(new Runnable() { // from class: com.huiyuan.ble.BleWrapper.9.2
                                                @Override // java.lang.Runnable
                                                public void run() {
                                                    BleWrapper.this.e.disconnect();
                                                }
                                            }).start();
                                            throw new e("retry max times", -2);
                                        }
                                        BleWrapper.this.g.f641a++;
                                        BleWrapper.this.g = null;
                                    }
                                }
                                Thread.sleep(100L, 0);
                            }
                        }
                        bleWrapper = BleWrapper.this;
                    } catch (Throwable th) {
                        BleWrapper bleWrapper2 = BleWrapper.this;
                        bleWrapper2.i = false;
                        bleWrapper2.h = null;
                        throw th;
                    }
                } catch (e e) {
                    if (BleWrapper.this.e.f778a != null) {
                        BleWrapper.this.e.f778a.onDeviceError(BleWrapper.this.e.v, BleWrapper.this.e, e.getErrCode(), e.getMessage());
                    }
                    bleWrapper = BleWrapper.this;
                } catch (Exception e2) {
                    e2.printStackTrace();
                    bleWrapper = BleWrapper.this;
                }
                bleWrapper.i = false;
                bleWrapper.h = null;
            }
        };
        this.v = str;
        this.c = context;
        this.f778a = wrapperCallback;
        this.f779b = 5000;
        if (i > 0) {
            this.f779b = i;
        }
        AnonymousClass1 anonymousClass1 = null;
        this.D = null;
        this.C = null;
        this.d = ((BluetoothManager) this.c.getSystemService("bluetooth")).getAdapter();
        BluetoothAdapter bluetoothAdapter = this.d;
        if (bluetoothAdapter != null && !bluetoothAdapter.isEnabled()) {
            this.d.enable();
        }
        if ((c() || b()) && (wrapperCallback2 = this.f778a) != null) {
            this.w = wrapperCallback2.getWrapperActivity();
            if (this.w != null) {
                this.x = new DynamicBleConnectReceiver(anonymousClass1);
                IntentFilter intentFilter = new IntentFilter();
                if (c()) {
                    intentFilter.setPriority(999);
                    intentFilter.addAction("android.bluetooth.device.action.FOUND");
                    intentFilter.addAction("android.bluetooth.device.action.PAIRING_REQUEST");
                }
                if (b()) {
                    intentFilter.addAction("android.bluetooth.adapter.action.STATE_CHANGED");
                    intentFilter.addAction("android.bluetooth.device.action.ACL_DISCONNECTED");
                    intentFilter.addAction("android.bluetooth.device.action.ACL_CONNECTED");
                }
                this.w.registerReceiver(this.x, intentFilter);
            }
        }
        this.q = null;
        this.s = new BluetoothAdapter.LeScanCallback() { // from class: com.huiyuan.ble.BleWrapper.2
            @Override // android.bluetooth.BluetoothAdapter.LeScanCallback
            public void onLeScan(BluetoothDevice bluetoothDevice, int i2, byte[] bArr) {
                BleWrapper bleWrapper = BleWrapper.this;
                if (!bleWrapper.l) {
                    bleWrapper.l = true;
                }
                l lVarA = l.a(bArr);
                BleWrapper.this.a(bluetoothDevice, lVarA.f, i2, lVarA.f651b);
            }
        };
        this.A = new HashMap<>();
        this.B = "";
        this.f = new ArrayList<>();
        this.g = null;
        this.e = this;
    }

    public void stopScan(boolean z) {
        Thread thread;
        BluetoothAdapter bluetoothAdapter = this.d;
        if (bluetoothAdapter != null) {
            if (bluetoothAdapter.isDiscovering()) {
                this.d.cancelDiscovery();
            }
            if (!z && (thread = this.p) != null) {
                this.o = false;
                thread.interrupt();
            }
            BluetoothLeScanner bluetoothLeScanner = this.q;
            if (bluetoothLeScanner == null) {
                this.d.stopLeScan(this.s);
            } else {
                bluetoothLeScanner.stopScan(this.r);
            }
        }
    }

    public void disconnect(BluetoothGatt bluetoothGatt) {
        Thread thread = this.j;
        if (thread != null) {
            thread.interrupt();
        }
        Thread thread2 = this.h;
        if (thread2 != null) {
            this.i = false;
            thread2.interrupt();
        }
        this.f.clear();
        this.g = null;
        if (bluetoothGatt != null) {
            b(bluetoothGatt);
        }
        d dVar = this.u;
        if (dVar != null) {
            dVar.d.f649b = false;
            this.u = null;
        }
        this.y = false;
    }

    public static boolean enterLock(Lock lock, Condition condition) {
        lock.lock();
        try {
            condition.await();
            return true;
        } catch (InterruptedException e) {
            e.printStackTrace();
            return false;
        }
    }

    public int writeCharacteristicAsync(BluetoothGattCharacteristic bluetoothGattCharacteristic, byte b2, f fVar) {
        b.b.a.g gVar = new b.b.a.g(this, bluetoothGattCharacteristic, g.a.WRITE_SYNC, new byte[]{b2}, fVar);
        this.f.add(gVar);
        while (!gVar.g) {
            try {
                Thread.sleep(20L, 0);
            } catch (InterruptedException unused) {
            }
        }
        return 0;
    }

    public int writeCharacteristicSync(BluetoothGattCharacteristic bluetoothGattCharacteristic, byte b2, f fVar) {
        b.b.a.g gVar = new b.b.a.g(this, bluetoothGattCharacteristic, g.a.WRITE_SYNC, new byte[]{b2}, fVar);
        this.f.add(gVar);
        while (!gVar.g) {
            try {
                Thread.sleep(20L, 0);
            } catch (InterruptedException unused) {
            }
        }
        return 0;
    }

    public static /* synthetic */ void a(BleWrapper bleWrapper, final f fVar) {
        boolean z = true;
        if (bleWrapper.q == null) {
            if (Build.VERSION.SDK_INT >= 24) {
                long j = bleWrapper.m;
                if (j != 0 && (j <= 0 || System.currentTimeMillis() - bleWrapper.m < 6000)) {
                    z = false;
                }
            }
            if (!z) {
                if (fVar != null) {
                    fVar.error("scan too frequently");
                    return;
                }
                return;
            }
            bleWrapper.m = System.currentTimeMillis();
            bleWrapper.l = false;
            try {
                bleWrapper.d.startLeScan(bleWrapper.s);
                new Thread(new Runnable() { // from class: com.huiyuan.ble.BleWrapper.6
                    @Override // java.lang.Runnable
                    public void run() {
                        try {
                            Thread.sleep(2000L);
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                        BleWrapper bleWrapper2 = BleWrapper.this;
                        if (!bleWrapper2.l) {
                            f fVar2 = fVar;
                            if (fVar2 != null) {
                                fVar2.error("start scan error");
                                return;
                            }
                            return;
                        }
                        if (bleWrapper2.p == null) {
                            bleWrapper2.p = new Thread(bleWrapper2.E, "scan check Handler");
                            BleWrapper.this.p.start();
                        }
                        f fVar3 = fVar;
                        if (fVar3 != null) {
                            fVar3.success("ok");
                        }
                    }
                }).start();
                return;
            } catch (Exception e) {
                if (fVar != null) {
                    fVar.error(e.getMessage());
                    return;
                }
                return;
            }
        }
        if (Build.VERSION.SDK_INT >= 24) {
            long j2 = bleWrapper.m;
            if (j2 != 0 && (j2 <= 0 || System.currentTimeMillis() - bleWrapper.m < 6000)) {
                z = false;
            }
        }
        if (!z) {
            if (fVar != null) {
                fVar.error("scan too frequently");
            }
        } else {
            bleWrapper.m = System.currentTimeMillis();
            ScanSettings scanSettingsBuild = new ScanSettings.Builder().setScanMode(2).build();
            bleWrapper.q.startScan(new ArrayList(2), scanSettingsBuild, bleWrapper.r);
        }
    }

    public void connect(String str) throws e {
        d value;
        synchronized (this.A) {
            if (this.A.containsKey(str)) {
                value = this.A.get(str);
            } else {
                Iterator<Map.Entry<String, d>> it = this.A.entrySet().iterator();
                while (true) {
                    if (!it.hasNext()) {
                        value = null;
                        break;
                    }
                    Map.Entry<String, d> next = it.next();
                    if (str.equalsIgnoreCase(next.getValue().f639a)) {
                        value = next.getValue();
                        break;
                    }
                }
            }
        }
        if (value != null) {
            a(value);
            return;
        }
        throw new e("指定设备不存在!", -1);
    }

    public void b(BleWrapper bleWrapper) {
        WrapperCallback wrapperCallback = this.f778a;
        if (wrapperCallback != null) {
            wrapperCallback.onConnected(this.v, bleWrapper);
        }
        f fVar = this.D;
        if (fVar != null) {
            fVar.success("连接成功");
        }
    }

    public void b(BleWrapper bleWrapper, String str, b.b.a.a aVar, boolean z, f fVar) {
        WrapperCallback wrapperCallback = this.f778a;
        if (wrapperCallback != null) {
            wrapperCallback.onSendUartProtocolData(this.v, bleWrapper, str, aVar, z);
        }
        if (fVar != null) {
            if (z) {
                JsonHelper.doCallback(fVar, aVar.c(), true);
            } else {
                fVar.error("发送失败");
            }
        }
    }

    public void b(d dVar) {
        WrapperCallback wrapperCallback = this.f778a;
        if (wrapperCallback != null) {
            wrapperCallback.onDeviceFound(this.v, dVar);
        }
    }

    public void connect(String str, f fVar) throws e {
        disconnect();
        this.D = fVar;
        connect(str);
    }

    public boolean c() {
        return !StringHelper.isEmpty(a());
    }

    public final void a(BluetoothDevice bluetoothDevice, String str, int i, List<ParcelUuid> list) {
        try {
            Iterator<ParcelUuid> it = list.iterator();
            while (it.hasNext()) {
                a(it.next(), bluetoothDevice, str, i);
            }
        } catch (Exception unused) {
        }
    }

    public final void a(d dVar) throws e {
        BluetoothGatt bluetoothGattConnectGatt;
        stopScan();
        d dVar2 = this.u;
        if (dVar2 != null) {
            if (this.y && dVar2.f640b.equals(dVar.f640b)) {
                return;
            } else {
                disconnect();
            }
        }
        if (this.y) {
            return;
        }
        disconnect();
        BluetoothDevice remoteDevice = this.d.getRemoteDevice(dVar.f640b);
        if (remoteDevice != null) {
            if (Build.VERSION.SDK_INT >= 23) {
                bluetoothGattConnectGatt = remoteDevice.connectGatt(this.c, false, this.F, 2);
            } else {
                bluetoothGattConnectGatt = remoteDevice.connectGatt(this.c, false, this.F);
            }
            if (bluetoothGattConnectGatt != null) {
                StringBuilder sbA = a.a("connect(BleDevice device),clientId=");
                sbA.append(a(bluetoothGattConnectGatt));
                sbA.toString();
                this.u = dVar;
                k kVar = this.u.d;
                kVar.f649b = true;
                kVar.f648a = System.currentTimeMillis();
                return;
            }
            throw new e("连接失败!", -1);
        }
        throw new e("指定设备未找到!");
    }

    public static /* synthetic */ void a(BleWrapper bleWrapper, BluetoothGatt bluetoothGatt, boolean z) {
        if (z) {
            bleWrapper.disconnect(bluetoothGatt);
        }
        bleWrapper.a(bleWrapper);
    }

    public void a(boolean z) {
        WrapperCallback wrapperCallback = this.f778a;
        if (wrapperCallback != null) {
            wrapperCallback.onBleState(z);
        }
    }

    public void a(BleWrapper bleWrapper) {
        WrapperCallback wrapperCallback = this.f778a;
        if (wrapperCallback != null) {
            wrapperCallback.onConnectFailed(this.v, bleWrapper);
        }
        f fVar = this.D;
        if (fVar != null) {
            fVar.error(JsonHelper.result2Json(0, "连接失败"));
        }
    }

    public void a(BleWrapper bleWrapper, String str, b.b.a.a aVar) {
        WrapperCallback wrapperCallback = this.f778a;
        if (wrapperCallback != null) {
            wrapperCallback.onReceiveNotification(this.v, bleWrapper, str, aVar);
        }
    }

    public void a(BleWrapper bleWrapper, String str, b.b.a.a aVar, boolean z, f fVar) {
        WrapperCallback wrapperCallback = this.f778a;
        if (wrapperCallback != null) {
            wrapperCallback.onReceiveUartProtocolData(this.v, bleWrapper, str, aVar, z);
        }
        if (fVar != null) {
            if (z) {
                JsonHelper.doCallback(fVar, aVar.c(), true);
            } else {
                fVar.error("接收失败");
            }
        }
    }

    public final void a(int i, boolean z, f fVar) {
        if (fVar != null) {
            if (z) {
                fVar.success(i + "");
                return;
            }
            fVar.error("获取失败");
        }
    }
}
