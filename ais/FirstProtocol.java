package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class FirstProtocol extends AisProtocol {

    @j
    public byte header;

    public FirstProtocol(c cVar, g gVar, byte b2) {
        super(cVar, gVar);
        this.header = b2;
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.header);
        byte[] bArrE = e();
        cVar.a((byte) bArrE.length);
        cVar.a(bArrE);
        return cVar.a();
    }

    public int b(byte[] bArr) {
        return bArr.length;
    }

    public byte[] e() {
        return new byte[0];
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.header = bArr[0];
        if (bArr.length <= 1) {
            return 1;
        }
        if (bArr.length <= 2) {
            return 2;
        }
        byte[] bArr2 = new byte[bArr.length - 2];
        System.arraycopy(bArr, 2, bArr2, 0, bArr2.length);
        return b(bArr2) + 2;
    }
}
