package com.huiyuan.ble;

import b.b.a.a;
import b.b.a.c;
import b.b.d.j;
import com.huiyuan.util.StringHelper;

/* JADX INFO: loaded from: classes.dex */
public class ManufacturerName_Protocol extends a {

    @j
    public String name;

    public ManufacturerName_Protocol(c cVar) {
        super(cVar);
    }

    @Override // b.b.a.a
    public byte[] a() {
        return StringHelper.isEmpty(this.name) ? new byte[0] : this.name.getBytes();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length > 0) {
            this.name = new String(bArr);
            return 0 + bArr.length;
        }
        this.name = "";
        return 0;
    }
}
