package com.huiyuan.util;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.Uri;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.BatteryManager;
import android.os.Build;
import android.provider.Settings;
import android.util.Base64;
import android.view.View;
import b.b.d.a;
import b.b.d.k;
import b.b.d.n;
import b.b.d.s;
import b.b.d.u;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Method;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;
import org.apache.cordova.filetransfer.FileTransfer;

/* JADX INFO: loaded from: classes.dex */
public class UtilHelper {

    /* JADX INFO: renamed from: com.huiyuan.util.UtilHelper$1, reason: invalid class name */
    public static /* synthetic */ class AnonymousClass1 {

        /* JADX INFO: renamed from: a, reason: collision with root package name */
        public static final /* synthetic */ int[] f876a = new int[s.values().length];

        static {
            try {
                f876a[s.ppLeftTop.ordinal()] = 1;
            } catch (NoSuchFieldError unused) {
            }
            try {
                f876a[s.ppRightTop.ordinal()] = 2;
            } catch (NoSuchFieldError unused2) {
            }
            try {
                f876a[s.ppLeftBottom.ordinal()] = 3;
            } catch (NoSuchFieldError unused3) {
            }
            try {
                f876a[s.ppRightBottom.ordinal()] = 4;
            } catch (NoSuchFieldError unused4) {
            }
        }
    }

    public static int byteArrayToInt(byte[] bArr, int i) {
        int i2 = 0;
        for (int i3 = 0; i3 < 4; i3++) {
            i2 += (bArr[i3 + i] & 255) << ((3 - i3) * 8);
        }
        return i2;
    }

    public static String composePath(String str, String str2) {
        return composePath(str, str2, null);
    }

    public static String copyAssetsFile(Activity activity, String str, boolean z) {
        Matcher matcher = Pattern.compile("^.*?[\\/]{0,1}([^\\/]+?)$", 2).matcher(str);
        if (!matcher.find()) {
            return null;
        }
        try {
            File file = new File(activity.getCacheDir().getParent(), matcher.group(1));
            if (z || !file.exists()) {
                if (file.exists()) {
                    file.delete();
                }
                InputStream inputStreamOpen = activity.getResources().getAssets().open(str);
                FileOutputStream fileOutputStream = new FileOutputStream(file);
                byte[] bArr = new byte[1024];
                while (true) {
                    int i = inputStreamOpen.read(bArr);
                    if (i == -1) {
                        break;
                    }
                    fileOutputStream.write(bArr, 0, i);
                }
                fileOutputStream.flush();
                fileOutputStream.close();
                inputStreamOpen.close();
            }
            return file.getAbsolutePath();
        } catch (IOException unused) {
            return null;
        }
    }

    public static int dip2px(Context context, float f) {
        return (int) ((f * context.getResources().getDisplayMetrics().density) + 0.5f);
    }

    public static int fibonacci(int i) {
        if (i < 0 || i == 0) {
            return 0;
        }
        if (i == 1) {
            return 1;
        }
        return fibonacci(i - 2) + fibonacci(i - 1);
    }

    public static void fullScreen(Activity activity) {
        int i = Build.VERSION.SDK_INT;
        if (i < 19) {
            activity.getWindow().getDecorView().setSystemUiVisibility(8);
        } else if (i >= 19) {
            activity.getWindow().getDecorView().setSystemUiVisibility(7943);
        }
    }

    public static String getAppName(Context context) {
        try {
            return (String) context.getPackageManager().getApplicationLabel(context.getApplicationInfo());
        } catch (Exception unused) {
            return context.getPackageName();
        }
    }

    public static String getAppVersion(Context context) {
        PackageInfo packageInfo;
        try {
            packageInfo = context.getPackageManager().getPackageInfo(context.getPackageName(), FileTransfer.MAX_BUFFER_SIZE);
        } catch (Exception e) {
            e.printStackTrace();
            packageInfo = null;
        }
        return packageInfo.versionName;
    }

    public static int getBatteryValue(Context context) {
        BatteryManager batteryManager = (BatteryManager) context.getSystemService("batterymanager");
        if (Build.VERSION.SDK_INT >= 21) {
            return batteryManager.getIntProperty(4);
        }
        return 0;
    }

