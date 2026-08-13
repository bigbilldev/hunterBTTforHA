package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class Second_86_Protocol extends SecondProtocol {

    @j
    public byte wIndex;

    @j
    public byte zcmDays;

    @j
    public byte zcmInterval1;

    @j
    public byte zcmInterval2;

    @j
    public byte zcmOddOrEven;

    @j
    public byte zcmType;

    @j
    public byte zemHour;

    @j
    public byte zemMinute;

    @j
    public byte zemSecond;

    @j
    public byte zmHour;

    @j
    public byte zmMinute;

    @j
    public byte zmSecond;

    @j
    public byte ztmDays;

    @j
    public byte ztmInterval1;

    @j
    public byte ztmInterval2;

    @j
    public byte ztmOddOrEven;

    @j
    public byte ztmType;

    public Second_86_Protocol(c cVar) {
        super(cVar, g.Second_86);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.wIndex);
        cVar.a(this.ztmType);
        cVar.a(this.ztmDays);
        cVar.a(this.ztmInterval1);
        cVar.a(this.ztmInterval2);
        cVar.a(this.ztmOddOrEven);
        cVar.a(this.zcmType);
        cVar.a(this.zcmDays);
        cVar.a(this.zcmInterval1);
        cVar.a(this.zcmInterval2);
        cVar.a(this.zcmOddOrEven);
        cVar.a(this.zmHour);
        cVar.a(this.zmMinute);
        cVar.a(this.zmSecond);
        cVar.a(this.zemHour);
        cVar.a(this.zemMinute);
        cVar.a(this.zemSecond);
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.zemSecond = bArr[0];
        if (bArr.length <= 1) {
            return 1;
        }
        this.ztmType = bArr[1];
        if (bArr.length <= 2) {
            return 2;
        }
        this.ztmDays = bArr[2];
        if (bArr.length <= 3) {
            return 3;
        }
        this.ztmInterval1 = bArr[3];
        if (bArr.length <= 4) {
            return 4;
        }
        this.ztmInterval2 = bArr[4];
        if (bArr.length <= 5) {
            return 5;
        }
        this.ztmOddOrEven = bArr[5];
        if (bArr.length <= 6) {
            return 6;
        }
        this.zcmType = bArr[6];
        if (bArr.length <= 7) {
            return 7;
        }
        this.zcmDays = bArr[7];
        if (bArr.length <= 8) {
            return 8;
        }
        this.zcmInterval1 = bArr[8];
        if (bArr.length <= 9) {
            return 9;
        }
        this.zcmInterval2 = bArr[9];
        if (bArr.length <= 10) {
            return 10;
        }
        this.zcmOddOrEven = bArr[10];
        if (bArr.length <= 11) {
            return 11;
        }
        this.zmHour = bArr[11];
        if (bArr.length <= 12) {
            return 12;
        }
        this.zmMinute = bArr[12];
        if (bArr.length <= 13) {
            return 13;
        }
        this.zmSecond = bArr[13];
        if (bArr.length <= 14) {
            return 14;
        }
        this.zemHour = bArr[14];
        if (bArr.length <= 15) {
            return 15;
        }
        this.zemMinute = bArr[15];
        if (bArr.length <= 16) {
            return 16;
        }
        this.zemSecond = bArr[16];
        return 17;
    }
}
