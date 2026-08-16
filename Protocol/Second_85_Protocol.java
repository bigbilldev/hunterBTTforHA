package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class Second_85_Protocol extends SecondProtocol {

    @j
    public byte headerMark;

    @j
    public byte zone1CYC;

    @j
    public byte zone1CYC1;

    @j
    public byte zone1CYC2;

    @j
    public byte zone1CYC3;

    @j
    public byte zone1TM;

    @j
    public byte zone1TM1;

    @j
    public byte zone1TM2;

    @j
    public byte zone1TM3;

    @j
    public byte zone2CYC;

    @j
    public byte zone2CYC1;

    @j
    public byte zone2CYC2;

    @j
    public byte zone2CYC3;

    @j
    public byte zone2TM;

    @j
    public byte zone2TM1;

    @j
    public byte zone2TM2;

    @j
    public byte zone2TM3;

    public Second_85_Protocol(c cVar) {
        super(cVar, g.Second_85);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.headerMark);
        cVar.a(this.zone1TM1);
        cVar.a(this.zone1TM2);
        cVar.a(this.zone1TM3);
        cVar.a(this.zone1CYC1);
        cVar.a(this.zone1CYC2);
        cVar.a(this.zone1CYC3);
        cVar.a(this.zone2TM1);
        cVar.a(this.zone2TM2);
        cVar.a(this.zone2TM3);
        cVar.a(this.zone2CYC1);
        cVar.a(this.zone2CYC2);
        cVar.a(this.zone2CYC3);
        cVar.a(this.zone1TM);
        cVar.a(this.zone1CYC);
        cVar.a(this.zone2TM);
        cVar.a(this.zone2CYC);
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.headerMark = bArr[0];
        if (bArr.length <= 1) {
            return 1;
        }
        this.zone1TM1 = bArr[1];
        if (bArr.length <= 2) {
            return 2;
        }
        this.zone1TM2 = bArr[2];
        if (bArr.length <= 3) {
            return 3;
        }
        this.zone1TM3 = bArr[3];
        if (bArr.length <= 4) {
            return 4;
        }
        this.zone1CYC1 = bArr[4];
        if (bArr.length <= 5) {
            return 5;
        }
        this.zone1CYC2 = bArr[5];
        if (bArr.length <= 6) {
            return 6;
        }
        this.zone1CYC3 = bArr[6];
        if (bArr.length <= 7) {
            return 7;
        }
        this.zone2TM1 = bArr[7];
        if (bArr.length <= 8) {
            return 8;
        }
        this.zone2TM2 = bArr[8];
        if (bArr.length <= 9) {
            return 9;
        }
        this.zone2TM3 = bArr[9];
        if (bArr.length <= 10) {
            return 10;
        }
        this.zone2CYC1 = bArr[10];
        if (bArr.length <= 11) {
            return 11;
        }
        this.zone2CYC2 = bArr[11];
        if (bArr.length <= 12) {
            return 12;
        }
        this.zone2CYC3 = bArr[12];
        if (bArr.length <= 13) {
            return 13;
        }
        this.zone1TM = bArr[13];
        if (bArr.length <= 14) {
            return 14;
        }
        this.zone1CYC = bArr[14];
        if (bArr.length <= 15) {
            return 15;
        }
        this.zone2TM = bArr[15];
        if (bArr.length <= 16) {
            return 16;
        }
        this.zone2CYC = bArr[16];
        return 17;
    }
}