    /* JADX WARN: Removed duplicated region for block: B:15:0x004a  */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct code enable 'Show inconsistent code' option in preferences
    */
    public static java.lang.String getDBDir(android.content.Context r2, boolean r3, boolean r4, boolean r5) {
        /*
            r0 = 0
            if (r4 == 0) goto L10
            java.lang.String r3 = android.os.Environment.DIRECTORY_PICTURES
            java.io.File r3 = android.os.Environment.getExternalStoragePublicDirectory(r3)
            if (r3 == 0) goto L4a
            java.lang.String r3 = r3.getAbsolutePath()
            goto L4b
        L10:
            java.lang.String r4 = android.os.Environment.getExternalStorageState()
            java.lang.String r1 = "mounted"
            boolean r4 = r1.equals(r4)
            if (r4 == 0) goto L4a
            if (r3 == 0) goto L3d
            java.lang.StringBuilder r3 = new java.lang.StringBuilder
            r3.<init>()
            java.io.File r4 = android.os.Environment.getExternalStorageDirectory()
            java.lang.String r4 = r4.getAbsolutePath()
            r3.append(r4)
            java.lang.String r4 = java.io.File.separator
            r3.append(r4)
            java.lang.String r4 = "db"
            r3.append(r4)
            java.lang.String r3 = r3.toString()
            goto L4b
        L3d:
            if (r2 == 0) goto L4a
            java.io.File r3 = r2.getExternalCacheDir()
            if (r3 == 0) goto L4a
            java.lang.String r3 = r3.getAbsolutePath()
            goto L4b
        L4a:
            r3 = r0
        L4b:
            if (r3 != 0) goto L5f
            if (r2 == 0) goto L5f
            java.io.File r2 = r2.getCacheDir()
            if (r2 == 0) goto L5f
            boolean r4 = r2.exists()
            if (r4 == 0) goto L5f
            java.lang.String r3 = r2.getAbsolutePath()
        L5f:
            if (r3 != 0) goto L62
            return r0
        L62:
            java.io.File r2 = new java.io.File
            r2.<init>(r3)
            boolean r3 = r2.exists()
            if (r3 != 0) goto L76
            if (r5 == 0) goto L76
            boolean r3 = r2.mkdirs()
            if (r3 != 0) goto L76
            return r0
        L76:
            java.lang.String r2 = r2.getAbsolutePath()
            return r2
        */
        throw new UnsupportedOperationException("Method not decompiled: com.huiyuan.util.UtilHelper.getDBDir(android.content.Context, boolean, boolean, boolean):java.lang.String");
    }

    public static String getDeviceBrand() {
        return Build.BRAND;
    }

    public static int getDeviceHeight(Context context) {
        return context.getResources().getDisplayMetrics().heightPixels;
    }

    public static int getDeviceWidth(Context context) {
        return context.getResources().getDisplayMetrics().widthPixels;
    }

    public static String getLocalIp(Context context) {
        NetworkInfo activeNetworkInfo = ((ConnectivityManager) context.getSystemService("connectivity")).getActiveNetworkInfo();
        if (activeNetworkInfo == null || !activeNetworkInfo.isConnected()) {
            return null;
        }
        if (activeNetworkInfo.getType() != 0) {
            if (activeNetworkInfo.getType() == 1) {
                return NetHelper.netintToIp(((WifiManager) context.getSystemService("wifi")).getConnectionInfo().getIpAddress());
            }
            return null;
        }
        try {
            Enumeration<NetworkInterface> networkInterfaces = NetworkInterface.getNetworkInterfaces();
            while (networkInterfaces.hasMoreElements()) {
                Enumeration<InetAddress> inetAddresses = networkInterfaces.nextElement().getInetAddresses();
                while (inetAddresses.hasMoreElements()) {
                    InetAddress inetAddressNextElement = inetAddresses.nextElement();
                    if (!inetAddressNextElement.isLoopbackAddress() && (inetAddressNextElement instanceof Inet4Address)) {
                        return inetAddressNextElement.getHostAddress();
                    }
                }
            }
            return null;
        } catch (SocketException e) {
            e.printStackTrace();
            return null;
        }
    }

    /* JADX WARN: Removed duplicated region for block: B:40:0x00f7  */
    /* JADX WARN: Removed duplicated region for block: B:50:0x013f  */
    /* JADX WARN: Removed duplicated region for block: B:58:0x01a0  */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct code enable 'Show inconsistent code' option in preferences
    */
    public static java.lang.String getSnapshot(android.app.Activity r17, java.lang.String r18, b.b.d.s r19, boolean r20, boolean r21) {
        /*
            Method dump skipped, instruction units count: 494
            To view this dump change 'Code comments level' option to 'DEBUG'
        */
        throw new UnsupportedOperationException("Method not decompiled: com.huiyuan.util.UtilHelper.getSnapshot(android.app.Activity, java.lang.String, b.b.d.s, boolean, boolean):java.lang.String");
    }

    public static String getSysLanguage(Context context) {
        return context.getResources().getConfiguration().locale.toString();
    }

    public static String getSystemModel() {
        return Build.MODEL;
    }

    public static String getSystemVersion() {
        return Build.VERSION.RELEASE;
    }

