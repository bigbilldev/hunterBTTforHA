package com.huiyuan.util;

import b.a.a.a.a;
import java.net.InetAddress;

/* JADX INFO: loaded from: classes.dex */
public class NetHelper {
    public static int bytesToInt(byte[] bArr) {
        return ((bArr[0] << 24) & (-16777216)) | (bArr[3] & 255) | ((bArr[2] << 8) & 65280) | ((bArr[1] << 16) & 16711680);
    }

    public static String bytesToIp(byte[] bArr) {
        StringBuffer stringBuffer = new StringBuffer();
        stringBuffer.append(bArr[0] & 255);
        stringBuffer.append('.');
        stringBuffer.append(bArr[1] & 255);
        stringBuffer.append('.');
        stringBuffer.append(bArr[2] & 255);
        stringBuffer.append('.');
        stringBuffer.append(bArr[3] & 255);
        return stringBuffer.toString();
    }

    public static String[] getIPAddrScope(String str) {
        int[] iPIntScope = getIPIntScope(str);
        return new String[]{intToIp(iPIntScope[0]), intToIp(iPIntScope[0])};
    }

    public static int[] getIPIntScope(String str) {
        String[] strArrSplit = str.split("/");
        if (strArrSplit.length != 2) {
            throw new IllegalArgumentException(a.a("invalid ipAndMask with: ", str));
        }
        int iIntValue = Integer.valueOf(strArrSplit[1].trim()).intValue();
        if (iIntValue < 0 || iIntValue > 31) {
            throw new IllegalArgumentException(a.a("invalid ipAndMask with: ", str));
        }
        int iIpToInt = ipToInt(strArrSplit[0]) & ((-1) << (32 - iIntValue));
        return new int[]{iIpToInt, iIpToInt + ((-1) >>> iIntValue)};
    }

    public static String[] getIPStrScope(String str, String str2) {
        int[] iPIntScope = getIPIntScope(str, str2);
        return new String[]{intToIp(iPIntScope[0]), intToIp(iPIntScope[0])};
    }

    public static byte[] intToBytes(int i) {
        return new byte[]{(byte) ((i >>> 24) & 255), (byte) ((i >>> 16) & 255), (byte) ((i >>> 8) & 255), (byte) (i & 255)};
    }

    public static String intToIp(int i) {
        StringBuilder sb = new StringBuilder();
        sb.append((i >> 24) & 255);
        sb.append('.');
        sb.append((i >> 16) & 255);
        sb.append('.');
        sb.append((i >> 8) & 255);
        sb.append('.');
        sb.append(i & 255);
        return sb.toString();
    }

    public static byte[] ipToBytesByInet(String str) {
        try {
            return InetAddress.getByName(str).getAddress();
        } catch (Exception unused) {
            throw new IllegalArgumentException(a.a(str, " is invalid IP"));
        }
    }

    public static byte[] ipToBytesByReg(String str) {
        byte[] bArr = new byte[4];
        try {
            String[] strArrSplit = str.split("\\.");
            bArr[0] = (byte) (Integer.parseInt(strArrSplit[0]) & 255);
            bArr[1] = (byte) (Integer.parseInt(strArrSplit[1]) & 255);
            bArr[2] = (byte) (Integer.parseInt(strArrSplit[2]) & 255);
            bArr[3] = (byte) (Integer.parseInt(strArrSplit[3]) & 255);
            return bArr;
        } catch (Exception unused) {
            throw new IllegalArgumentException(a.a(str, " is invalid IP"));
        }
    }

    public static int ipToInt(String str) {
        try {
            return bytesToInt(ipToBytesByInet(str));
        } catch (Exception unused) {
            throw new IllegalArgumentException(a.a(str, " is invalid IP"));
        }
    }

    public static String netintToIp(int i) {
        StringBuilder sb = new StringBuilder();
        sb.append(i & 255);
        sb.append('.');
        sb.append((i >> 8) & 255);
        sb.append('.');
        sb.append((i >> 16) & 255);
        sb.append('.');
        sb.append((i >> 24) & 255);
        return sb.toString();
    }

    public static int[] getIPIntScope(String str, String str2) {
        try {
            int iIpToInt = ipToInt(str);
            if (str2 != null && !"".equals(str2)) {
                int iIpToInt2 = ipToInt(str2);
                int i = iIpToInt & iIpToInt2;
                return new int[]{i, (ipToInt("255.255.255.255") - iIpToInt2) + i};
            }
            return new int[]{iIpToInt, iIpToInt};
        } catch (Exception unused) {
            throw new IllegalArgumentException("invalid ip scope express  ip:" + str + "  mask:" + str2);
        }
    }
}
