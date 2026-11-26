package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.b;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class Second_9A_Protocol extends SecondProtocol {

    @j
    public short totalBytes;

    public Second_9A_Protocol(c cVar) {
        super(cVar, g.Second_9A);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(b.a().a(this.totalBytes));
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length <= 1) {
            return 0;
        }
        this.totalBytes = b.a().a(bArr, 0);
        return 2;
    }
}
