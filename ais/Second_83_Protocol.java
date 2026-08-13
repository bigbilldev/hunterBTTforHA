package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class Second_83_Protocol extends SecondProtocol {

    @j
    public boolean enabled;

    @j
    public byte runAllHH;

    @j
    public byte runAllMM;

    @j
    public byte runAllSS;

    @j
    public byte specialSetting;

    @j
    public byte suspendWatering;

    @j
    public boolean zone1EnableManual;

    @j
    public byte zone1Enabled;

    @j
    public byte zone1Mode;

    @j
    public boolean zone2EnableManual;

    @j
    public byte zone2Enabled;

    @j
    public byte zone2Mode;

    public Second_83_Protocol(c cVar) {
        super(cVar, g.Second_83);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.enabled);
        cVar.a(this.suspendWatering);
        cVar.a(this.zone1Enabled);
        cVar.a(this.zone1Mode);
        cVar.a(this.zone1EnableManual);
        cVar.a(this.zone2Enabled);
        cVar.a(this.zone2Mode);
        cVar.a(this.zone2EnableManual);
        cVar.a(this.runAllHH);
        cVar.a(this.runAllMM);
        cVar.a(this.runAllSS);
        cVar.a(this.specialSetting);
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.enabled = bArr[0] != 0;
        if (bArr.length <= 1) {
            return 1;
        }
        this.suspendWatering = bArr[1];
        if (bArr.length <= 2) {
            return 2;
        }
        this.zone1Enabled = bArr[2];
        if (bArr.length <= 3) {
            return 3;
        }
        this.zone1Mode = bArr[3];
        if (bArr.length <= 4) {
            return 4;
        }
        this.zone1EnableManual = bArr[4] != 0;
        if (bArr.length <= 5) {
            return 5;
        }
        this.zone2Enabled = bArr[5];
        if (bArr.length <= 6) {
            return 6;
        }
        this.zone2Mode = bArr[6];
        if (bArr.length <= 7) {
            return 7;
        }
        this.zone2EnableManual = bArr[7] != 0;
        if (bArr.length <= 8) {
            return 8;
        }
        this.runAllHH = bArr[8];
        if (bArr.length <= 9) {
            return 9;
        }
        this.runAllMM = bArr[9];
        if (bArr.length <= 10) {
            return 10;
        }
        this.runAllSS = bArr[10];
        if (bArr.length <= 11) {
            return 11;
        }
        this.specialSetting = bArr[11];
        return 12;
    }
}
