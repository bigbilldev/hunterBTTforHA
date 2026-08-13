package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.b;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class Second_84_Protocol extends SecondProtocol {

    @j
    public byte day;

    @j
    public byte hour;

    @j
    public byte minute;

    @j
    public byte month;

    @j
    public byte second;

    @j
    public byte week;

    @j
    public short year;

    public Second_84_Protocol(c cVar) {
        super(cVar, g.Second_84);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(this.year);
        cVar.a(this.month);
        cVar.a(this.day);
        cVar.a(this.hour);
        cVar.a(this.minute);
        cVar.a(this.second);
        cVar.a(this.week);
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length <= 0) {
            return 0;
        }
        this.year = b.a().a(bArr, 0);
        if (bArr.length <= 2) {
            return 2;
        }
        this.month = bArr[2];
        if (bArr.length <= 3) {
            return 3;
        }
        this.day = bArr[3];
        if (bArr.length <= 4) {
            return 4;
        }
        this.hour = bArr[4];
        if (bArr.length <= 5) {
            return 5;
        }
        this.minute = bArr[5];
        if (bArr.length <= 6) {
            return 6;
        }
        this.second = bArr[6];
        if (bArr.length <= 7) {
            return 7;
        }
        this.week = bArr[7];
        return 8;
    }
}
