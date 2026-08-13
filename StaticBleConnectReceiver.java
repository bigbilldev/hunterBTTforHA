package com.huiyuan.ble;

import a.b.a.u;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/* JADX INFO: loaded from: classes.dex */
public class StaticBleConnectReceiver extends BroadcastReceiver {

    /* JADX INFO: renamed from: b, reason: collision with root package name */
    public static String f809b = StaticBleConnectReceiver.class.getSimpleName();

    /* JADX INFO: renamed from: a, reason: collision with root package name */
    public String f810a = "123456";

    @Override // android.content.BroadcastReceiver
    public void onReceive(Context context, Intent intent) {
        if (intent.getAction().equals("android.bluetooth.device.action.PAIRING_REQUEST")) {
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
                                u.a((Class<? extends BluetoothDevice>) bluetoothDevice.getClass(), bluetoothDevice, this.f810a);
                                abortBroadcast();
                            }
                            if (intExtra != 0) {
                                String str = "设置配对确认标志，type=" + intExtra;
                                u.a(bluetoothDevice.getClass(), bluetoothDevice, true);
                                abortBroadcast();
                                return;
                            }
                            return;
                    }
                } catch (Exception e) {
                    String str2 = "连接错误，反射异常：" + e;
                }
                String str22 = "连接错误，反射异常：" + e;
            }
        }
    }
}
