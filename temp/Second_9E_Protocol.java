package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.b;
import b.b.d.j;
import java.util.Arrays;

/* JADX INFO: loaded from: classes.dex */
public class Second_9E_Protocol extends SecondProtocol {

    @j
    public int infiltrateSecond1;

    @j
    public int infiltrateSecond2;

    @j
    public int runSecond1;

    @j
    public int runSecond2;

    @j
    public int timestamp1;

    @j
    public int timestamp2;

    @j
    public byte zoneId1;

    @j
    public byte zoneId2;

    public Second_9E_Protocol(c cVar) {
        super(cVar, g.Second_9E);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        b bVarA = b.a();
        cVar.a(this.zoneId1);
        cVar.a(bVarA.a(this.timestamp1));
        byte[] bArr = new byte[5];
        byte[] bArrA = bVarA.a(this.infiltrateSecond1);
        System.arraycopy(bArrA, 2, bArr, 1, 2);
        byte[] bArrA2 = bVarA.a(this.runSecond1);
        System.arraycopy(bArrA2, 2, bArr, 3, 2);
        bArr[0] = (byte) ((bArrA[1] << 4) | bArrA2[1]);
        cVar.a(bArr);
        cVar.a(this.zoneId2);
        cVar.a(bVarA.a(this.timestamp2));
        Arrays.fill(bArr, (byte) 0);
        byte[] bArrA3 = bVarA.a(this.infiltrateSecond2);
        System.arraycopy(bArrA3, 2, bArr, 1, 2);
        byte[] bArrA4 = bVarA.a(this.runSecond2);
        System.arraycopy(bArrA4, 2, bArr, 3, 2);
        bArr[0] = (byte) (bArrA4[1] | (bArrA3[1] << 4));
        cVar.a(bArr);
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        b bVarA = b.a();
        if (bArr.length <= 0) {
            return 0;
        }
        this.zoneId1 = bArr[0];
        if (bArr.length <= 4) {
            return 1;
        }
        this.timestamp1 = bVarA.a(bVarA.a(bArr, 1, 4));
        if (bArr.length <= 9) {
            return 5;
        }
        byte[] bArr2 = new byte[4];
        System.arraycopy(bArr, 6, bArr2, 2, 2);
        bArr2[1] = (byte) ((bArr[5] >> 4) & 15);
        this.infiltrateSecond1 = bVarA.a(bArr2);
        Arrays.fill(bArr2, (byte) 0);
        System.arraycopy(bArr, 8, bArr2, 2, 2);
        bArr2[1] = (byte) (bArr[5] & 15);
        this.runSecond1 = bVarA.a(bArr2);
        if (bArr.length <= 10) {
            return 10;
        }
        this.zoneId2 = bArr[10];
        if (bArr.length <= 14) {
            return 11;
        }
        this.timestamp2 = bVarA.a(bVarA.a(bArr, 11, 4));
        if (bArr.length <= 19) {
            return 15;
        }
        Arrays.fill(bArr2, (byte) 0);
        System.arraycopy(bArr, 16, bArr2, 2, 2);
        bArr2[1] = (byte) ((bArr[15] >> 4) & 15);
        this.infiltrateSecond2 = bVarA.a(bArr2);
        Arrays.fill(bArr2, (byte) 0);
        System.arraycopy(bArr, 18, bArr2, 2, 2);
        bArr2[1] = (byte) (bArr[15] & 15);
        this.runSecond2 = bVarA.a(bArr2);
        return 20;
    }
}
