package b.b.a.m;

import com.huiyuan.ble.BatteryLevel_Protocol;
import com.huiyuan.ble.DeviceName_Protocol;
import com.huiyuan.ble.FirmwareVersion_Protocol;
import com.huiyuan.ble.ManufacturerName_Protocol;
import com.huiyuan.ble.ais.First_C1_Protocol;
import com.huiyuan.ble.ais.First_C2_Protocol;
import com.huiyuan.ble.ais.First_C3_Protocol;
import com.huiyuan.ble.ais.First_C4_Protocol;
import com.huiyuan.ble.ais.First_D1_Protocol;
import com.huiyuan.ble.ais.First_D2_Protocol;
import com.huiyuan.ble.ais.First_D3_Protocol;
import com.huiyuan.ble.ais.First_D4_Protocol;
import com.huiyuan.ble.ais.First_D5_Protocol;
import com.huiyuan.ble.ais.First_D6_Protocol;
import com.huiyuan.ble.ais.First_D7_Protocol;
import com.huiyuan.ble.ais.First_D8_Protocol;
import com.huiyuan.ble.ais.First_D9_Protocol;
import com.huiyuan.ble.ais.First_E1_Protocol;
import com.huiyuan.ble.ais.First_E2_Protocol;
import com.huiyuan.ble.ais.First_E3_Protocol;
import com.huiyuan.ble.ais.First_E4_Protocol;
import com.huiyuan.ble.ais.First_E5_Protocol;
import com.huiyuan.ble.ais.First_E6_Protocol;
import com.huiyuan.ble.ais.First_E7_Protocol;
import com.huiyuan.ble.ais.First_E8_Protocol;
import com.huiyuan.ble.ais.First_E9_Protocol;
import com.huiyuan.ble.ais.First_EA_Protocol;
import com.huiyuan.ble.ais.First_EB_Protocol;
import com.huiyuan.ble.ais.First_F1_Protocol;
import com.huiyuan.ble.ais.First_F2_Protocol;
import com.huiyuan.ble.ais.Second_81_Protocol;
import com.huiyuan.ble.ais.Second_82_Protocol;
import com.huiyuan.ble.ais.Second_83_Protocol;
import com.huiyuan.ble.ais.Second_84_Protocol;
import com.huiyuan.ble.ais.Second_85_Protocol;
import com.huiyuan.ble.ais.Second_86_Protocol;
import com.huiyuan.ble.ais.Second_87_Protocol;
import com.huiyuan.ble.ais.Second_88_Protocol;
import com.huiyuan.ble.ais.Second_89_Protocol;
import com.huiyuan.ble.ais.Second_8A_Protocol;
import com.huiyuan.ble.ais.Second_8B_Protocol;
import com.huiyuan.ble.ais.Second_8C_Protocol;
import com.huiyuan.ble.ais.Second_8D_Protocol;
import com.huiyuan.ble.ais.Second_8E_Protocol;
import com.huiyuan.ble.ais.Second_8F_Protocol;
import com.huiyuan.ble.ais.Second_90_Protocol;
import com.huiyuan.ble.ais.Second_91_Protocol;
import com.huiyuan.ble.ais.Second_92_Protocol;
import com.huiyuan.ble.ais.Second_93_Protocol;
import com.huiyuan.ble.ais.Second_94_Protocol;
import com.huiyuan.ble.ais.Second_95_Protocol;
import com.huiyuan.ble.ais.Second_96_Protocol;
import com.huiyuan.ble.ais.Second_97_Protocol;
import com.huiyuan.ble.ais.Second_98_Protocol;
import com.huiyuan.ble.ais.Second_99_Protocol;
import com.huiyuan.ble.ais.Second_9A_Protocol;
import com.huiyuan.ble.ais.Second_9B_Protocol;
import com.huiyuan.ble.ais.Second_9C_Protocol;
import com.huiyuan.ble.ais.Second_9D_Protocol;
import com.huiyuan.ble.ais.Second_9E_Protocol;
import com.huiyuan.ble.ais.Second_9F_Protocol;
import com.huiyuan.ble.ais.Second_A0_Protocol;
import com.huiyuan.ble.ais.Second_A1_Protocol;
import com.huiyuan.ble.ais.Second_A2_Protocol;
import com.huiyuan.ble.ais.Second_A3_Protocol;

/* JADX INFO: compiled from: BleCharacteristic2.java */
/* JADX INFO: loaded from: classes.dex */
public class c extends b.b.a.c {
    public c(d dVar, boolean z, String str, String str2) {
        super(dVar, z, str, str2);
    }

