package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class Second_88_Protocol extends SecondProtocol {

    @j
    public byte endHour1;

    @j
    public byte endHour2;

    @j
    public byte endMinute1;

    @j
    public byte endMinute2;

    @j
    public byte endSecond1;

    @j
    public byte endSecond2;

    @j
    public byte runHour;

    @j
    public byte runMinute;

    @j
    public byte runSecond;

    @j
    public byte soakHour;

    @j
    public byte soakMinute;

    @j
    public byte soakSecond;

    @j
    public byte startHour1;

    @j
    public byte startHour2;

    @j
    public byte startMinute1;

    @j
    public byte startMinute2;

    @j
    public byte startSecond1;

    @j
    public byte startSecond2;

    public Second_88_Protocol(c cVar) {
        super(cVar, g.Second_88);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.startHour1);
        cVar.a(this.startMinute1);
        cVar.a(this.startSecond1);
        cVar.a(this.endHour1);
        cVar.a(this.endMinute1);
        cVar.a(this.endSecond1);
        cVar.a(this.startHour2);
        cVar.a(this.startMinute2);
        cVar.a(this.startSecond2);
        cVar.a(this.endHour2);
        cVar.a(this.endMinute2);
        cVar.a(this.endSecond2);
        cVar.a(this.runHour);
        cVar.a(this.runMinute);
        cVar.a(this.runSecond);
        cVar.a(this.soakHour);
        cVar.a(this.soakMinute);
        cVar.a(this.soakSecond);
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
        this.endHour1 = bArr[3];
        if (bArr.length <= 4) {
            return 4;
        }
        this.endMinute1 = bArr[4];
        if (bArr.length <= 5) {
            return 5;
        }
        this.endSecond1 = bArr[5];
        if (bArr.length <= 6) {
            return 6;
        }
        this.startHour2 = bArr[6];
        if (bArr.length <= 7) {
            return 7;
        }
        this.startMinute2 = bArr[7];
        if (bArr.length <= 8) {
            return 8;
        }
        this.startSecond2 = bArr[8];
        if (bArr.length <= 9) {
            return 9;
        }
        this.endHour2 = bArr[9];
        if (bArr.length <= 10) {
            return 10;
        }
        this.endMinute2 = bArr[10];
        if (bArr.length <= 11) {
            return 11;
        }
        this.endSecond2 = bArr[11];
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
        if (bArr.length <= 15) {
            return 15;
        }
        this.soakHour = bArr[15];
        if (bArr.length <= 16) {
            return 16;
        }
        this.soakMinute = bArr[16];
        if (bArr.length <= 17) {
            return 17;
        }
        this.soakSecond = bArr[17];
        return 18;
    }
}
