package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class Second_8A_Protocol extends SecondProtocol {

    @j
    public byte cmRunHour;

    @j
    public byte cmRunMinute;

    @j
    public byte cmRunSecond;

    @j
    public byte cmSoakHour;

    @j
    public byte cmSoakMinute;

    @j
    public byte cmSoakecond;

    @j
    public byte emHour;

    @j
    public byte emMinute;

    @j
    public byte emSecond;

    @j
    public byte mRunHour;

    @j
    public byte mRunMinute;

    @j
    public byte mRunSecond;

    @j
    public byte tmRunHour;

    @j
    public byte tmRunMinute;

    @j
    public byte tmRunSecond;

    @j
    public byte type;

    public Second_8A_Protocol(c cVar) {
        super(cVar, g.Second_8a);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.type);
        cVar.a(this.tmRunHour);
        cVar.a(this.tmRunMinute);
        cVar.a(this.tmRunSecond);
        cVar.a(this.cmRunHour);
        cVar.a(this.cmRunMinute);
        cVar.a(this.cmRunSecond);
        cVar.a(this.cmSoakHour);
        cVar.a(this.cmSoakMinute);
        cVar.a(this.cmSoakecond);
        cVar.a(this.mRunHour);
        cVar.a(this.mRunMinute);
        cVar.a(this.mRunSecond);
        cVar.a(this.emHour);
        cVar.a(this.emMinute);
        cVar.a(this.emSecond);
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.type = bArr[0];
        if (bArr.length <= 1) {
            return 1;
        }
        this.tmRunHour = bArr[1];
        if (bArr.length <= 2) {
            return 2;
        }
        this.tmRunMinute = bArr[2];
        if (bArr.length <= 3) {
            return 3;
        }
        this.tmRunSecond = bArr[3];
        if (bArr.length <= 4) {
            return 4;
        }
        this.cmRunHour = bArr[4];
        if (bArr.length <= 5) {
            return 5;
        }
        this.cmRunMinute = bArr[5];
        if (bArr.length <= 6) {
            return 6;
        }
        this.cmRunSecond = bArr[6];
        if (bArr.length <= 7) {
            return 7;
        }
        this.cmSoakHour = bArr[7];
        if (bArr.length <= 8) {
            return 8;
        }
        this.cmSoakMinute = bArr[8];
        if (bArr.length <= 9) {
            return 9;
        }
        this.cmSoakecond = bArr[9];
        if (bArr.length <= 10) {
            return 10;
        }
        this.mRunHour = bArr[10];
        if (bArr.length <= 11) {
            return 11;
        }
        this.mRunMinute = bArr[11];
        if (bArr.length <= 12) {
            return 12;
        }
        this.mRunSecond = bArr[12];
        if (bArr.length <= 13) {
            return 13;
        }
        this.emHour = bArr[13];
        if (bArr.length <= 14) {
            return 14;
        }
        this.emMinute = bArr[14];
        if (bArr.length <= 15) {
            return 15;
        }
        this.emSecond = bArr[15];
        return 16;
    }
}
