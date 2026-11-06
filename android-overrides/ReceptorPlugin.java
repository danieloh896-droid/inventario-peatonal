package co.edu.univalle.inventariopeatonal;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.NetworkRequest;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

/** Lee el receptor por la red WiFi aunque Android prefiera los datos móviles (WiFi sin internet). */
@CapacitorPlugin(name = "Receptor")
public class ReceptorPlugin extends Plugin {
    private volatile Network wifi;

    @Override
    public void load() {
        ConnectivityManager cm = (ConnectivityManager) getContext().getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkRequest req = new NetworkRequest.Builder()
                .addTransportType(NetworkCapabilities.TRANSPORT_WIFI).build();
        cm.requestNetwork(req, new ConnectivityManager.NetworkCallback() {
            @Override public void onAvailable(Network n) { wifi = n; }
            @Override public void onLost(Network n) { if (n.equals(wifi)) wifi = null; }
        });
    }

    @PluginMethod
    public void get(final PluginCall call) {
        final String url = call.getString("url");
        new Thread(() -> {
            try {
                Network n = wifi;
                URL u = new URL(url);
                HttpURLConnection c = (HttpURLConnection) (n != null ? n.openConnection(u) : u.openConnection());
                c.setConnectTimeout(2500);
                c.setReadTimeout(2500);
                int code = c.getResponseCode();
                InputStream in = c.getInputStream();
                ByteArrayOutputStream out = new ByteArrayOutputStream();
                byte[] buf = new byte[4096];
                int r;
                while ((r = in.read(buf)) > 0) out.write(buf, 0, r);
                in.close();
                c.disconnect();
                JSObject o = new JSObject();
                o.put("status", code);
                o.put("data", out.toString("UTF-8"));
                o.put("viaWifi", n != null);
                call.resolve(o);
            } catch (Exception e) {
                call.reject(String.valueOf(e.getMessage()));
            }
        }).start();
    }
}
