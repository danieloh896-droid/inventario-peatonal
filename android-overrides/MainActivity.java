package co.edu.univalle.inventariopeatonal;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(ReceptorPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
