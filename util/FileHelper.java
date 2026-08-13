package com.huiyuan.util;

import android.content.ContentUris;
import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.DocumentsContract;
import android.provider.MediaStore;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;

/* JADX INFO: loaded from: classes.dex */
public class FileHelper {
    public static String a(Context context, Uri uri, String str, String[] strArr) {
        Cursor cursorQuery;
        String[] strArr2 = {org.apache.cordova.camera.FileHelper._DATA};
        try {
            cursorQuery = context.getContentResolver().query(uri, strArr2, str, strArr, null);
            if (cursorQuery == null) {
                return null;
            }
            try {
                if (cursorQuery.moveToFirst()) {
                    return cursorQuery.getString(cursorQuery.getColumnIndexOrThrow(strArr2[0]));
                }
                return null;
            } catch (Exception unused) {
                if (cursorQuery == null) {
                    return null;
                }
                cursorQuery.close();
                return null;
            }
        } catch (Exception unused2) {
            cursorQuery = null;
        }
    }

    public static void copyFile(String str, String str2) throws Throwable {
        copyFile(new File(str), new File(str2));
    }

    public static String getFilePathByUri(Context context, Uri uri) {
        String strA;
        Uri uri2 = null;
        if (!"content".equalsIgnoreCase(uri.getScheme())) {
            if ("file".equalsIgnoreCase(uri.getScheme())) {
                return uri.getPath();
            }
            return null;
        }
        if (Build.VERSION.SDK_INT < 19) {
            return a(context, uri, null, null);
        }
        if (!DocumentsContract.isDocumentUri(context, uri)) {
            if ("content".equalsIgnoreCase(uri.getScheme())) {
                return a(context, uri, null, null);
            }
            if ("file".equals(uri.getScheme())) {
                return uri.getPath();
            }
            return null;
        }
        String documentId = DocumentsContract.getDocumentId(uri);
        if ("com.android.providers.media.documents".equals(uri.getAuthority())) {
            String str = documentId.split(":")[0];
            String[] strArr = {documentId.split(":")[1]};
            if ("image".equals(str)) {
                uri2 = MediaStore.Images.Media.EXTERNAL_CONTENT_URI;
            } else if ("video".equals(str)) {
                uri2 = MediaStore.Video.Media.EXTERNAL_CONTENT_URI;
            } else if ("audio".equals(str)) {
                uri2 = MediaStore.Audio.Media.EXTERNAL_CONTENT_URI;
            }
            strA = a(context, uri2, "_id=?", strArr);
        } else if ("com.android.providers.downloads.documents".equals(uri.getAuthority())) {
            strA = a(context, ContentUris.withAppendedId(Uri.parse("content://downloads/public_downloads"), Long.valueOf(documentId).longValue()), null, null);
        } else {
            if (!"com.android.externalstorage.documents".equals(uri.getAuthority())) {
                return null;
            }
            String[] strArrSplit = DocumentsContract.getDocumentId(uri).split(":");
            if (!"primary".equalsIgnoreCase(strArrSplit[0])) {
                return null;
            }
            strA = Environment.getExternalStorageDirectory() + "/" + strArrSplit[1];
        }
        return strA;
    }

    public static void copyFile(File file, File file2) throws Throwable {
        FileInputStream fileInputStream;
        FileOutputStream fileOutputStream = null;
        try {
            fileInputStream = new FileInputStream(file);
            try {
                FileOutputStream fileOutputStream2 = new FileOutputStream(file2);
                try {
                    byte[] bArr = new byte[1024];
                    while (true) {
                        int i = fileInputStream.read(bArr);
                        if (i <= 0) {
                            fileInputStream.close();
                            fileOutputStream2.close();
                            return;
                        }
                        fileOutputStream2.write(bArr, 0, i);
                    }
                } catch (Throwable th) {
                    th = th;
                    fileOutputStream = fileOutputStream2;
                    if (fileInputStream != null) {
                        fileInputStream.close();
                    }
                    if (fileOutputStream != null) {
                        fileOutputStream.close();
                    }
                    throw th;
                }
            } catch (Throwable th2) {
                th = th2;
            }
        } catch (Throwable th3) {
            th = th3;
            fileInputStream = null;
        }
    }
}
