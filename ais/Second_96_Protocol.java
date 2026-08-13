package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.b;
import b.b.d.j;
import java.util.Arrays;

/* JADX INFO: loaded from: classes.dex */
public class Second_96_Protocol extends SecondProtocol {

    @j
    public byte[] currentData;

    @j
    public short storePosition;

    public Second_96_Protocol(c cVar) {
        super(cVar, g.Second_96);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(b.a().a(this.storePosition));
        byte[] bArr = new byte[17];
        Arrays.fill(bArr, (byte) 0);
        byte[] bArr2 = this.currentData;
        if (bArr2 == null || bArr2.length == 0) {
            cVar.a((byte) 0);
        } else {
            cVar.a((byte) bArr2.length);
            byte[] bArr3 = this.currentData;
            System.arraycopy(bArr3, 0, bArr, 0, bArr3.length);
        }
        cVar.a(bArr);
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length <= 1) {
            return 0;
        }
        this.storePosition = b.a().a(bArr, 0);
        if (bArr.length <= 2) {
            return 2;
        }
        int i = bArr[2];
        int i2 = 3 + i;
        if (bArr.length <= i2 - 1 || i <= 0) {
            return 3;
        }
        this.currentData = new byte[i];
        System.arraycopy(bArr, 3, this.currentData, 0, i);
        return i2;
    }
}
