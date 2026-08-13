package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class Second_82_Protocol extends SecondProtocol {

    @j
    public boolean enabled;

    @j
    public byte suspendWatering;

    @j
    public byte zone1Conflict;

    @j
    public boolean zone1EnableExtManual;

    @j
    public boolean zone1EnableManual;

    @j
    public byte zone1Enabled;

    @j
    public byte zone1Mode;

    @j
    public byte zone1State;

    @j
    public byte zone2Conflict;

    @j
    public boolean zone2EnableExtManual;

    @j
    public boolean zone2EnableManual;

    @j
    public byte zone2Enabled;

    @j
    public byte zone2Mode;

    @j
    public byte zone2State;

    public Second_82_Protocol(c cVar) {
        super(cVar, g.Second_82);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.enabled);
        cVar.a(this.suspendWatering);
        cVar.a(this.zone1Enabled);
        cVar.a(this.zone1Mode);
        cVar.a(this.zone1EnableManual);
        cVar.a(this.zone1EnableExtManual);
        cVar.a(this.zone2Enabled);
        cVar.a(this.zone2Mode);
        cVar.a(this.zone2EnableManual);
        cVar.a(this.zone2EnableExtManual);
        cVar.a(this.zone1State);
        cVar.a(this.zone2State);
        cVar.a(this.zone1Conflict);
        cVar.a(this.zone2Conflict);
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
        this.zone1EnableExtManual = bArr[5] != 0;
        if (bArr.length <= 6) {
            return 6;
        }
        this.zone2Enabled = bArr[6];
        if (bArr.length <= 7) {
            return 7;
        }
        this.zone2Mode = bArr[7];
        if (bArr.length <= 8) {
            return 8;
        }
        this.zone2EnableManual = bArr[8] != 0;
        if (bArr.length <= 9) {
            return 9;
        }
        this.zone2EnableExtManual = bArr[9] != 0;
        if (bArr.length <= 10) {
            return 10;
        }
        this.zone1State = bArr[10];
        if (bArr.length <= 11) {
            return 11;
        }
        this.zone2State = bArr[11];
        if (bArr.length <= 12) {
            return 12;
        }
        this.zone1Conflict = bArr[12];
        if (bArr.length <= 13) {
            return 13;
        }
        this.zone2Conflict = bArr[13];
        return 14;
    }
}
