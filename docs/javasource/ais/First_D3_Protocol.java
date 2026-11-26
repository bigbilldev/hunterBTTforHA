package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class First_D3_Protocol extends FirstProtocol {

    @j
    public byte day;

    @j
    public byte type;

    @j
    public byte week;

    public First_D3_Protocol(c cVar) {
        super(cVar, g.First_d3, (byte) 99);
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public int b(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.type = bArr[0];
        if (bArr.length <= 1) {
            return 1;
        }
        this.day = bArr[1];
        if (bArr.length <= 2) {
            return 2;
        }
        this.week = bArr[2];
        return 3;
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public byte[] e() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.type);
        cVar.a(this.day);
        cVar.a(this.week);
        return cVar.a();
    }
}