    /* JADX WARN: Failed to restore switch over string. Please report as a decompilation issue */
    @Override // b.b.a.c
    public b.b.a.a a() {
        if (this.d == null) {
            g gVarValueOf = g.System;
            try {
                gVarValueOf = g.valueOf(this.f638b);
            } catch (IllegalArgumentException unused) {
            }
            switch (gVarValueOf.ordinal()) {
                case 1:
                    this.d = new Second_81_Protocol(this);
                    break;
                case 2:
                    this.d = new Second_82_Protocol(this);
                    break;
                case 3:
                    this.d = new Second_83_Protocol(this);
                    break;
                case 4:
                    this.d = new Second_84_Protocol(this);
                    break;
                case 5:
                    this.d = new Second_85_Protocol(this);
                    break;
                case 6:
                    this.d = new Second_86_Protocol(this);
                    break;
                case 7:
                    this.d = new Second_87_Protocol(this);
                    break;
                case 8:
                    this.d = new Second_88_Protocol(this);
                    break;
                case 9:
                    this.d = new Second_89_Protocol(this);
                    break;
                case 10:
                    this.d = new Second_8A_Protocol(this);
                    break;
                case 11:
                    this.d = new Second_8B_Protocol(this);
                    break;
                case 12:
                    this.d = new Second_8C_Protocol(this);
                    break;
                case 13:
                    this.d = new Second_8D_Protocol(this);
                    break;
                case 14:
                    this.d = new Second_8E_Protocol(this);
                    break;
                case 15:
                    this.d = new Second_8F_Protocol(this);
                    break;
                case 16:
                    this.d = new Second_90_Protocol(this);
                    break;
                case 17:
                    this.d = new Second_91_Protocol(this);
                    break;
                case 18:
                    this.d = new Second_92_Protocol(this);
                    break;
                case 19:
                    this.d = new Second_93_Protocol(this);
                    break;
                case 20:
                    this.d = new Second_94_Protocol(this);
                    break;
                case 21:
                    this.d = new Second_95_Protocol(this);
                    break;
                case 22:
                    this.d = new Second_96_Protocol(this);
                    break;
                case 23:
                    this.d = new Second_97_Protocol(this);
                    break;
                case 24:
                    this.d = new Second_98_Protocol(this);
                    break;
                case 25:
                    this.d = new Second_99_Protocol(this);
                    break;
                case 26:
                    this.d = new Second_9A_Protocol(this);
                    break;
                case 27:
                    this.d = new Second_9B_Protocol(this);
                    break;
                case 28:
                    this.d = new Second_9C_Protocol(this);
                    break;
                case 29:
                    this.d = new Second_9D_Protocol(this);
                    break;
                case 30:
                    this.d = new Second_A2_Protocol(this);
                    break;
                case 31:
                    this.d = new Second_9E_Protocol(this);
                    break;
                case 32:
                    this.d = new Second_9F_Protocol(this);
                    break;
                case 33:
                    this.d = new Second_A0_Protocol(this);
                    break;
                case 34:
                    this.d = new Second_A1_Protocol(this);
                    break;
                case 35:
                    this.d = new Second_A3_Protocol(this);
                    break;
                case 36:
                    this.d = new First_C1_Protocol(this);
                    break;
                case 37:
                    this.d = new First_C2_Protocol(this);
                    break;
                case 38:
                    this.d = new First_C3_Protocol(this);
                    break;
                case 39:
                    this.d = new First_C4_Protocol(this);
                    break;
                case 40:
                    this.d = new First_D1_Protocol(this);
                    break;
                case 41:
                    this.d = new First_D2_Protocol(this);
                    break;
                case 42:
                    this.d = new First_D3_Protocol(this);
                    break;
                case 43:
                    this.d = new First_D4_Protocol(this);
                    break;
                case 44:
                    this.d = new First_D5_Protocol(this);
                    break;
                case 45:
                    this.d = new First_D6_Protocol(this);
                    break;
                case 46:
                    this.d = new First_D7_Protocol(this);
                    break;
                case 47:
                    this.d = new First_D8_Protocol(this);
                    break;
                case 48:
                    this.d = new First_D9_Protocol(this);
                    break;
                case 49:
                    this.d = new First_E1_Protocol(this);
                    break;
                case 50:
                    this.d = new First_E2_Protocol(this);
                    break;
                case 51:
                    this.d = new First_E3_Protocol(this);
                    break;
                case 52:
                    this.d = new First_E4_Protocol(this);
                    break;
                case 53:
                    this.d = new First_E5_Protocol(this);
                    break;
                case 54:
                    this.d = new First_E6_Protocol(this);
                    break;
                case 55:
                    this.d = new First_E7_Protocol(this);
                    break;
                case 56:
                    this.d = new First_E8_Protocol(this);
                    break;
                case 57:
                    this.d = new First_E9_Protocol(this);
                    break;
                case 58:
                    this.d = new First_EA_Protocol(this);
                    break;
                case 59:
                    this.d = new First_EB_Protocol(this);
                    break;
                case 60:
                    this.d = new First_F1_Protocol(this);
                    break;
                case 61:
                    this.d = new First_F2_Protocol(this);
                    break;
                default:
                    String str = this.f638b;
                    byte b2 = -1;
                    switch (str.hashCode()) {
                        case -1544285801:
                            if (str.equals("BatteryLevel")) {
                                b2 = 0;
                            }
                            break;
                        case -1520513503:
                            if (str.equals("DeviceName")) {
                                b2 = 1;
                            }
                            break;
                        case -767621604:
                            if (str.equals("ManufacturerName")) {
                                b2 = 3;
                            }
                            break;
                        case -208414083:
                            if (str.equals("FirmwareVersion")) {
                                b2 = 2;
                            }
                            break;
                    }
                    if (b2 == 0) {
                        this.d = new BatteryLevel_Protocol(this);
                    } else if (b2 == 1) {
                        this.d = new DeviceName_Protocol(this);
                    } else if (b2 == 2) {
                        this.d = new FirmwareVersion_Protocol(this);
                    } else if (b2 == 3) {
                        this.d = new ManufacturerName_Protocol(this);
                    }
                    break;
            }
        }
        return this.d;
    }
}