    public static int getWifiValue(Context context) throws u {
        WifiInfo connectionInfo;
        if (!isWifiConnect(context) || (connectionInfo = ((WifiManager) context.getSystemService("wifi")).getConnectionInfo()) == null) {
            throw new u("wifi未连接");
        }
        int rssi = connectionInfo.getRssi();
        if ((rssi <= -50 || rssi >= 0) && ((rssi <= -70 || rssi >= -50) && (rssi <= -80 || rssi >= -70))) {
        }
        return rssi;
    }

    public static byte[] intToByteArray(int i) {
        int iNumberOfLeadingZeros = (40 - Integer.numberOfLeadingZeros(i < 0 ? i ^ (-1) : i)) / 8;
        byte[] bArr = new byte[4];
        for (int i2 = 0; i2 < iNumberOfLeadingZeros; i2++) {
            bArr[3 - i2] = (byte) (i >>> (i2 * 8));
        }
        return bArr;
    }

    public static boolean is24HourFormat(Context context) {
        String string = Settings.System.getString(context.getContentResolver(), "time_12_24");
        if (string == null) {
            DateFormat timeInstance = DateFormat.getTimeInstance(1, context.getResources().getConfiguration().locale);
            string = (!(timeInstance instanceof SimpleDateFormat) || ((SimpleDateFormat) timeInstance).toPattern().indexOf(72) < 0) ? "12" : "24";
        }
        return string.equals("24");
    }

