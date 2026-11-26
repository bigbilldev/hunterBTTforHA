package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.b;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class First_D2_Protocol extends FirstProtocol {

    @j
    public short duration;

    public First_D2_Protocol(c cVar) {
        super(cVar, g.First_d2, (byte) 98);
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public int b(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.duration = b.a().a(bArr, 0);
        return 2;
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public byte[] e() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.duration);
        return cVar.a();
    }
}
