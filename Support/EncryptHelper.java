package com.huiyuan.util;

import java.io.UnsupportedEncodingException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Date;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/* JADX INFO: loaded from: classes.dex */
public class EncryptHelper {
    public static String DesDecrypt(String str, String str2) {
        if (StringHelper.isEmpty(str)) {
            return "";
        }
        try {
            byte[] byteArray = StringHelper.toByteArray(str);
            if (byteArray == null || byteArray.length <= 0) {
                return "";
            }
            String strPadLeft = StringHelper.padLeft(StringHelper.toHexString(MessageDigest.getInstance("MD5").digest(str2.getBytes())), 32, '0');
            String strSubstring = strPadLeft.substring(0, 24);
            String strSubstring2 = strPadLeft.substring(24);
            SecretKeySpec secretKeySpec = new SecretKeySpec(strSubstring.getBytes(), "DESede");
            IvParameterSpec ivParameterSpec = new IvParameterSpec(strSubstring2.getBytes());
            Cipher cipher = Cipher.getInstance("DESede/CBC/PKCS5Padding");
            cipher.init(2, secretKeySpec, ivParameterSpec);
            return new String(cipher.doFinal(byteArray));
        } catch (Exception e) {
            e.printStackTrace();
            return "";
        }
    }

    public static String generateToken(String str, String str2) {
        try {
            String str3 = String.format("%s-%s-%s", StringHelper.getRandomStr(5), str, String.valueOf(new Date().getTime() / 1000));
            String strPadLeft = StringHelper.padLeft(StringHelper.toHexString(MessageDigest.getInstance("MD5").digest(str2.getBytes())), 32, '0');
            String strSubstring = strPadLeft.substring(0, 24);
            String strSubstring2 = strPadLeft.substring(24);
            SecretKeySpec secretKeySpec = new SecretKeySpec(strSubstring.getBytes(), "DESede");
            IvParameterSpec ivParameterSpec = new IvParameterSpec(strSubstring2.getBytes());
            Cipher cipher = Cipher.getInstance("DESede/CBC/PKCS5Padding");
            cipher.init(1, secretKeySpec, ivParameterSpec);
            return StringHelper.toHexString(cipher.doFinal(str3.getBytes("UTF-8")));
        } catch (Exception unused) {
            return "";
        }
    }

    public static long getHashCode(String str) {
        byte[] bytes = str.getBytes();
        long j = 0;
        for (int length = bytes.length; length > 0; length--) {
            j = (j * 131) + ((long) bytes[bytes.length - length]);
        }
        return j & Long.MAX_VALUE;
    }

    public static String md5(String str) {
        try {
            byte[] bArrDigest = MessageDigest.getInstance("MD5").digest(str.getBytes("UTF-8"));
            StringBuilder sb = new StringBuilder(bArrDigest.length * 2);
            for (byte b2 : bArrDigest) {
                int i = b2 & 255;
                if (i < 16) {
                    sb.append("0");
                }
                sb.append(Integer.toHexString(i));
            }
            return sb.toString();
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException("Huh, UTF-8 should be supported?", e);
        } catch (NoSuchAlgorithmException e2) {
            throw new RuntimeException("Huh, MD5 should be supported?", e2);
        }
    }
}
