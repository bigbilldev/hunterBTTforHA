package com.huiyuan.util;

import android.content.Context;
import b.a.a.a.a;
import dalvik.system.DexFile;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/* JADX INFO: loaded from: classes.dex */
public class ClassHelper {

    public interface InFilteResult {
        boolean check(String str);
    }

    public interface OutFilteResult {
        boolean check(String str, Class cls);
    }

    public static List<String> getClassNamesByPackageName(Context context, String str) {
        final String strA = a.a(str, ".");
        return getClassNamesInPackage(context, new InFilteResult() { // from class: com.huiyuan.util.ClassHelper.3
            @Override // com.huiyuan.util.ClassHelper.InFilteResult
            public boolean check(String str2) {
                return str2.startsWith(strA);
            }
        });
    }

    public static List<String> getClassNamesInPackage(Context context, InFilteResult inFilteResult) {
        ArrayList arrayList = new ArrayList();
        try {
            Enumeration<String> enumerationEntries = new DexFile(context.getPackageCodePath()).entries();
            while (enumerationEntries.hasMoreElements()) {
                String strNextElement = enumerationEntries.nextElement();
                if (!arrayList.contains(strNextElement) && (inFilteResult == null || inFilteResult.check(strNextElement))) {
                    arrayList.add(strNextElement);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return arrayList;
    }

    public static HashMap<String, Class> getClassesByPackageName(Context context, String str) {
        final String strA = a.a(str, ".");
        return getClassesInPackage(context, new InFilteResult() { // from class: com.huiyuan.util.ClassHelper.2
            @Override // com.huiyuan.util.ClassHelper.InFilteResult
            public boolean check(String str2) {
                return str2.startsWith(strA);
            }
        }, null);
    }

    public static HashMap<String, Class> getClassesInPackage(Context context, InFilteResult inFilteResult, OutFilteResult outFilteResult) {
        HashMap<String, Class> map = new HashMap<>();
        String packageCodePath = null;
        try {
            if (context == null) {
                Matcher matcher = Pattern.compile("\"(.*?\\.apk)\"", 2).matcher(ClassHelper.class.getClassLoader().toString());
                if (matcher.find()) {
                    packageCodePath = matcher.group(1);
                }
            } else {
                packageCodePath = context.getPackageCodePath();
            }
            if (!StringHelper.isEmpty(packageCodePath)) {
                Enumeration<String> enumerationEntries = new DexFile(packageCodePath).entries();
                while (enumerationEntries.hasMoreElements()) {
                    String strNextElement = enumerationEntries.nextElement();
                    if (!strNextElement.startsWith("android.") && !strNextElement.startsWith("androidx.") && !map.containsKey(strNextElement) && (inFilteResult == null || inFilteResult.check(strNextElement))) {
                        try {
                            Class<?> cls = Class.forName(strNextElement);
                            if (cls != null && (outFilteResult == null || outFilteResult.check(strNextElement, cls))) {
                                map.put(strNextElement, cls);
                            }
                        } catch (ClassNotFoundException e) {
                            e.printStackTrace();
                        }
                    }
                }
            }
        } catch (Exception e2) {
            e2.printStackTrace();
        }
        return map;
    }

    public static HashMap<String, Class> getInstantiableClassesInPackage(Context context, InFilteResult inFilteResult, final Class cls) {
        return getClassesInPackage(context, inFilteResult, new OutFilteResult() { // from class: com.huiyuan.util.ClassHelper.1
            @Override // com.huiyuan.util.ClassHelper.OutFilteResult
            public boolean check(String str, Class cls2) {
                if (!cls.isAssignableFrom(cls2) || Modifier.isAbstract(cls2.getModifiers())) {
                    return false;
                }
                try {
                    return cls2.newInstance() != null;
                } catch (Exception unused) {
                    return false;
                }
            }
        });
    }
}
