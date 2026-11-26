package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.b;
import b.b.d.j;
import java.util.Arrays;

/* JADX INFO: loaded from: classes.dex */
public class Second_9B_Protocol extends SecondProtocol {

    @j
    public short completeBytes;

    @j
    public byte[] currentData;

    @j
    public short totalBytes;

    public Second_9B_Protocol(c cVar) {
        super(cVar, g.Second_9B);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        b bVarA = b.a();
        cVar.a(bVarA.a(this.totalBytes));
        cVar.a(bVarA.a(this.completeBytes));
        byte[] bArr = new byte[15];
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
        b bVarA = b.a();
        if (bArr.length <= 1) {
            return 0;
        }
        this.totalBytes = bVarA.a(bArr, 0);
        if (bArr.length <= 3) {
            return 2;
        }
        this.completeBytes = bVarA.a(bArr, 2);
        if (bArr.length <= 4) {
            return 4;
        }
        int i = bArr[4];
        int i2 = 5 + i;
        if (bArr.length <= i2 - 1 || i <= 0) {
            return 5;
        }
        this.currentData = new byte[i];
        System.arraycopy(bArr, 5, this.currentData, 0, i);
        return i2;
    }
}
