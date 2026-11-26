package com.huiyuan.ble;

import com.huiyuan.ble.ais.AisWrapper;
import com.huiyuan.util.JsonHelper;
import java.util.ArrayList;
import java.util.Iterator;
import org.apache.cordova.CallbackContext;
import org.apache.cordova.CordovaPlugin;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/* JADX INFO: loaded from: classes.dex */
public class AisBlePlugin extends CordovaPlugin {

    public class CordovaWrapper implements b.b.d.f {

        /* JADX INFO: renamed from: a, reason: collision with root package name */
        public CallbackContext f740a;

        public CordovaWrapper(CallbackContext callbackContext) {
            this.f740a = callbackContext;
        }

        @Override // b.b.d.f
        public void error(final JSONObject jSONObject) {
            AisBlePlugin.this.cordova.getActivity().runOnUiThread(new Runnable() { // from class: com.huiyuan.ble.AisBlePlugin.CordovaWrapper.3
                @Override // java.lang.Runnable
                public void run() {
                    CordovaWrapper.this.f740a.error(jSONObject);
                }
            });
        }

        @Override // b.b.d.f
        public void success(final JSONObject jSONObject) {
            AisBlePlugin.this.cordova.getActivity().runOnUiThread(new Runnable() { // from class: com.huiyuan.ble.AisBlePlugin.CordovaWrapper.1
                @Override // java.lang.Runnable
                public void run() {
                    CordovaWrapper.this.f740a.success(jSONObject);
                }
            });
        }

        @Override // b.b.d.f
        public void error(final String str) {
            AisBlePlugin.this.cordova.getActivity().runOnUiThread(new Runnable() { // from class: com.huiyuan.ble.AisBlePlugin.CordovaWrapper.4
                @Override // java.lang.Runnable
                public void run() {
                    CordovaWrapper.this.f740a.error(str);
                }
            });
        }

        @Override // b.b.d.f
        public void success(final String str) {
            AisBlePlugin.this.cordova.getActivity().runOnUiThread(new Runnable() { // from class: com.huiyuan.ble.AisBlePlugin.CordovaWrapper.2
                @Override // java.lang.Runnable
                public void run() {
                    CordovaWrapper.this.f740a.success(str);
                }
            });
        }
    }

    public class a implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f746b;

