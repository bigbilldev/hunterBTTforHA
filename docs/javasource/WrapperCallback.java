package com.huiyuan.ble;

import android.app.Activity;
import b.b.a.a;
import b.b.a.d;

/* JADX INFO: loaded from: classes.dex */
public interface WrapperCallback {
    Activity getWrapperActivity();

    void onBleState(boolean z);

    void onConnectFailed(String str, BleWrapper bleWrapper);

    void onConnected(String str, BleWrapper bleWrapper);

    void onDeviceError(String str, BleWrapper bleWrapper, int i, String str2);

    void onDeviceFound(String str, d dVar);

    void onDisconnected(String str, BleWrapper bleWrapper);

    void onReceiveNotification(String str, BleWrapper bleWrapper, String str2, a aVar);

    void onReceiveUartProtocolData(String str, BleWrapper bleWrapper, String str2, a aVar, boolean z);

    void onSendUartProtocolData(String str, BleWrapper bleWrapper, String str2, a aVar, boolean z);
}
