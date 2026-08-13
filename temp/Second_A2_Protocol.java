package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.b;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public class Second_A2_Protocol extends SecondProtocol {

    @j
    public int totalRecords;

    public Second_A2_Protocol(c cVar) {
        super(cVar, g.Second_A2);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        cVar.a(b.a().a(this.totalRecords));
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length <= 3) {
            return 0;
        }
        b bVarA = b.a();
        this.totalRecords = bVarA.a(bVarA.a(bArr, 0, 4));
        return 4;
    }
}
