package com.huiyuan.ble.ais;

import b.b.a.a;
import b.b.a.c;
import b.b.a.m.g;
import b.b.d.j;

/* JADX INFO: loaded from: classes.dex */
public abstract class AisProtocol extends a {

    @j
    public g protocolType;

    public AisProtocol(c cVar, g gVar) {
        super(cVar);
        this.protocolType = gVar;
    }

    public g d() {
        return this.protocolType;
    }
}
