package com.huiyuan.ble;

import b.b.a.a;
import b.b.a.c;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class BatteryLevel_Protocol extends a {

    @j
    public byte value;

    public BatteryLevel_Protocol(c cVar) {
        super(cVar);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.value);
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.value = bArr[0];
        return 1;
    }
}
