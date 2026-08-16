package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;
import com.huiyuan.util.StringHelper;

/* JADX INFO: loaded from: classes.dex */
public class Second_90_Protocol extends SecondProtocol {

    @j
    public String zoneName;

    public Second_90_Protocol(c cVar) {
        super(cVar, g.Second_90);
    }

    @Override // b.b.a.a
    public byte[] a() {
        byte[] bArr = new byte[20];
        if (!StringHelper.isEmpty(this.zoneName)) {
            byte[] bytes = this.zoneName.getBytes();
            int iMin = Math.min(bArr.length, bytes.length);
            for (int i = 0; i < iMin; i++) {
                bArr[i] = bytes[i];
            }
        }
        return bArr;
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr != null && bArr.length != 0) {
            b.b.d.c cVar = new b.b.d.c();
            int iMin = Math.min(bArr.length, 20);
            for (int i = 0; i < iMin && bArr[i] != 0; i++) {
                cVar.a(bArr[i]);
            }
            byte[] bArrA = cVar.a();
            int length = bArrA.length;
            this.zoneName = new String(bArrA);
            return length;
        }
        this.zoneName = "";
        return 0;
    }
}
