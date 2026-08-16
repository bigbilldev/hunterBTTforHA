package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;
import com.huiyuan.util.StringHelper;

/* JADX INFO: loaded from: classes.dex */
public class First_C1_Protocol extends FirstProtocol {

    @j
    public String password;

    public First_C1_Protocol(c cVar) {
        super(cVar, g.First_c1, (byte) 81);
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public int b(byte[] bArr) {
        if (bArr == null || bArr.length == 0) {
            this.password = "";
            return 0;
        }
        int length = bArr.length;
        this.password = new String(bArr);
        return length;
    }

    @Override // com.huiyuan.ble.ais.FirstProtocol
    public byte[] e() {
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
}
