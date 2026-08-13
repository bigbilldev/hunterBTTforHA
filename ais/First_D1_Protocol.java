package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class First_D1_Protocol extends FirstProtocol {

    @j
    public byte detailState;

    public First_D1_Protocol(c cVar) {
        super(cVar, g.First_d1, (byte) 97);
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public int b(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.detailState = bArr[0];
        return 1;
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public byte[] e() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.detailState);
        return cVar.a();
    }
}
