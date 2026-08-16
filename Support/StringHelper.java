package com.huiyuan.util;

import java.util.Random;

/* JADX INFO: loaded from: classes.dex */
public class StringHelper {
    public static String getRandomStr(int i) {
        Random random = new Random();
        StringBuffer stringBuffer = new StringBuffer();
        for (int i2 = 0; i2 < i; i2++) {
            stringBuffer.append("abcdefghijklmnopqrstuvwxyz0123456789".charAt(random.nextInt(36)));
        }
        return stringBuffer.toString();
    }

    public static boolean isEmpty(String str) {
        return str == null || str.length() < 1;
    }

    public static String padLeft(String str, int i, char c) {
        if (str == null) {
            str = "";
        }
        int length = str.length();
        if (length < i) {
            for (int i2 = 0; i2 < i - length; i2++) {
                str = c + str;
            }
        }
        return str;
    }

    public static byte[] toByteArray(String str) {
        if (isEmpty(str)) {
            throw new IllegalArgumentException("this hexString must not be empty");
        }
        String lowerCase = str.toLowerCase();
        byte[] bArr = new byte[lowerCase.length() / 2];
        for (int i = 0; i < bArr.length; i++) {
            int i2 = i * 2;
            bArr[i] = Integer.valueOf(lowerCase.substring(i2, i2 + 2), 16).byteValue();
        }
        return bArr;
    }

    public static String toHexString(byte[] bArr, String str) {
        if (bArr == null || bArr.length < 1) {
            return "";
        }
        StringBuilder sb = new StringBuilder();
        boolean zIsEmpty = isEmpty(str);
        for (int i = 0; i < bArr.length; i++) {
            sb.append(String.format("%02X", Byte.valueOf(bArr[i])));
            if (!zIsEmpty && i < bArr.length - 1) {
                sb.append(str);
            }
        }
        return sb.toString();
    }

    public static String toHexString(byte[] bArr) {
        return toHexString(bArr, "");
    }
}