        public a(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f746b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f746b.error(JsonHelper.result2Json(-1, "nameOrAddress为空!"));
        }
    }

    public class a0 implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ AisWrapper f747b;
        public final /* synthetic */ String c;
        public final /* synthetic */ CallbackContext d;

        public a0(AisWrapper aisWrapper, String str, CallbackContext callbackContext) {
            this.f747b = aisWrapper;
            this.c = str;
            this.d = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f747b.startScan(this.c, AisBlePlugin.this.new CordovaWrapper(this.d));
        }
    }

    public class b implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f748b;

        public b(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f748b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f748b.error("蓝牙包装对象为空!");
        }
    }

    public class b0 implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f749b;

        public b0(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f749b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f749b.error("蓝牙包装对象为空!");
        }
    }

    public class c implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ AisWrapper f750b;
        public final /* synthetic */ CallbackContext c;

        public c(AisBlePlugin aisBlePlugin, AisWrapper aisWrapper, CallbackContext callbackContext) {
            this.f750b = aisWrapper;
            this.c = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f750b.disconnect();
            this.c.success("成功");
        }
    }

    public class c0 implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ AisWrapper f751b;
        public final /* synthetic */ CallbackContext c;

        public c0(AisBlePlugin aisBlePlugin, AisWrapper aisWrapper, CallbackContext callbackContext) {
            this.f751b = aisWrapper;
            this.c = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f751b.stopScan();
            this.c.success("成功");
        }
    }

    public class d implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f752b;

        public d(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f752b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f752b.error("蓝牙包装对象为空!");
        }
    }

    public class d0 implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f753b;

        public d0(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f753b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f753b.error("蓝牙包装对象为空!");
        }
    }

    public class e implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ AisWrapper f754b;
        public final /* synthetic */ CallbackContext c;

        public e(AisBlePlugin aisBlePlugin, AisWrapper aisWrapper, CallbackContext callbackContext) {
            this.f754b = aisWrapper;
            this.c = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            try {
                JSONObject jSONObject = new JSONObject();
                jSONObject.put("connected", this.f754b.getConnected());
                this.c.success(jSONObject);
            } catch (Exception unused) {
            }
        }
    }

    public class e0 implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f755b;

        public e0(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f755b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f755b.error("蓝牙包装对象为空!");
        }
    }

    public class f implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f756b;

        public f(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f756b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f756b.error("蓝牙包装对象为空!");
        }
    }

    public class f0 implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f757b;

        public f0(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f757b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f757b.error(JsonHelper.result2Json(-1, "蓝牙包装对象为空!"));
        }
    }

    public class g implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ AisWrapper f758b;
        public final /* synthetic */ CallbackContext c;

        public g(AisBlePlugin aisBlePlugin, AisWrapper aisWrapper, CallbackContext callbackContext) {
            this.f758b = aisWrapper;
            this.c = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            ArrayList<String> currentProtocolTypes = this.f758b.getCurrentProtocolTypes();
            JSONArray jSONArray = new JSONArray();
            Iterator<String> it = currentProtocolTypes.iterator();
            while (it.hasNext()) {
                jSONArray.put(it.next());
            }
            this.c.success(jSONArray);
        }
    }

    public class h implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f759b;

        public h(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f759b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f759b.error("蓝牙包装对象为空!");
        }
    }

    public class i implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ AisWrapper f760b;
        public final /* synthetic */ String c;
        public final /* synthetic */ CallbackContext d;

        public i(AisBlePlugin aisBlePlugin, AisWrapper aisWrapper, String str, CallbackContext callbackContext) {
            this.f760b = aisWrapper;
            this.c = str;
            this.d = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f760b.setSessionId(this.c);
            this.d.success("成功");
        }
    }

    public class j implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f761b;

        public j(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f761b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f761b.error("蓝牙包装对象为空!");
        }
    }

    public class k implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f762b;

        public k(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f762b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f762b.error("蓝牙包装对象为空!");
        }
    }

    public class l implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f763b;

        public l(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f763b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f763b.error("蓝牙包装对象为空!");
        }
    }

    public class m implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f764b;

        public m(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f764b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f764b.error("蓝牙包装对象为空!");
        }
    }

    public class n implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f765b;
        public final /* synthetic */ Exception c;

        public n(AisBlePlugin aisBlePlugin, CallbackContext callbackContext, Exception exc) {
            this.f765b = callbackContext;
            this.c = exc;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f765b.success(this.c.getMessage());
        }
    }

    public class o implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f766b;

        public o(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f766b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f766b.error("蓝牙包装对象为空!");
        }
    }

    public class p implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f767b;
        public final /* synthetic */ Exception c;

        public p(AisBlePlugin aisBlePlugin, CallbackContext callbackContext, Exception exc) {
            this.f767b = callbackContext;
            this.c = exc;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f767b.success(this.c.getMessage());
        }
    }

    public class q implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f768b;

        public q(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f768b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f768b.error("蓝牙包装对象为空!");
        }
    }

    public class r implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f769b;
        public final /* synthetic */ Exception c;

        public r(AisBlePlugin aisBlePlugin, CallbackContext callbackContext, Exception exc) {
            this.f769b = callbackContext;
            this.c = exc;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f769b.success(this.c.getMessage());
        }
    }

    public class s implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f770b;

        public s(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f770b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f770b.error("蓝牙包装对象为空!");
        }
    }

    public class t implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f771b;
        public final /* synthetic */ Exception c;

        public t(AisBlePlugin aisBlePlugin, CallbackContext callbackContext, Exception exc) {
            this.f771b = callbackContext;
            this.c = exc;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f771b.success(this.c.getMessage());
        }
    }

    public class u implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f772b;

        public u(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f772b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f772b.error("蓝牙包装对象为空!");
        }
    }

    public class v implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f773b;
        public final /* synthetic */ AisWrapper c;

        public v(AisBlePlugin aisBlePlugin, CallbackContext callbackContext, AisWrapper aisWrapper) {
            this.f773b = callbackContext;
            this.c = aisWrapper;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f773b.success(this.c.getAllDemoProtocolJson());
        }
    }

    public class w implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f774b;
        public final /* synthetic */ Exception c;

        public w(AisBlePlugin aisBlePlugin, CallbackContext callbackContext, Exception exc) {
            this.f774b = callbackContext;
            this.c = exc;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f774b.success(this.c.getMessage());
        }
    }

    public class x implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f775b;

        public x(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f775b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f775b.error("蓝牙包装对象为空!");
        }
    }

    public class y implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f776b;
        public final /* synthetic */ Exception c;

        public y(AisBlePlugin aisBlePlugin, CallbackContext callbackContext, Exception exc) {
            this.f776b = callbackContext;
            this.c = exc;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f776b.success(this.c.getMessage());
        }
    }

    public class z implements Runnable {

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ CallbackContext f777b;

        public z(AisBlePlugin aisBlePlugin, CallbackContext callbackContext) {
            this.f777b = callbackContext;
        }

        @Override // java.lang.Runnable
        public void run() {
            this.f777b.error("蓝牙包装对象为空!");
        }
    }

    @Override // org.apache.cordova.CordovaPlugin
    public boolean execute(String str, JSONArray jSONArray, CallbackContext callbackContext) throws JSONException {
        if (str.equals("getAllDemoJsonProtocol")) {
            AisWrapper aisWrapper = getAisWrapper();
            if (aisWrapper != null) {
                this.cordova.getActivity().runOnUiThread(new v(this, callbackContext, aisWrapper));
                return true;
            }
            this.cordova.getActivity().runOnUiThread(new k(this, callbackContext));
        } else if (str.equals("startScan")) {
            AisWrapper aisWrapper2 = getAisWrapper();
            if (aisWrapper2 != null) {
                this.cordova.getActivity().runOnUiThread(new a0(aisWrapper2, jSONArray.getString(0), callbackContext));
                return true;
            }
            this.cordova.getActivity().runOnUiThread(new z(this, callbackContext));
        } else if (str.equals("stopScan")) {
            AisWrapper aisWrapper3 = getAisWrapper();
            if (aisWrapper3 != null) {
                this.cordova.getActivity().runOnUiThread(new c0(this, aisWrapper3, callbackContext));
                return true;
            }
            this.cordova.getActivity().runOnUiThread(new b0(this, callbackContext));
        } else if (str.equals("getCurrentDevice")) {
            AisWrapper aisWrapper4 = getAisWrapper();
            if (aisWrapper4 != null) {
                callbackContext.success(aisWrapper4.getCurrentDeviceJson());
                return true;
            }
            this.cordova.getActivity().runOnUiThread(new d0(this, callbackContext));
        } else if (str.equals("getJsonDevices")) {
            AisWrapper aisWrapper5 = getAisWrapper();
            if (aisWrapper5 != null) {
                callbackContext.success(aisWrapper5.getDevicesJson());
                return true;
            }
            this.cordova.getActivity().runOnUiThread(new e0(this, callbackContext));
        } else if (str.equals("connect")) {
            AisWrapper aisWrapper6 = getAisWrapper();
            if (aisWrapper6 == null) {
                this.cordova.getActivity().runOnUiThread(new f0(this, callbackContext));
            } else {
                String string = jSONArray.getString(0);
                if (string == null || string.length() == 0) {
                    this.cordova.getActivity().runOnUiThread(new a(this, callbackContext));
                } else {
                    try {
                        aisWrapper6.connect(string, new CordovaWrapper(callbackContext));
                        return true;
                    } catch (b.b.a.e e2) {
                        callbackContext.error(JsonHelper.result2Json(e2.getErrCode(), e2.getMessage()));
                    }
                }
            }
        } else if (str.equals("disconnect")) {
            AisWrapper aisWrapper7 = getAisWrapper();
            if (aisWrapper7 != null) {
                this.cordova.getActivity().runOnUiThread(new c(this, aisWrapper7, callbackContext));
                return true;
            }
            this.cordova.getActivity().runOnUiThread(new b(this, callbackContext));
        } else if (str.equals("getConnected")) {
            AisWrapper aisWrapper8 = getAisWrapper();
            if (aisWrapper8 != null) {
                this.cordova.getActivity().runOnUiThread(new e(this, aisWrapper8, callbackContext));
                return true;
            }
            this.cordova.getActivity().runOnUiThread(new d(this, callbackContext));
        } else if (str.equals("getCurrentProtocolTypes")) {
            AisWrapper aisWrapper9 = getAisWrapper();
            if (aisWrapper9 != null) {
                this.cordova.getActivity().runOnUiThread(new g(this, aisWrapper9, callbackContext));
                return true;
            }
            this.cordova.getActivity().runOnUiThread(new f(this, callbackContext));
        } else if (str.equals("setSessionId")) {
            AisWrapper aisWrapper10 = getAisWrapper();
            if (aisWrapper10 != null) {
                this.cordova.getActivity().runOnUiThread(new i(this, aisWrapper10, jSONArray.getString(0), callbackContext));
                return true;
            }
            this.cordova.getActivity().runOnUiThread(new h(this, callbackContext));
        } else if (str.equals("send")) {
            AisWrapper aisWrapper11 = getAisWrapper();
            if (aisWrapper11 != null) {
                aisWrapper11.send(jSONArray.getString(0), jSONArray.getString(1), new CordovaWrapper(callbackContext));
                return true;
            }
            this.cordova.getActivity().runOnUiThread(new j(this, callbackContext));
        } else if (str.equals("getDeviceRssi")) {
            AisWrapper aisWrapper12 = getAisWrapper();
            if (aisWrapper12 != null) {
                aisWrapper12.getDeviceRssi(new CordovaWrapper(callbackContext));
                return true;
            }
            this.cordova.getActivity().runOnUiThread(new l(this, callbackContext));
        } else if (str.equals("read")) {
            AisWrapper aisWrapper13 = getAisWrapper();
            if (aisWrapper13 == null) {
                this.cordova.getActivity().runOnUiThread(new m(this, callbackContext));
            } else {
                try {
                    aisWrapper13.read(jSONArray.getString(0), new CordovaWrapper(callbackContext));
                    return true;
                } catch (Exception e3) {
                    this.cordova.getActivity().runOnUiThread(new n(this, callbackContext, e3));
                }
            }
        } else if (str.equals("localOADUpdate")) {
            AisWrapper aisWrapper14 = getAisWrapper();
            if (aisWrapper14 == null) {
                this.cordova.getActivity().runOnUiThread(new o(this, callbackContext));
            } else {
                try {
                    aisWrapper14.localOADUpdate(jSONArray.getString(0), new CordovaWrapper(callbackContext));
                    return true;
                } catch (Exception e4) {
                    this.cordova.getActivity().runOnUiThread(new p(this, callbackContext, e4));
                }
            }
        } else if (str.equals("remoteOADUpdate")) {
            AisWrapper aisWrapper15 = getAisWrapper();
            if (aisWrapper15 == null) {
                this.cordova.getActivity().runOnUiThread(new q(this, callbackContext));
            } else {
                try {
                    aisWrapper15.remoteOADUpdate(jSONArray.getString(0), new CordovaWrapper(callbackContext));
                    return true;
                } catch (Exception e5) {
                    this.cordova.getActivity().runOnUiThread(new r(this, callbackContext, e5));
                }
            }
        } else if (str.equals("saveZoneImage")) {
            AisWrapper aisWrapper16 = getAisWrapper();
            if (aisWrapper16 == null) {
                this.cordova.getActivity().runOnUiThread(new s(this, callbackContext));
            } else {
                try {
                    aisWrapper16.saveZoneImage((byte) jSONArray.getInt(0), jSONArray.getString(1), jSONArray.getInt(2), jSONArray.getInt(3), new CordovaWrapper(callbackContext));
                    return true;
                } catch (Exception e6) {
                    this.cordova.getActivity().runOnUiThread(new t(this, callbackContext, e6));
                }
            }
        } else if (str.equals("sendZoneImage")) {
            AisWrapper aisWrapper17 = getAisWrapper();
            if (aisWrapper17 == null) {
                this.cordova.getActivity().runOnUiThread(new u(this, callbackContext));
            } else {
                try {
                    aisWrapper17.sendZoneImage((byte) jSONArray.getInt(0), jSONArray.getString(1), jSONArray.getInt(2), jSONArray.getInt(3), new CordovaWrapper(callbackContext));
                    return true;
                } catch (Exception e7) {
                    this.cordova.getActivity().runOnUiThread(new w(this, callbackContext, e7));
                }
            }
        } else if (str.equals("continueZoneImageSend")) {
            AisWrapper aisWrapper18 = getAisWrapper();
            if (aisWrapper18 == null) {
                this.cordova.getActivity().runOnUiThread(new x(this, callbackContext));
            } else {
                try {
                    aisWrapper18.continueZoneImageSend(new CordovaWrapper(callbackContext));
                    return true;
                } catch (Exception e8) {
                    this.cordova.getActivity().runOnUiThread(new y(this, callbackContext, e8));
                }
            }
        }
        return false;
    }

    public AisWrapper getAisWrapper() {
        InjectActivity injectActivity = (InjectActivity) this.cordova.getActivity();
        if (injectActivity != null) {
            return injectActivity.a();
        }
        return null;
    }
}
