package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.b;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class Second_94_Protocol extends SecondProtocol {

    @j
    public short completeBytes;

    @j
    public byte currentBytes;

    @j
    public byte state;

    @j
    public short totalBytes;

    public Second_94_Protocol(c cVar) {
        super(cVar, g.Second_94);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        b bVarA = b.a();
        cVar.a(this.state);
        cVar.a(bVarA.a(this.totalBytes));
        cVar.a(bVarA.a(this.completeBytes));
        cVar.a(this.currentBytes);
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        b bVarA = b.a();
        if (bArr.length <= 0) {
            return 0;
        }
        this.state = bArr[0];
        if (bArr.length <= 2) {
            return 1;
        }
        this.totalBytes = bVarA.a(bArr, 1);
        if (bArr.length <= 4) {
            return 3;
        }
        this.completeBytes = bVarA.a(bArr, 3);
        if (bArr.length <= 5) {
            return 5;
        }
        this.currentBytes = bArr[5];
        return 6;
    }
}
