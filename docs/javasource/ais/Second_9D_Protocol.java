package com.huiyuan.ble.ais;

import b.b.a.c;
import b.b.a.m.g;
import b.b.d.b;
import b.b.d.j;
import com.huiyuan.util.DateHelper;
import java.util.Date;

/* JADX INFO: loaded from: classes.dex */
public class Second_9D_Protocol extends SecondProtocol {

    @j
    public String endTime;

    @j
    public String startTime;

    public Second_9D_Protocol(c cVar) {
        super(cVar, g.Second_9D);
    }

    @Override // b.b.a.a
    public byte[] a() {
        b.b.d.c cVar = new b.b.d.c();
        b bVarA = b.a();
        Date dateTime = DateHelper.parseDateTime(this.startTime);
        if (dateTime == null) {
            dateTime = new Date();
        }
        cVar.a(bVarA.a((short) DateHelper.extractYear(dateTime)));
        cVar.a((byte) dateTime.getMonth());
        cVar.a((byte) (dateTime.getDate() - 1));
        cVar.a((byte) dateTime.getHours());
        cVar.a((byte) dateTime.getMinutes());
        cVar.a((byte) dateTime.getSeconds());
        Date dateTime2 = DateHelper.parseDateTime(this.endTime);
        if (dateTime2 == null) {
            dateTime2 = new Date();
        }
        cVar.a(bVarA.a((short) DateHelper.extractYear(dateTime2)));
        cVar.a((byte) dateTime2.getMonth());
        cVar.a((byte) (dateTime2.getDate() - 1));
        cVar.a((byte) dateTime2.getHours());
        cVar.a((byte) dateTime2.getMinutes());
        cVar.a((byte) dateTime2.getSeconds());
        return cVar.a();
    }

    @Override // b.b.a.a
    public int a(byte[] bArr) {
        b bVarA = b.a();
        if (bArr.length <= 1) {
            return 0;
        }
        short sA = bVarA.a(bArr, 0);
        if (bArr.length <= 2) {
            return 2;
        }
        byte b2 = bArr[2];
        if (bArr.length <= 3) {
            return 3;
        }
        int i = bArr[3] + 1;
        if (bArr.length <= 4) {
            return 4;
        }
        byte b3 = bArr[4];
        if (bArr.length <= 5) {
            return 5;
        }
        byte b4 = bArr[5];
        if (bArr.length <= 6) {
            return 6;
        }
        byte b5 = bArr[6];
        if (bArr.length <= 8) {
            return 7;
        }
        short sA2 = bVarA.a(bArr, 7);
        if (bArr.length <= 9) {
            return 9;
        }
        byte b6 = bArr[9];
        if (bArr.length <= 10) {
            return 10;
        }
        int i2 = bArr[10] + 1;
        if (bArr.length <= 11) {
            return 11;
        }
        byte b7 = bArr[11];
        if (bArr.length <= 12) {
            return 12;
        }
        byte b8 = bArr[12];
        if (bArr.length <= 13) {
            return 13;
        }
        byte b9 = bArr[13];
        this.startTime = DateHelper.doFormatDate(DateHelper.toDate(sA, b2, i, b3, b4, b5), "yyyy-MM-dd HH:mm:ss");
        this.endTime = DateHelper.doFormatDate(DateHelper.toDate(sA2, b6, i2, b7, b8, b9), "yyyy-MM-dd HH:mm:ss");
        return 14;
    }
}
