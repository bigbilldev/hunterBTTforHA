package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.b;
import b.b.d.j;
import java.util.Arrays;

/* JADX INFO: loaded from: classes.dex */
public class Second_A3_Protocol extends SecondProtocol {

    @j
    public int infiltrate;

    @j
    public int run;

    @j
    public int timestamp;

    @j
    public byte zone;

    public Second_A3_Protocol(c cVar) {
        super(cVar, g.Second_A3);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        b bVarA = b.a();
        cVar.a(this.zone);
        cVar.a(bVarA.a(this.timestamp));
        byte[] bArr = new byte[5];
        byte[] bArrA = bVarA.a(this.infiltrate);
        System.arraycopy(bArrA, 2, bArr, 1, 2);
        byte[] bArrA2 = bVarA.a(this.run);
        System.arraycopy(bArrA2, 2, bArr, 3, 2);
        bArr[0] = (byte) (bArrA2[1] | (bArrA[1] << 4));
        cVar.a(bArr);
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        b bVarA = b.a();
        if (bArr.length <= 0) {
            return 0;
        }
        this.zone = bArr[0];
        if (bArr.length <= 4) {
            return 1;
        }
        this.timestamp = bVarA.a(bVarA.a(bArr, 1, 4));
        if (bArr.length <= 9) {
            return 5;
        }
        byte[] bArr2 = new byte[4];
        System.arraycopy(bArr, 6, bArr2, 2, 2);
        bArr2[1] = (byte) ((bArr[5] >> 4) & 15);
        this.infiltrate = bVarA.a(bArr2);
        Arrays.fill(bArr2, (byte) 0);
        System.arraycopy(bArr, 8, bArr2, 2, 2);
        bArr2[1] = (byte) (bArr[5] & 15);
        this.run = bVarA.a(bArr2);
        return 10;
    }
}
