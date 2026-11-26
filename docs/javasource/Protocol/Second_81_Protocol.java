package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;
import com.huiyuan.util.StringHelper;

/* JADX INFO: loaded from: classes.dex */
public class Second_81_Protocol extends SecondProtocol {

    @j
    public String password;

    public Second_81_Protocol(c cVar) {
        super(cVar, g.Second_81);
    }

    @Override // b.b.a.a
    public byte[] a() {
        byte[] bArr = new byte[4];
        if (!StringHelper.isEmpty(this.password)) {
            byte[] bytes = this.password.getBytes();
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
            int length = bArr.length;
            this.password = new String(bArr);
            return length;
        }
        this.password = "";
        return 0;
    }
}
