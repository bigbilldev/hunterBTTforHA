package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.b;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class First_EB_Protocol extends FirstProtocol {

    @j
    public byte control;

    @j
    public short minute;

    public First_EB_Protocol(c cVar) {
        super(cVar, g.First_eb, (byte) 123);
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public int b(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.control = bArr[0];
        if (bArr.length <= 1) {
            return 1;
        }
        this.minute = b.a().a(bArr, 1);
        return 3;
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public byte[] e() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.control);
        cVar.a(this.minute);
        return cVar.a();
    }
}
