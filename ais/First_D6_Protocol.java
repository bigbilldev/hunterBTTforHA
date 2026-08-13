package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class First_D6_Protocol extends FirstProtocol {

    @j
    public byte delayDay;

    public First_D6_Protocol(c cVar) {
        super(cVar, g.First_d6, (byte) 102);
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public int b(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.delayDay = bArr[0];
        return 1;
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public byte[] e() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.delayDay);
        return cVar.a();
    }
}
