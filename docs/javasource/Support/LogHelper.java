package com.huiyuan.util;

/* JADX INFO: loaded from: classes.dex */
public class LogHelper {

    /* JADX INFO: renamed from: a, reason: collision with root package name */
    public static LogLevel f869a = LogLevel.DEBUG;

    public enum LogLevel {
        LOG((byte) 0),
        WARN((byte) 1),
        INFO((byte) 2),
        ERROR((byte) 3),
        DEBUG((byte) 4),
        VERBOSE((byte) 5),
        NOLOG((byte) 6);

        public byte _value;

        LogLevel(byte b2) {
            this._value = b2;
        }

        public static LogLevel indexOf(byte b2) {
            for (LogLevel logLevel : values()) {
                if (logLevel.getValue() == b2) {
                    return logLevel;
                }
            }
            return null;
        }

        public byte getValue() {
            return this._value;
        }
    }

    public static void changeLogLevel(LogLevel logLevel) {
        f869a = logLevel;
    }

    public static void d(String str, String str2) {
        if (f869a._value <= LogLevel.DEBUG._value) {
            int length = 2001 - str.length();
            while (str2.length() > length) {
                str2.substring(0, length);
                str2 = str2.substring(length);
            }
        }
    }

    public static void e(String str, String str2) {
        if (f869a._value <= LogLevel.ERROR._value) {
            int length = 2001 - str.length();
            while (str2.length() > length) {
                str2.substring(0, length);
                str2 = str2.substring(length);
            }
        }
    }

    public static void i(String str, String str2) {
        if (f869a._value <= LogLevel.INFO._value) {
            int length = 2001 - str.length();
            while (str2.length() > length) {
                str2.substring(0, length);
                str2 = str2.substring(length);
            }
        }
    }

    public static void v(String str, String str2) {
        if (f869a._value <= LogLevel.VERBOSE._value) {
            int length = 2001 - str.length();
            while (str2.length() > length) {
                str2.substring(0, length);
                str2 = str2.substring(length);
            }
        }
    }

    public static void w(String str, String str2) {
        if (f869a._value <= LogLevel.WARN._value) {
            int length = 2001 - str.length();
            while (str2.length() > length) {
                str2.substring(0, length);
                str2 = str2.substring(length);
            }
        }
    }
}
