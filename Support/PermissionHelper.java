package com.huiyuan.util;

import android.content.Context;
import android.content.Intent;
import android.os.Build;
import b.a.a.a.a;
import b.b.d.o;
import b.b.d.p;
import com.gun0912.tedpermission.TedPermissionActivity;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;

/* JADX INFO: loaded from: classes.dex */
public class PermissionHelper {

    /* JADX INFO: renamed from: a, reason: collision with root package name */
    public Context f872a;

    /* JADX INFO: renamed from: b, reason: collision with root package name */
    public p f873b;
    public o c;

    public PermissionHelper(Context context, o oVar) {
        this.f872a = context;
        this.c = oVar;
    }

    public static boolean hasPermission(Context context, String str) {
        try {
            return ((Integer) context.getClass().getDeclaredMethod("checkSelfPermission", String.class).invoke(context, str)).intValue() == 0;
        } catch (IllegalAccessException unused) {
            a.b("IllegalAccessException when checking permission ", str);
            return false;
        } catch (NoSuchMethodException unused2) {
            a.b("No need to check for permission ", str);
            return true;
        } catch (InvocationTargetException unused3) {
            a.b("invocationTargetException when checking permission ", str);
            return false;
        }
    }

    public static boolean hasPermissions(Context context, o oVar, String str) {
        if (oVar.a(str) > -1) {
            return hasPermissions(context, oVar.b(str));
        }
        return false;
    }

    public static void requestPermission(Context context, int i, String str) {
        requestPermissions(context, i, new String[]{str});
    }

    public static void requestPermissions(Context context, int i, String[] strArr) {
        try {
            Class<?> cls = context.getClass();
            cls.getDeclaredMethod("requestPermissions", cls, Integer.TYPE, String[].class).invoke(context, Integer.valueOf(i), strArr);
        } catch (IllegalAccessException unused) {
            StringBuilder sbA = a.a("IllegalAccessException when requesting permissions ");
            sbA.append(Arrays.toString(strArr));
            sbA.toString();
        } catch (NoSuchMethodException unused2) {
            StringBuilder sbA2 = a.a("No need to request permissions ");
            sbA2.append(Arrays.toString(strArr));
            sbA2.toString();
            int[] iArr = new int[strArr.length];
            Arrays.fill(iArr, 0);
            try {
                context.getClass().getDeclaredMethod("onRequestPermissionsResult", Integer.TYPE, String[].class, int[].class).invoke(context, Integer.valueOf(i), strArr, iArr);
            } catch (IllegalAccessException | NoSuchMethodException | InvocationTargetException unused3) {
            }
        } catch (InvocationTargetException unused4) {
            StringBuilder sbA3 = a.a("invocationTargetException when requesting permissions ");
            sbA3.append(Arrays.toString(strArr));
            sbA3.toString();
        }
    }

    public void check(String str) {
        o oVar = this.c;
        if (oVar == null) {
            throw new NullPointerException("config");
        }
        String[] strArrB = oVar.b(str);
        if (strArrB == null || strArrB.length < 1) {
            throw new IllegalArgumentException(TedPermissionActivity.EXTRA_PERMISSIONS);
        }
        int iA = this.c.a(str);
        if (iA < 0) {
            throw new IllegalArgumentException("request code");
        }
        p pVar = this.f873b;
        if (pVar == null) {
            throw new NullPointerException("You must setPermissionListener() on TedPermission");
        }
        if (Build.VERSION.SDK_INT < 23) {
            pVar.onPermissionGranted(str);
            return;
        }
        if (this.c.c(str)) {
            this.f873b.onPermissionGranted(str);
            return;
        }
        Intent intent = new Intent(this.f872a, (Class<?>) PermissionActivity.class);
        intent.putExtra("func", str);
        intent.putExtra(TedPermissionActivity.EXTRA_PERMISSIONS, strArrB);
        intent.putExtra("requestCode", iA);
        intent.addFlags(268435456);
        intent.addFlags(262144);
        PermissionActivity.a(this.f872a, intent, this.f873b);
    }

    public PermissionHelper setPermissionHandler(final p pVar) {
        this.f873b = new p() { // from class: com.huiyuan.util.PermissionHelper.1
            @Override // b.b.d.p
            public void onPermissionDenied(String str, ArrayList<String> arrayList) {
                pVar.onPermissionDenied(str, arrayList);
            }

            @Override // b.b.d.p
            public void onPermissionGranted(String str) {
                PermissionHelper.this.c.d(str);
                pVar.onPermissionGranted(str);
            }
        };
        return this;
    }

    public static boolean hasPermissions(Context context, String[] strArr) {
        String str = null;
        try {
            Method declaredMethod = context.getClass().getDeclaredMethod("hasPermission", String.class);
            Boolean boolValueOf = Boolean.valueOf(strArr.length > 0);
            for (int i = 0; i < strArr.length; i++) {
                str = strArr[i];
                boolValueOf = Boolean.valueOf(boolValueOf.booleanValue() && ((Boolean) declaredMethod.invoke(context, str)).booleanValue());
                if (!boolValueOf.booleanValue()) {
                    break;
                }
            }
            return boolValueOf.booleanValue();
        } catch (IllegalAccessException unused) {
            a.b("IllegalAccessException when checking permission ", str);
            return false;
        } catch (NoSuchMethodException unused2) {
            a.b("No need to check for permission ", str);
            return true;
        } catch (InvocationTargetException unused3) {
            a.b("invocationTargetException when checking permission ", str);
            return false;
        }
    }

    public static void requestPermissions(Context context, o oVar, String str) {
        int iA = oVar.a(str);
        if (iA > -1) {
            requestPermissions(context, iA, oVar.b(str));
            String str2 = "找到功能项：" + str;
        }
    }
}
