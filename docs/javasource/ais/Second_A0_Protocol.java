package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class Second_A0_Protocol extends SecondProtocol {

    @j
    public byte hour5;

    @j
    public byte hour6;

    @j
    public byte hour7;

    @j
    public byte hour8;

    @j
    public byte minute5;

    @j
    public byte minute6;

    @j
    public byte minute7;

    @j
    public byte minute8;

    @j
    public byte second5;

    @j
    public byte second6;

    @j
    public byte second7;

    @j
    public byte second8;

    public Second_A0_Protocol(c cVar) {
        super(cVar, g.Second_A0);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.hour5);
        cVar.a(this.minute5);
        cVar.a(this.second5);
        cVar.a(this.hour6);
        cVar.a(this.minute6);
        cVar.a(this.second6);
        cVar.a(this.hour7);
        cVar.a(this.minute7);
        cVar.a(this.second7);
        cVar.a(this.hour8);
        cVar.a(this.minute8);
        cVar.a(this.second8);
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.hour5 = bArr[0];
        if (bArr.length <= 1) {
            return 1;
        }
        this.minute5 = bArr[1];
        if (bArr.length <= 2) {
            return 2;
        }
        this.second5 = bArr[2];
        if (bArr.length <= 3) {
            return 3;
        }
        this.hour6 = bArr[3];
        if (bArr.length <= 4) {
            return 4;
        }
        this.minute6 = bArr[4];
        if (bArr.length <= 5) {
            return 5;
        }
        this.second6 = bArr[5];
        if (bArr.length <= 6) {
            return 6;
        }
        this.hour7 = bArr[6];
        if (bArr.length <= 7) {
            return 7;
        }
        this.minute7 = bArr[7];
        if (bArr.length <= 8) {
            return 8;
        }
        this.second7 = bArr[8];
        if (bArr.length <= 9) {
            return 9;
        }
        this.hour8 = bArr[9];
        if (bArr.length <= 10) {
            return 10;
        }
        this.minute8 = bArr[10];
        if (bArr.length <= 11) {
            return 11;
        }
        this.second8 = bArr[11];
        return 12;
    }
}
