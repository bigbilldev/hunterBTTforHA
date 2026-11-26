package com.huiyuan.util;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.MediaController;
import android.widget.VideoView;
import androidx.appcompat.app.AppCompatActivity;
import b.b.d.d;
import b.b.d.e;
import java.util.regex.Pattern;

/* JADX INFO: loaded from: classes.dex */
public class FullScreenPlayVideoActivity extends AppCompatActivity {

    /* JADX INFO: renamed from: b, reason: collision with root package name */
    public VideoView f863b;

    public class a implements b.b.d.a<Boolean> {
        public a() {
        }

        @Override // b.b.d.a
        public void apply(Boolean bool) {
            FullScreenPlayVideoActivity.this.a(bool);
        }
    }

    public class b implements b.b.d.a<Boolean> {

        /* JADX INFO: renamed from: a, reason: collision with root package name */
        public final /* synthetic */ Activity f865a;

        public b(FullScreenPlayVideoActivity fullScreenPlayVideoActivity, Activity activity) {
            this.f865a = activity;
        }

        @Override // b.b.d.a
        public void apply(Boolean bool) {
            if (bool.booleanValue()) {
                return;
            }
            UtilHelper.fullScreen(this.f865a);
        }
    }

    public void a(Boolean bool) {
        if (bool.booleanValue()) {
            return;
        }
        UtilHelper.fullScreen(this);
    }

    public void clickJump(View view) {
        Intent intent = new Intent();
        intent.putExtra("skipped", true);
        setResult(-1, intent);
        finish();
    }

    @Override // androidx.appcompat.app.AppCompatActivity, androidx.fragment.app.FragmentActivity, androidx.activity.ComponentActivity, androidx.core.app.ComponentActivity, android.app.Activity
    public void onCreate(Bundle bundle) {
        super.onCreate(bundle);
        setContentView(R$layout.activity_fullscreen_play_video);
        this.f863b = (VideoView) findViewById(R$id.vvPlayer);
        UtilHelper.startMonitorKeyboardState(this, new a());
        setRequestedOrientation(0);
        UtilHelper.fullScreen(this);
        UtilHelper.startMonitorKeyboardState(this, new b(this, this));
        String string = getIntent().getExtras().getString("fileOrUrl");
        if (StringHelper.isEmpty(string)) {
            return;
        }
        try {
            MediaController mediaController = new MediaController(this);
            mediaController.setVisibility(8);
            this.f863b.setMediaController(mediaController);
            if (Pattern.compile("^https{0,1}://.*$", 2).matcher(string).find()) {
                this.f863b.setVideoURI(Uri.parse(string));
            } else {
                this.f863b.setVideoPath(string);
            }
            this.f863b.setOnErrorListener(new d(this));
            this.f863b.setOnCompletionListener(new e(this));
            this.f863b.start();
        } catch (Exception unused) {
            setResult(0);
            finish();
        }
    }
}
