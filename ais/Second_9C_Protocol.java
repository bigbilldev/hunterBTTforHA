package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class Second_9C_Protocol extends SecondProtocol {

    @j
    public byte[] config;

    @j
    public boolean isGlobal;

    public Second_9C_Protocol(c cVar) {
        super(cVar, g.Second_9C);
        this.config = new byte[]{100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100};
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.isGlobal ? (byte) 1 : (byte) 0);
        cVar.a(this.config);
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        int i = 1;
        if (bArr.length <= 0) {
            return 0;
        }
        this.isGlobal = bArr[0] == 1;
        if (bArr.length <= 1) {
            return 1;
        }
        int iMin = Math.min(bArr.length - 1, this.config.length);
        for (int i2 = 0; i2 < iMin; i2++) {
            this.config[i2] = bArr[i];
            i++;
        }
        return i;
    }
}
