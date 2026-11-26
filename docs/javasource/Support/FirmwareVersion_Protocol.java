package com.huiyuan.ble;

import b.b.a.a;
import b.b.a.c;
import b.b.d.j;
import com.huiyuan.util.StringHelper;

/* JADX INFO: loaded from: classes.dex */
public class FirmwareVersion_Protocol extends a {

    @j
    public String version;

    public FirmwareVersion_Protocol(c cVar) {
        super(cVar);
    }

    @Override // b.b.a.a
    public byte[] a() {
        return StringHelper.isEmpty(this.version) ? new byte[0] : this.version.getBytes();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        if (bArr.length > 0) {
            this.version = new String(bArr);
            return 0 + bArr.length;
        }
        this.version = "";
        return 0;
    }
}