    public static Boolean isMobileDataEnabled(Context context) {
        ConnectivityManager connectivityManager = (ConnectivityManager) context.getSystemService("connectivity");
        try {
            Method declaredMethod = Class.forName(connectivityManager.getClass().getName()).getDeclaredMethod("getMobileDataEnabled", new Class[0]);
            declaredMethod.setAccessible(true);
            return (Boolean) declaredMethod.invoke(connectivityManager, new Object[0]);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public static boolean isWifiConnect(Context context) {
        NetworkInfo networkInfo = ((ConnectivityManager) context.getSystemService("connectivity")).getNetworkInfo(1);
        if (networkInfo == null) {
            return false;
        }
        return networkInfo.isConnected();
    }

    public static String join(String str, String[] strArr) {
        StringBuffer stringBuffer = new StringBuffer();
        int length = strArr.length;
        for (int i = 0; i < length; i++) {
            if (i == length - 1) {
                stringBuffer.append(strArr[i]);
            } else {
                stringBuffer.append(strArr[i]);
                stringBuffer.append(str);
            }
        }
        return stringBuffer.toString();
    }

    public static void keepScreenLight(Activity activity) {
        activity.getWindow().addFlags(128);
    }

    public static void openUrl(Activity activity, String str) throws u {
        if (StringHelper.isEmpty(str)) {
            throw new u("url为空!");
        }
        Matcher matcher = Pattern.compile("^(https{0,1})(://.*)$", 2).matcher(str);
        if (!matcher.find()) {
            throw new u("非法的url!");
        }
        activity.startActivity(new Intent("android.intent.action.VIEW", Uri.parse(matcher.group(1).toLowerCase() + matcher.group(2))));
    }

    public static int px2dip(Context context, float f) {
        return (int) ((f / context.getResources().getDisplayMetrics().density) + 0.5f);
    }

    public static void sendMail(Activity activity, String str, String str2, String str3, String... strArr) throws u {
        if (StringHelper.isEmpty(str3)) {
            throw new u("email为空!");
        }
        if (!Pattern.compile("^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\\.[a-zA-Z0-9_-]+)+$", 2).matcher(str3).matches()) {
            throw new u("非法的email!");
        }
        Intent intent = new Intent("android.intent.action.SEND", Uri.parse("mailto:" + str3));
        intent.setType("message/rfc822");
        intent.putExtra("android.intent.extra.EMAIL", new String[]{str3});
        intent.putExtra("android.intent.extra.CC", strArr);
        intent.putExtra("android.intent.extra.SUBJECT", str);
        intent.putExtra("android.intent.extra.TEXT", str2);
        activity.startActivity(Intent.createChooser(intent, "请选择邮件类应用"));
    }

    public static void shareUrl(Activity activity, String str, String str2) throws u {
        if (StringHelper.isEmpty(str)) {
            throw new u("url为空!");
        }
        Intent intent = new Intent();
        intent.setAction("android.intent.action.SEND");
        intent.setType("text/plain");
        intent.putExtra("android.intent.extra.SUBJECT", str2);
        intent.putExtra("android.intent.extra.TEXT", str);
        activity.startActivity(Intent.createChooser(intent, "请选择分享应用"));
    }

    public static void startMonitorKeyboardState(Activity activity, a<Boolean> aVar) {
        View decorView = activity.getWindow().getDecorView();
        decorView.getViewTreeObserver().addOnGlobalLayoutListener(new k(decorView, aVar));
    }

    public static byte[] subBytes(byte[] bArr, int i, int i2) {
        if (i < 0) {
            i = 0;
        }
        if (bArr == null || bArr.length <= 0 || i >= bArr.length || i2 <= 0) {
            return null;
        }
        if (i + i2 > bArr.length) {
            i2 = bArr.length - i;
        }
        byte[] bArr2 = new byte[i2];
        System.arraycopy(bArr, i, bArr2, 0, i2);
        return bArr2;
    }

    public static int toHash(String str) {
        int iCharAt = 0;
        for (int i = 0; i < str.length(); i++) {
            iCharAt = ((iCharAt << 5) + (str.charAt(i) - '`')) % 11113;
        }
        return iCharAt;
    }

    public static List<String> unzipImageData(String str, boolean z) {
        GZIPInputStream gZIPInputStream;
        int iByteArrayToInt;
        ArrayList arrayList = new ArrayList();
        if (str != null && str.length() > 0) {
            try {
                byte[] bArrDecode = Base64.decode(str, 0);
                if (bArrDecode == null || bArrDecode.length <= 0) {
                    gZIPInputStream = null;
                } else {
                    ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
                    gZIPInputStream = new GZIPInputStream(new ByteArrayInputStream(bArrDecode));
                    byte[] bArr = new byte[256];
                    while (true) {
                        int i = gZIPInputStream.read(bArr);
                        if (i < 0) {
                            break;
                        }
                        byteArrayOutputStream.write(bArr, 0, i);
                    }
                    byte[] bArr2 = {0, 0, 0, 0};
                    ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(byteArrayOutputStream.toByteArray());
                    while (byteArrayInputStream.read(bArr2, 0, bArr2.length) >= 0 && (iByteArrayToInt = byteArrayToInt(bArr2, 0)) >= 0) {
                        byte[] bArr3 = new byte[iByteArrayToInt];
                        byteArrayInputStream.read(bArr3, 0, iByteArrayToInt);
                        if (z) {
                            arrayList.add(Base64.encodeToString(bArr3, 0));
                        } else {
                            arrayList.add(new String(bArr3));
                        }
                    }
                }
                gZIPInputStream.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        return arrayList;
    }

    public static byte xorValue(byte[] bArr) {
        if (bArr == null) {
            return (byte) 0;
        }
        byte b2 = 0;
        for (byte b3 : bArr) {
            b2 = (byte) (b2 ^ b3);
        }
        return b2;
    }

    public static String zipImageData(List<String> list, boolean z) {
        if (list != null && list.size() > 0) {
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            try {
                GZIPOutputStream gZIPOutputStream = new GZIPOutputStream(byteArrayOutputStream);
                for (int i = 0; i < list.size(); i++) {
                    String str = list.get(i);
                    if (str != null && str.length() > 0) {
                        byte[] bArrDecode = z ? Base64.decode(str, 0) : str.getBytes("UTF-8");
                        if (bArrDecode != null && bArrDecode.length > 0) {
                            byte[] bArrIntToByteArray = intToByteArray(bArrDecode.length);
                            gZIPOutputStream.write(bArrIntToByteArray, 0, bArrIntToByteArray.length);
                            gZIPOutputStream.write(bArrDecode);
                        }
                    }
                }
                gZIPOutputStream.close();
                return Base64.encodeToString(byteArrayOutputStream.toByteArray(), 0);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        return null;
    }

    public static String composePath(String str, String str2, String str3) {
        if (StringHelper.isEmpty(str)) {
            return str2;
        }
        if (StringHelper.isEmpty(str2)) {
            return str;
        }
        if (StringHelper.isEmpty(str3)) {
            str3 = File.separator;
        }
        Object[] objArr = new Object[3];
        objArr[0] = str;
        if (str.endsWith(str3) || str2.startsWith(str3)) {
            str3 = "";
        }
        objArr[1] = str3;
        objArr[2] = str2;
        return String.format("%s%s%s", objArr);
    }

    public static String join(String str, List<Map> list, String str2) {
        ArrayList arrayList = new ArrayList();
        Iterator<Map> it = list.iterator();
        while (it.hasNext()) {
            arrayList.add(n.a(it.next().get(str2)));
        }
        return join(str, arrayList);
    }

    public static String join(String str, List<String> list) {
        StringBuffer stringBuffer = new StringBuffer();
        int size = list.size();
        for (int i = 0; i < size; i++) {
            if (i == size - 1) {
                stringBuffer.append(list.get(i));
            } else {
                stringBuffer.append(list.get(i));
                stringBuffer.append(str);
            }
        }
        return stringBuffer.toString();
    }

    public static String copyAssetsFile(Activity activity, String str) {
        return copyAssetsFile(activity, str, false);
    }

    public static String getSnapshot(Activity activity, String str) {
        return getSnapshot(activity, str, s.ppLeftBottom, true, true);
    }

    public static String getSnapshot(Activity activity) {
        return getSnapshot(activity, null, s.ppCenterCenter, false, false);
    }
}
