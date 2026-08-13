package com.huiyuan.util;

import android.database.Cursor;
import android.util.Base64;
import b.b.d.a;
import b.b.d.f;
import b.b.d.j;
import java.lang.reflect.Array;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.sql.Connection;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

/* JADX INFO: loaded from: classes.dex */
public class JsonHelper {
    public static void doCallback(f fVar, Object obj, boolean z) {
        String string;
        JSONObject json2;
        JSONObject jSONObject = null;
        if (obj != null) {
            if (obj instanceof JSONObject) {
                json2 = (JSONObject) obj;
            } else if (obj instanceof String) {
                string = (String) obj;
                try {
                    jSONObject = (JSONObject) new JSONTokener(string).nextValue();
                } catch (Exception unused) {
                }
            } else {
                try {
                    json2 = toJson2(obj, true, true, null);
                } catch (Exception unused2) {
                    string = obj.toString();
                }
            }
            jSONObject = json2;
            string = null;
        } else {
            string = null;
        }
        if (jSONObject == null) {
            if (z) {
                fVar.success(string);
                return;
            } else {
                fVar.error(string);
                return;
            }
        }
        if (!z) {
            fVar.error(jSONObject);
            return;
        }
        try {
            fVar.success(jSONObject);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public static <T> T fromJson(String str, boolean z, Class<T> cls) {
        return (T) fromJson(str, z, false, (Class) cls);
    }

    public static Object fromJsonToFieldValue(String str, String str2, boolean z, boolean z2, Class<?> cls) {
        if (str == null || str.equals("")) {
            throw new NullPointerException("JsonString can't be null");
        }
        if (str2 == null || str2.equals("")) {
            throw new NullPointerException("fieldName can't be null");
        }
        JSONObject jSONObject = (JSONObject) new JSONTokener(str).nextValue();
        while (!cls.equals(Object.class)) {
            for (Field field : cls.getDeclaredFields()) {
                if (((z && ((j) field.getAnnotation(j.class)) != null) || !z) && field.getName().equalsIgnoreCase(str2)) {
                    field.setAccessible(true);
                    return jsonObjectToObject(jSONObject, field);
                }
            }
            if (!z2) {
                return null;
            }
            cls = cls.getSuperclass();
        }
        return null;
    }

    public static int getType(Class<?> cls) {
        if (cls != null && (String.class.isAssignableFrom(cls) || Character.class.isAssignableFrom(cls) || Character.TYPE.isAssignableFrom(cls) || Character.TYPE.isAssignableFrom(cls))) {
            return 0;
        }
        if (cls != null && (Byte.TYPE.isAssignableFrom(cls) || Byte.TYPE.isAssignableFrom(cls))) {
            return 21;
        }
        if (cls != null && (Short.TYPE.isAssignableFrom(cls) || Short.TYPE.isAssignableFrom(cls))) {
            return 31;
        }
        if (cls != null && (Integer.TYPE.isAssignableFrom(cls) || Integer.class.isAssignableFrom(cls) || Number.class.isAssignableFrom(cls) || Integer.TYPE.isAssignableFrom(cls))) {
            return 1;
        }
        if (cls != null && (Long.TYPE.isAssignableFrom(cls) || Long.TYPE.isAssignableFrom(cls))) {
            return 2;
        }
        if (cls != null && (Float.TYPE.isAssignableFrom(cls) || Float.TYPE.isAssignableFrom(cls))) {
            return 3;
        }
        if (cls != null && (Double.TYPE.isAssignableFrom(cls) || Double.TYPE.isAssignableFrom(cls))) {
            return 4;
        }
        if (cls != null && (Boolean.TYPE.isAssignableFrom(cls) || Boolean.class.isAssignableFrom(cls) || Boolean.TYPE.isAssignableFrom(cls))) {
            return 5;
        }
        if (cls != null && cls.isArray()) {
            return 6;
        }
        if (cls != null && Connection.class.isAssignableFrom(cls)) {
            return 7;
        }
        if (cls != null && JSONArray.class.isAssignableFrom(cls)) {
            return 8;
        }
        if (cls != null && JSONObject.class.isAssignableFrom(cls)) {
            return 41;
        }
        if (cls != null && List.class.isAssignableFrom(cls)) {
            return 9;
        }
        if (cls == null || !Map.class.isAssignableFrom(cls)) {
            return (cls == null || !Enum.class.isAssignableFrom(cls)) ? 14 : 11;
        }
        return 10;
    }

    public static Object jsonArray(JSONArray jSONArray, Class<?> cls) {
        Object objNewInstance = null;
        if (jSONArray != null) {
            try {
                objNewInstance = Array.newInstance(cls, jSONArray.length());
            } catch (Exception unused) {
            }
            if (objNewInstance != null) {
                for (int i = 0; i < jSONArray.length(); i++) {
                    int type = getType(cls);
                    if (type == 1) {
                        Array.setInt(objNewInstance, i, jSONArray.getInt(i));
                    } else if (type == 2) {
                        Array.setLong(objNewInstance, i, jSONArray.getLong(i));
                    } else if (type == 3 || type == 4) {
                        Array.setDouble(objNewInstance, i, jSONArray.getDouble(i));
                    } else if (type == 5) {
                        Array.setBoolean(objNewInstance, i, jSONArray.getBoolean(i));
                    } else if (type == 21) {
                        Array.setByte(objNewInstance, i, (byte) jSONArray.getInt(i));
                    } else if (type != 31) {
                        Array.set(objNewInstance, i, jSONArray.get(i));
                    } else {
                        Array.setShort(objNewInstance, i, (short) jSONArray.getInt(i));
                    }
                }
            }
        }
        return objNewInstance;
    }

    public static List<Object> jsonArrayToList(JSONArray jSONArray) throws JSONException {
        ArrayList arrayList = new ArrayList();
        if (jSONArray != null) {
            for (int i = 0; i < jSONArray.length(); i++) {
                Object obj = jSONArray.get(i);
                if (obj != null) {
                    if (obj instanceof JSONObject) {
                        arrayList.add(jsonObjectToMap((JSONObject) obj));
                    } else if (obj instanceof JSONArray) {
                        arrayList.add(jsonArrayToList((JSONArray) obj));
                    } else {
                        arrayList.add(obj);
                    }
                }
            }
        }
        return arrayList;
    }

    public static Map<String, Object> jsonObjectToMap(JSONObject jSONObject) throws JSONException {
        HashMap map = new HashMap();
        if (jSONObject != null) {
            Iterator<String> itKeys = jSONObject.keys();
            while (itKeys.hasNext()) {
                String next = itKeys.next();
                Object obj = jSONObject.get(next);
                if (obj == null) {
                    map.put(next, null);
                } else if (obj instanceof JSONObject) {
                    map.put(next, jsonObjectToMap((JSONObject) obj));
                } else if (obj instanceof JSONArray) {
                    map.put(next, jsonArrayToList((JSONArray) obj));
                } else {
                    map.put(next, obj);
                }
            }
        }
        return map;
    }

    public static Object jsonObjectToObject(JSONObject jSONObject, Field field) {
        int type = getType(field.getType());
        if (type == 21) {
            return Byte.valueOf((byte) jSONObject.optInt(field.getName()));
        }
        if (type == 31) {
            return Short.valueOf((short) jSONObject.optInt(field.getName()));
        }
        if (type != 41) {
            switch (type) {
                case 0:
                case 11:
                    Object objOpt = jSONObject.opt(field.getName());
                    if (!(objOpt instanceof String)) {
                        return objOpt;
                    }
                    try {
                        for (Method method : field.getType().getMethods()) {
                            if (method.getName().equals("valueOf")) {
                                return method.invoke(null, objOpt);
                            }
                        }
                        return objOpt;
                    } catch (Exception unused) {
                        return objOpt;
                    }
                case 1:
                    return Integer.valueOf(jSONObject.optInt(field.getName()));
                case 2:
                    return Long.valueOf(jSONObject.optLong(field.getName()));
                case 3:
                case 4:
                    return Double.valueOf(jSONObject.optDouble(field.getName()));
                case 5:
                    return Boolean.valueOf(jSONObject.optBoolean(field.getName()));
                case 6:
                case 7:
                case 8:
                    break;
                case 9:
                    return jsonArrayToList(jSONObject.optJSONArray(field.getName()));
                case 10:
                    return jsonObjectToMap(jSONObject.optJSONObject(field.getName()));
                default:
                    return null;
            }
        }
        Class<?> type2 = field.getType();
        return type2 == JSONArray.class ? jSONObject.optJSONArray(field.getName()) : type2 == JSONObject.class ? jSONObject.optJSONObject(field.getName()) : jsonArray(jSONObject.optJSONArray(field.getName()), type2.getComponentType());
    }

    public static JSONObject result2Json(final int i, final String str, Object obj) {
        try {
            return toJson2(obj, true, new a<JSONObject>() { // from class: com.huiyuan.util.JsonHelper.1
                @Override // b.b.d.a
                public void apply(JSONObject jSONObject) {
                    try {
                        jSONObject.put("result", i);
                        jSONObject.put("message", str);
                    } catch (Exception unused) {
                    }
                }
            });
        } catch (Exception e) {
            JSONObject jSONObject = new JSONObject();
            try {
                jSONObject.put("result", i);
                jSONObject.put("message", e.getMessage());
            } catch (Exception unused) {
            }
            return jSONObject;
        }
    }

    public static String toJson(Object obj, boolean z, a<JSONObject> aVar) {
        return toJson2(obj, z, aVar).toString();
    }

    public static JSONObject toJson2(Object obj, boolean z, a<JSONObject> aVar) {
        return toJson2(obj, z, false, aVar);
    }

    public static <T> T fromJson(String str, boolean z, boolean z2, Class<T> cls) throws IllegalAccessException, InstantiationException {
        if (str == null || str.equals("")) {
            throw new NullPointerException("JsonString can't be null");
        }
        T tNewInstance = cls.newInstance();
        JSONObject jSONObject = (JSONObject) new JSONTokener(str).nextValue();
        while (!cls.equals(Object.class)) {
            for (Field field : cls.getDeclaredFields()) {
                if ((z && ((j) field.getAnnotation(j.class)) != null) || !z) {
                    field.setAccessible(true);
                    field.set(tNewInstance, jsonObjectToObject(jSONObject, field));
                }
            }
            if (!z2) {
                break;
            }
            cls = cls.getSuperclass();
        }
        return tNewInstance;
    }

    public static String toJson(Object obj, boolean z, boolean z2, a<JSONObject> aVar) {
        return toJson2(obj, z, z2, aVar).toString();
    }

    /* JADX WARN: Removed duplicated region for block: B:53:0x012b  */
    /* JADX WARN: Removed duplicated region for block: B:79:0x01a4  */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct code enable 'Show inconsistent code' option in preferences
    */
    public static org.json.JSONObject toJson2(java.lang.Object r10, boolean r11, boolean r12, b.b.d.a<org.json.JSONObject> r13) throws org.json.JSONException, java.lang.IllegalAccessException {
        /*
            Method dump skipped, instruction units count: 452
            To view this dump change 'Code comments level' option to 'DEBUG'
        */
        throw new UnsupportedOperationException("Method not decompiled: com.huiyuan.util.JsonHelper.toJson2(java.lang.Object, boolean, boolean, b.b.d.a):org.json.JSONObject");
    }

    public static JSONObject result2Json(int i, String str) {
        return result2Json(i, str, new a<JSONObject>() { // from class: com.huiyuan.util.JsonHelper.2
            @Override // b.b.d.a
            public void apply(JSONObject jSONObject) {
            }
        });
    }

    public static JSONObject result2Json(int i, String str, a<JSONObject> aVar) {
        JSONObject jSONObject = new JSONObject();
        try {
            jSONObject.put("result", i);
            jSONObject.put("message", str);
            if (aVar != null) {
                aVar.apply(jSONObject);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return jSONObject;
    }

    public static JSONObject result2Json(int i, String str, final Cursor cursor) {
        return result2Json(i, str, new a<JSONObject>() { // from class: com.huiyuan.util.JsonHelper.3
            @Override // b.b.d.a
            public void apply(JSONObject jSONObject) {
                if (cursor != null) {
                    try {
                        try {
                            JSONArray jSONArray = new JSONArray();
                            while (cursor.moveToNext()) {
                                int columnCount = cursor.getColumnCount();
                                JSONObject jSONObject2 = new JSONObject();
                                for (int i2 = 0; i2 < columnCount; i2++) {
                                    if (cursor.getColumnName(i2) != null) {
                                        try {
                                            if (cursor.getString(i2) != null) {
                                                int type = cursor.getType(i2);
                                                if (type == 1) {
                                                    float f = cursor.getFloat(i2);
                                                    if (f < -2.1474836E9f || f > 2.1474836E9f) {
                                                        jSONObject2.put(cursor.getColumnName(i2), cursor.getString(i2));
                                                    } else {
                                                        jSONObject2.put(cursor.getColumnName(i2), cursor.getInt(i2));
                                                    }
                                                } else if (type == 2) {
                                                    jSONObject2.put(cursor.getColumnName(i2), cursor.getFloat(i2));
                                                } else if (type == 4) {
                                                    jSONObject2.put(cursor.getColumnName(i2), new String(Base64.encode(cursor.getBlob(i2), 0)));
                                                } else if (type != 5) {
                                                    jSONObject2.put(cursor.getColumnName(i2), cursor.getString(i2));
                                                } else {
                                                    jSONObject2.put(cursor.getColumnName(i2), (Object) null);
                                                }
                                            } else {
                                                jSONObject2.put(cursor.getColumnName(i2), "");
                                            }
                                        } catch (Exception unused) {
                                        }
                                    }
                                }
                                jSONArray.put(jSONObject2);
                            }
                            jSONObject.put("rows", jSONArray);
                        } catch (Exception unused2) {
                        }
                    } finally {
                        cursor.close();
                    }
                }
            }
        });
    }

    public static void fromJson(String str, boolean z, Object obj) throws IllegalAccessException {
        fromJson(str, z, false, obj);
    }

    public static Object fromJsonToFieldValue(String str, String str2, boolean z, Class<?> cls) {
        return fromJsonToFieldValue(str, str2, z, false, cls);
    }

    public static void fromJson(String str, boolean z, boolean z2, Object obj) throws IllegalAccessException {
        if (str != null && !str.equals("")) {
            JSONObject jSONObject = (JSONObject) new JSONTokener(str).nextValue();
            for (Class<?> superclass = obj.getClass(); !superclass.equals(Object.class); superclass = superclass.getSuperclass()) {
                for (Field field : superclass.getDeclaredFields()) {
                    if ((z && ((j) field.getAnnotation(j.class)) != null) || !z) {
                        field.setAccessible(true);
                        field.set(obj, jsonObjectToObject(jSONObject, field));
                    }
                }
                if (!z2) {
                    return;
                }
            }
            return;
        }
        throw new NullPointerException("JsonString can't be null");
    }
}
