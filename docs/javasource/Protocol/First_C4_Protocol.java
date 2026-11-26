package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class First_C4_Protocol extends FirstProtocol {

    @j
    public byte hour;

    @j
    public byte minute;

    @j
    public byte second;

    @j
    public byte week;

    public First_C4_Protocol(c cVar) {
        super(cVar, g.First_c4, (byte) 84);
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
        if (bArr.length <= 2) {
            return 2;
        }
        this.second = bArr[2];
        if (bArr.length <= 3) {
            return 3;
        }
        this.week = bArr[3];
        return 4;
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public byte[] e() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.hour);
        cVar.a(this.minute);
        cVar.a(this.second);
        cVar.a(this.week);
        return cVar.a();
    }
}
