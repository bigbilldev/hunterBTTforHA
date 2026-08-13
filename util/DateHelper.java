package com.huiyuan.util;

import b.a.a.a.a;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/* JADX INFO: loaded from: classes.dex */
public class DateHelper {
    public static String date2YMDE(Date date, String str) {
        if (date == null) {
            return "";
        }
        try {
            return doFormatDate(date, str + " E");
        } catch (Exception e) {
            e.printStackTrace();
            return "";
        }
    }

    public static String doFormatDate(Date date, String str) {
        return new SimpleDateFormat(str).format(date);
    }

    public static int extractDate(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        return calendar.get(5);
    }

    public static int extractDayOfWeek(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        int i = calendar.get(7) - 1;
        if (i == 0) {
            return 7;
        }
        return i;
    }

    public static int extractHour(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        return calendar.get(10);
    }

    public static int extractMilliSecond(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        return calendar.get(14);
    }

    public static int extractMinute(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        return calendar.get(12);
    }

    public static int extractMonth(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        return calendar.get(2);
    }

    public static int extractSecond(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        return calendar.get(13);
    }

    public static int extractYear(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        return calendar.get(1);
    }

    public static int getCountDayOfMonth() {
        return Calendar.getInstance(Locale.CHINA).getActualMaximum(5);
    }

    public static int getCountDayOfYear() {
        Calendar calendar = Calendar.getInstance();
        calendar.set(6, 1);
        calendar.roll(6, -1);
        return calendar.get(6);
    }

    public static int getCountWeeksOfYear(int i) {
        int i2 = (i % 400 == 0 || (i % 4 == 0 && i % 100 != 0)) ? 366 : 365;
        int i3 = i2 % 7;
        return i2 / 7;
    }

    public static String getCurrentHoursMin() {
        return doFormatDate(new Date(), "HH:mm");
    }

    public static Long getCurrentSeconds() {
        return Long.valueOf(System.currentTimeMillis() / 1000);
    }

    public static String getCurrentTime(String str) {
        return doFormatDate(new Date(), str);
    }

    public static Date getDateForWeekDay(int i, Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        calendar.add(5, i - calendar.get(7));
        return calendar.getTime();
    }

    public static List<Map<String, String>> getDayList(String str, String str2, String str3) {
        ArrayList arrayList = new ArrayList();
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat(str3);
        try {
            Date date = simpleDateFormat.parse(str);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(date);
            Date date2 = simpleDateFormat.parse(str2);
            Calendar calendar2 = Calendar.getInstance();
            calendar2.setTime(date2);
            if (calendar.compareTo(calendar2) <= 0) {
                while (calendar.compareTo(calendar2) <= 0) {
                    Hashtable hashtable = new Hashtable();
                    hashtable.put("DAY", simpleDateFormat.format(calendar.getTime()));
                    arrayList.add(hashtable);
                    calendar.add(5, 1);
                }
            } else {
                while (calendar.compareTo(calendar2) >= 0) {
                    Hashtable hashtable2 = new Hashtable();
                    hashtable2.put("DAY", simpleDateFormat.format(calendar.getTime()));
                    arrayList.add(hashtable2);
                    calendar.add(5, -1);
                }
            }
        } catch (ParseException unused) {
        }
        return arrayList;
    }

    public static int getDayOfMonth(Date date) {
        Calendar calendar = Calendar.getInstance(Locale.CHINA);
        calendar.setTime(date);
        return calendar.get(5);
    }

    public static int getDayOfWeek(Date date) {
        Calendar calendar = Calendar.getInstance(Locale.CHINA);
        calendar.setTime(date);
        int i = calendar.get(7) - 1;
        if (i == 0) {
            return 7;
        }
        return i;
    }

    public static int getDayOfYear() {
        return Calendar.getInstance().get(6);
    }

