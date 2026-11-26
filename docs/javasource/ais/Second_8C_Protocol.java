package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class Second_8C_Protocol extends SecondProtocol {

    @j
    public byte runHour;

    @j
    public byte runMinute;

    @j
    public byte runSecond;

    @j
    public byte startHour1;

    @j
    public byte startHour2;

    @j
    public byte startHour3;

    @j
    public byte startHour4;

    @j
    public byte startMinute1;

    @j
    public byte startMinute2;

    @j
    public byte startMinute3;

    @j
    public byte startMinute4;

    @j
    public byte startSecond1;

    @j
    public byte startSecond2;

    @j
    public byte startSecond3;

    @j
    public byte startSecond4;

    public Second_8C_Protocol(c cVar) {
        super(cVar, g.Second_8c);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.startHour1);
        cVar.a(this.startMinute1);
        cVar.a(this.startSecond1);
        cVar.a(this.startHour2);
        cVar.a(this.startMinute2);
        cVar.a(this.startSecond2);
        cVar.a(this.startHour3);
        cVar.a(this.startMinute3);
        cVar.a(this.startSecond3);
        cVar.a(this.startHour4);
        cVar.a(this.startMinute4);
        cVar.a(this.startSecond4);
        cVar.a(this.runHour);
        cVar.a(this.runMinute);
        cVar.a(this.runSecond);
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.startHour1 = bArr[0];
        if (bArr.length <= 1) {
            return 1;
        }
        this.startMinute1 = bArr[1];
        if (bArr.length <= 2) {
            return 2;
        }
        this.startSecond1 = bArr[2];
        if (bArr.length <= 3) {
            return 3;
        }
        this.startHour2 = bArr[3];
        if (bArr.length <= 4) {
            return 4;
        }
        this.startMinute2 = bArr[4];
        if (bArr.length <= 5) {
            return 5;
        }
        this.startSecond2 = bArr[5];
        if (bArr.length <= 6) {
            return 6;
        }
        this.startHour3 = bArr[6];
        if (bArr.length <= 7) {
            return 7;
        }
        this.startMinute3 = bArr[7];
        if (bArr.length <= 8) {
            return 8;
        }
        this.startSecond3 = bArr[8];
        if (bArr.length <= 9) {
            return 9;
        }
        this.startHour4 = bArr[9];
        if (bArr.length <= 10) {
            return 10;
        }
        this.startMinute4 = bArr[10];
        if (bArr.length <= 11) {
            return 11;
        }
        this.startSecond4 = bArr[11];
        if (bArr.length <= 12) {
            return 12;
        }
        this.runHour = bArr[12];
        if (bArr.length <= 13) {
            return 13;
        }
        this.runMinute = bArr[13];
        if (bArr.length <= 14) {
            return 14;
        }
        this.runSecond = bArr[14];
        return 15;
    }
}
