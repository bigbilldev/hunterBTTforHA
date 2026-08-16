package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class First_E3_Protocol extends FirstProtocol {

    @j
    public byte hour;

    @j
    public byte minute;

    public First_E3_Protocol(c cVar) {
        super(cVar, g.First_e3, (byte) 115);
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public int b(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.hour = bArr[0];
        if (bArr.length <= 1) {
            return 1;
        }
        this.minute = bArr[1];
        return 2;
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public byte[] e() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.hour);
        cVar.a(this.minute);
        return cVar.a();
    }
}