    public static int getDiffDays(Date date, Date date2) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        Calendar calendar2 = Calendar.getInstance();
        calendar2.setTime(date2);
        return (int) Math.abs((calendar.getTimeInMillis() - calendar2.getTimeInMillis()) / 86400000);
    }

    public static int getDiffMinutes(Date date, Date date2) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        Calendar calendar2 = Calendar.getInstance();
        calendar2.setTime(date2);
        return ((int) (calendar.getTimeInMillis() - calendar2.getTimeInMillis())) / 60000;
    }

    public static Date getFirstDayOfMonth(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        calendar.set(5, 1);
        return calendar.getTime();
    }

    public static String getFirstDayOfMonthStr(Date date) {
        return doFormatDate(getFirstDayOfMonth(date), "yyyy-MM-dd");
    }

    public static Date getFirstDayOfQuarter(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        int i = calendar.get(2);
        if (i >= 0 && i <= 2) {
            calendar.set(2, 0);
        }
        if (i >= 3 && i <= 5) {
            calendar.set(2, 3);
        }
        if (i >= 6 && i <= 7) {
            calendar.set(2, 6);
        }
        if (i >= 9 && i <= 11) {
            calendar.set(2, 9);
        }
        calendar.set(5, calendar.getActualMinimum(5));
        return calendar.getTime();
    }

    public static String getFirstDayOfQuarterStr(Date date) {
        return doFormatDate(getFirstDayOfQuarter(date), "yyyy-MM-dd");
    }

    public static String getFirstDayOfWeek(String str, String str2, String str3) {
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy w");
        new Date();
        try {
            return new SimpleDateFormat(str3).format(simpleDateFormat.parse(str + " " + str2));
        } catch (ParseException unused) {
            return "";
        }
    }

    public static Date getHalfYear() {
        Calendar.getInstance().add(6, 183);
        return Calendar.getInstance().getTime();
    }

    public static String getHalfYearStr() {
        return doFormatDate(getHalfYear(), "yyyy-MM-dd");
    }

    public static List<Map<String, String>> getHourList(String str, String str2, int i) {
        ArrayList arrayList = new ArrayList();
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("HH:mm");
        try {
            Date date = simpleDateFormat.parse(str);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(date);
            Date date2 = simpleDateFormat.parse(str2);
            Calendar calendar2 = Calendar.getInstance();
            calendar2.setTime(date2);
            while (calendar.compareTo(calendar2) <= 0) {
                Hashtable hashtable = new Hashtable();
                hashtable.put("HOUR", simpleDateFormat.format(calendar.getTime()));
                arrayList.add(hashtable);
                calendar.add(12, i);
            }
        } catch (ParseException unused) {
        }
        return arrayList;
    }

    public static Date getLastDayOfMonth(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        calendar.set(5, calendar.getActualMaximum(5));
        return calendar.getTime();
    }

    public static String getLastDayOfMonthStr(Date date) {
        return doFormatDate(getLastDayOfMonth(date), "yyyy-MM-dd");
    }

    public static Date getLastDayOfQuarter(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        int i = calendar.get(2);
        if (i >= 0 && i <= 2) {
            calendar.set(2, 2);
        }
        if (i >= 3 && i <= 5) {
            calendar.set(2, 5);
        }
        if (i >= 6 && i <= 7) {
            calendar.set(2, 7);
        }
        if (i >= 9 && i <= 11) {
            calendar.set(2, 11);
        }
        calendar.set(5, calendar.getActualMaximum(5));
        System.out.println(calendar.getTime());
        return calendar.getTime();
    }

    public static String getLastDayOfQuarterStr(Date date) {
        return doFormatDate(getLastDayOfQuarter(date), "yyyy-MM-dd");
    }

    public static String getLastDayOfWeek(String str, String str2, String str3) {
        return getOffsetDay(getFirstDayOfWeek(str, String.valueOf(Integer.valueOf(str2).intValue() + 1), str3), -1, str3);
    }

    public static Date getLastMonthFirstDay(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        calendar.set(5, 1);
        calendar.add(2, -1);
        return calendar.getTime();
    }

    public static String getLastMonthFirstDayStr(Date date) {
        return doFormatDate(getLastMonthFirstDay(date), "yyyy-MM-dd");
    }

    public static Date getLastMonthLastDay(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        calendar.add(2, -1);
        calendar.set(5, 1);
        calendar.roll(5, -1);
        return calendar.getTime();
    }

    public static String getLastMonthLastDayStr(Date date) {
        return doFormatDate(getLastMonthLastDay(date), "yyyy-MM-dd");
    }

    public static List<String> getListDayOfMonth(String str) {
        ArrayList arrayList = new ArrayList();
        List<Map<String, String>> dayList = getDayList(getFirstDayOfMonthStr(doFormatDate(str, "yyyy-MM-dd")), getLastDayOfMonthStr(doFormatDate(str, "yyyy-MM-dd")), "yyyy-MM-dd");
        for (int i = 0; i < dayList.size(); i++) {
            arrayList.add(dayList.get(i).get("DAY"));
        }
        return arrayList;
    }

    public static List<String> getListDayOfWeek(String str) {
        ArrayList arrayList = new ArrayList();
        List<Map<String, String>> dayList = getDayList(getWeekFirstDayStr(doFormatDate(str, "yyyy-MM-dd")), getWeekLastDayStr(doFormatDate(str, "yyyy-MM-dd")), "yyyy-MM-dd");
        for (int i = 0; i < dayList.size(); i++) {
            arrayList.add(dayList.get(i).get("DAY"));
        }
        return arrayList;
    }

    public static int getMonth() {
        return Calendar.getInstance().get(2) + 1;
    }

    public static String getMonthDay(int i, String str, String str2) {
        String str3;
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat(str);
        try {
            Date date = simpleDateFormat.parse(str2);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(date);
            Calendar calendar2 = Calendar.getInstance();
            calendar2.setTime(date);
            calendar2.add(5, 1);
            if (calendar2.get(2) != calendar.get(2)) {
                calendar2.add(2, i);
                calendar2.add(5, -1);
                str3 = simpleDateFormat.format(calendar2.getTime());
            } else {
                calendar.add(2, i);
                str3 = simpleDateFormat.format(calendar.getTime());
            }
            return str3;
        } catch (ParseException unused) {
            System.out.println("d");
            return "197101";
        }
    }

    public static String getNextDayStr(String str) {
        return doFormatDate(new Date(doFormatDate(str, "yyyy-MM-dd").getTime() + 86400000), "yyyy-MM-dd");
    }

    public static Date getNextMonthFirstDay(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        calendar.add(2, 1);
        calendar.set(5, 1);
        return calendar.getTime();
    }

    public static String getNextMonthFirstDayStr(Date date) {
        return doFormatDate(getNextMonthFirstDay(date), "yyyy-MM-dd");
    }

    public static Date getNextMonthLastDay(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        calendar.add(2, 1);
        calendar.set(5, 1);
        calendar.roll(5, -1);
        return calendar.getTime();
    }

    public static String getNextMonthLastDayStr(Date date) {
        return doFormatDate(getNextMonthLastDay(date), "yyyy-MM-dd");
    }

    public static Date getNextWeekFirstDate(Date date) {
        Calendar calendar = Calendar.getInstance(Locale.CHINA);
        calendar.setTime(date);
        for (int i = 1; i <= 7; i++) {
            calendar.add(5, 1);
            if (calendar.get(7) == 2) {
                return calendar.getTime();
            }
        }
        return date;
    }

    public static String getNextWeekFirstDay(Date date) {
        return new SimpleDateFormat("yyyy-MM-dd").format(getNextWeekFirstDate(date));
    }

    public static Date getNextWeekLastDate(Date date) {
        Calendar calendar = Calendar.getInstance(Locale.CHINA);
        calendar.setTime(getNextWeekFirstDate(date));
        for (int i = 1; i <= 7; i++) {
            calendar.add(5, 1);
            if (calendar.get(7) == 1) {
                return calendar.getTime();
            }
        }
        return date;
    }

    public static String getNextWeekLastDay(Date date) {
        return new SimpleDateFormat("yyyy-MM-dd").format(getNextWeekLastDate(date));
    }

    public static Date getNextYearFirstDay(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        calendar.add(1, 1);
        calendar.set(6, 1);
        return calendar.getTime();
    }

    public static String getNextYearFirstDayStr(Date date) {
        return doFormatDate(getNextYearFirstDay(date), "yyyy-MM-dd");
    }

    public static Date getNextYearLastDay(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        calendar.add(1, 1);
        calendar.set(6, 1);
        calendar.roll(6, -1);
        return calendar.getTime();
    }

    public static String getNextYearLastDayStr(Date date) {
        return doFormatDate(getNextYearLastDay(date), "yyyy-MM-dd");
    }

    public static String getOffsetDay(String str, Integer num, String str2) {
        try {
            SimpleDateFormat simpleDateFormat = new SimpleDateFormat(str2);
            Date date = simpleDateFormat.parse(str);
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(date);
            calendar.add(5, num.intValue() - 1);
            return simpleDateFormat.format(calendar.getTime());
        } catch (Exception e) {
            e.printStackTrace();
            return "";
        }
    }

    public static String getPreDayStr(String str) {
        return doFormatDate(new Date(doFormatDate(str, "yyyy-MM-dd").getTime() - 86400000), "yyyy-MM-dd");
    }

    public static Date getSubtractionDay(Date date, Integer num) {
        GregorianCalendar gregorianCalendar = new GregorianCalendar();
        gregorianCalendar.setTime(date);
        gregorianCalendar.add(5, num.intValue());
        return gregorianCalendar.getTime();
    }

    public static String getSubtractionStringDay(Date date, Integer num, String str) {
        GregorianCalendar gregorianCalendar = new GregorianCalendar();
        gregorianCalendar.setTime(date);
        gregorianCalendar.add(5, num.intValue());
        return doFormatDate(gregorianCalendar.getTime(), str);
    }

    public static String getToday(String str) {
        return new SimpleDateFormat(str).format(new Date());
    }

    public static String getTomorrow(String str) {
        Calendar calendar = Calendar.getInstance();
        calendar.add(5, 1);
        return new SimpleDateFormat(str).format(calendar.getTime());
    }

    public static Date getWeekFirstDay(Date date) {
        Calendar calendar = Calendar.getInstance(Locale.CHINA);
        calendar.setTime(date);
        for (int i = 1; i <= 7; i++) {
            calendar.add(5, -1);
            if (calendar.get(7) == 2) {
                return calendar.getTime();
            }
        }
        return date;
    }

    public static String getWeekFirstDayStr(Date date) {
        return doFormatDate(getWeekFirstDay(date), "yyyy-MM-dd");
    }

    public static int getWeekIndexOfYear(Date date) {
        try {
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(date);
            return calendar.get(3);
        } catch (Exception unused) {
            return 0;
        }
    }

    public static Date getWeekLastDay(Date date) {
        Calendar calendar = Calendar.getInstance(Locale.CHINA);
        calendar.setTime(getWeekFirstDay(date));
        for (int i = 1; i <= 7; i++) {
            calendar.add(5, 1);
            if (calendar.get(7) == 1) {
                return calendar.getTime();
            }
        }
        return date;
    }

    public static String getWeekLastDayStr(Date date) {
        return doFormatDate(getWeekLastDay(date), "yyyy-MM-dd");
    }

    public static List getWeekListOfYear(Date date) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        int i = calendar.get(1);
        int countWeeksOfYear = getCountWeeksOfYear(i);
        ArrayList arrayList = new ArrayList();
        int i2 = 0;
        while (i2 < countWeeksOfYear) {
            i2++;
            String offsetDay = getOffsetDay(getFirstDayOfWeek(String.valueOf(i), String.valueOf(i2), "yyyy年MM月dd号"), 2, "yyyy年MM月dd号");
            String lastDayOfWeek = getLastDayOfWeek(String.valueOf(i), String.valueOf(i2), "yyyy年MM月dd号");
            HashMap map = new HashMap();
            map.put("yearWeek", i + "-" + i2);
            map.put("weekIndex", Integer.valueOf(i2));
            map.put("weekDay", String.valueOf(i) + "年第" + i2 + "周（" + offsetDay + "-" + lastDayOfWeek + "）");
            arrayList.add(map);
        }
        return arrayList;
    }

    public static int getWeekOfMonth() {
        return Calendar.getInstance().get(8);
    }

    public static int getWeekOfYear() {
        try {
            Calendar calendar = Calendar.getInstance();
            calendar.setTime(new Date());
            return calendar.get(3);
        } catch (Exception e) {
            e.printStackTrace();
            return 0;
        }
    }

    public static String getWeekStr(String str) {
        Date dateDoFormatDate = doFormatDate(str, "yyyy-MM-dd");
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(dateDoFormatDate);
        return new SimpleDateFormat("EEEE").format(calendar.getTime());
    }

    public static int getYear() {
        return Calendar.getInstance().get(1);
    }

    public static String getYesterday(String str) {
        Calendar calendar = Calendar.getInstance();
        calendar.add(5, -1);
        return new SimpleDateFormat(str).format(calendar.getTime());
    }

    public static Date getYesterdayOfDate() {
        Calendar calendar = Calendar.getInstance();
        calendar.add(5, -1);
        return calendar.getTime();
    }

    public static boolean isLeapYear(int i) {
        return (i % 4 == 0 && i % 100 != 0) || i % 400 == 0;
    }

    public static boolean isLeapYear2(int i) {
        return new GregorianCalendar().isLeapYear(i);
    }

    public static boolean isWeekEnd(String str) {
        return getDayOfWeek(str) == 6 || getDayOfWeek(str) == 7;
    }

    public static Date parseDateTime(String str) {
        if (!StringHelper.isEmpty(str)) {
            int i = 0;
            try {
                String strReplaceAll = str.replaceAll("-", "/").replaceAll("T", " ");
                Matcher matcher = Pattern.compile("([^\\.]+)\\.+(\\d+)$").matcher(strReplaceAll);
                if (matcher.find()) {
                    strReplaceAll = matcher.group(1);
                    i = Integer.parseInt(matcher.group(2));
                }
                return new Date(Date.parse(strReplaceAll) + ((long) i));
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        return null;
    }

    public static Date sceondsCastDate(Long l) {
        return new Date(l.longValue() * 1000);
    }

    public static String sceondsCastStringDate(Long l, String str) {
        return new SimpleDateFormat(str).format(new Date(l.longValue() * 1000));
    }

    public static Date toDate(int i, int i2, int i3, int i4, int i5, int i6) {
        Calendar calendar = Calendar.getInstance();
        calendar.set(i, i2, i3, i4, i5, i6);
        return calendar.getTime();
    }

    public static Date doFormatDate(String str, String str2) {
        try {
            return new SimpleDateFormat(str2).parse(str);
        } catch (ParseException unused) {
            return new Date();
        }
    }

    public static boolean isWeekEnd(Date date) {
        return getDayOfWeek(date) == 6 || getDayOfWeek(date) == 7;
    }

    public static Date sceondsCastDate(String str) {
        return new Date(Long.parseLong(str) * 1000);
    }

    public static int getDayOfWeek(String str) {
        return getDayOfWeek(doFormatDate(str, "yyyy-MM-dd"));
    }

    public static String sceondsCastStringDate(String str, String str2) {
        return new SimpleDateFormat(str2).format(new Date(Long.parseLong(str) * 1000));
    }

    public static String getYesterday() {
        Calendar calendar = Calendar.getInstance();
        calendar.add(5, -1);
        return new SimpleDateFormat("yyyy-MM-dd").format(calendar.getTime());
    }

    public int getWeekOfYear(String str) {
        try {
            return getWeekIndexOfYear(new SimpleDateFormat("yyyy-MM-dd").parse(str));
        } catch (Exception e) {
            e.printStackTrace();
            return 0;
        }
    }

    public static Long getDiffDays(String str, String str2) {
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy-MM-dd");
        try {
            return Long.valueOf((simpleDateFormat.parse(str).getTime() - simpleDateFormat.parse(str2).getTime()) / 86400000);
        } catch (Exception unused) {
            return 0L;
        }
    }

    public static int getDiffMinutes(String str, String str2) {
        if (str.length() <= 10) {
            str = a.a(str, " 00:00:00");
        }
        if (str2.length() <= 10) {
            str2 = a.a(str2, " 00:00:00");
        }
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(doFormatDate(str, "yyyy-MM-dd HH:mm:ss"));
        Calendar calendar2 = Calendar.getInstance();
        calendar2.setTime(doFormatDate(str2, "yyyy-MM-dd HH:mm:ss"));
        return ((int) (calendar.getTimeInMillis() - calendar2.getTimeInMillis())) / 60000;
    }
}
