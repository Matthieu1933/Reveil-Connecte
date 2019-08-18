package com.betomaluje.miband.bluetooth;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothProfile;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.util.Log;

import com.betomaluje.miband.ActionCallback;
import com.betomaluje.miband.AppUtils;
import com.betomaluje.miband.model.Profile;
import com.betomaluje.miband.model.UserInfo;

import java.util.HashMap;
import java.util.List;
import java.util.Set;
import java.util.UUID;

/**
 * Created by betomaluje on 6/26/15.
 */
public class BTConnectionManager {

    public interface DataRead {
        public void OnDataRead();
    }

    //the scanning timeout period
    private static final long SCAN_PERIOD = 45000;
    private static BTConnectionManager instance;
    private final String TAG = getClass().getSimpleName();
    private Context context;
    private boolean mScanning = false;
    private boolean mFound = false;
    private boolean mAlreadyPaired = false;
    private boolean isConnected = false;
    private boolean isConnecting = false;
    private boolean isSyncNotification = false;

    private Handler mHandler = new Handler(Looper.getMainLooper());
    private BluetoothAdapter adapter;
    private ActionCallback connectionCallback;

    private BTCommandManager io;
    private BluetoothGatt gatt;

    private DataRead onDataRead;

    private BluetoothAdapter.LeScanCallback mLeScanCallback = new BluetoothAdapter.LeScanCallback() {
        @Override
        public void onLeScan(final BluetoothDevice device, int rssi, byte[] scanRecord) {

            Log.d(TAG,
                    "onLeScan: name: " + device.getName() + ", uuid: "
                            + device.getUuids() + ", add: "
                            + device.getAddress() + ", type: "
                            + device.getType() + ", bondState: "
                            + device.getBondState() + ", rssi: " + rssi);

            if (device.getName() != null && device.getAddress() != null && device.getName().equals("MI") && device.getAddress().startsWith("88:0F:10")) {
                mFound = true;

                stopDiscovery();

                device.connectGatt(context, false, btleGattCallback);
            }
        }
    };

    private Runnable stopRunnable = new Runnable() {
        @Override
        public void run() {
            stopDiscovery();
        }
    };

    public BTConnectionManager(Context context, ActionCallback connectionCallback) {
        this.context = context;

        //Log.i(TAG, "new BTConnectionManager");

        this.connectionCallback = connectionCallback;
    }

    public synchronized static BTConnectionManager getInstance(Context context, ActionCallback connectionCallback) {
        if (instance == null) {
            instance = new BTConnectionManager(context, connectionCallback);
        }

        return instance;
    }

    public void connect() {
        Log.i(TAG, "trying to connect");
        mFound = false;

        BluetoothManager manager = (BluetoothManager) context.getSystemService(Context.BLUETOOTH_SERVICE);
        adapter = manager.getAdapter();

        if (adapter == null || !adapter.isEnabled()) {
            connectionCallback.onFail(NotificationConstants.BLUETOOTH_OFF, "Bluetooth disabled");
            isConnected = false;
            isConnecting = false;
        } else {

            if (!context.getPackageManager().hasSystemFeature(PackageManager.FEATURE_BLUETOOTH_LE)) {
                connectionCallback.onFail(NotificationConstants.BLUETOOTH_OFF, "Bluetooth LE not supported");
                isConnected = false;
                isConnecting = false;
                return;
            }

            if (!isConnecting && !adapter.isDiscovering()) {

                Log.i(TAG, "connecting...");

                isConnecting = true;

                if (!tryPairedDevices()) {

                    Log.i(TAG, "not already paired");
                    mScanning = true;

                    if (AppUtils.supportsBluetoothLE(context)) {
                        //Log.i(TAG, "is BTLE");
                        adapter.stopLeScan(mLeScanCallback);
                        startBTLEDiscovery();
                    } else {
                        //Log.i(TAG, "is BT");
                        adapter.cancelDiscovery();
                        startBTDiscovery();
                    }
                }
            }
        }
    }

    public void toggleNotifications(boolean enable) {
        if (gatt == null) return;

        HashMap<UUID, BluetoothGattCharacteristic> mAvailableCharacteristics = null;

        for (BluetoothGattService service : gatt.getServices()) {
            if (Profile.UUID_SERVICE_MILI.equals(service.getUuid())) {
                List<BluetoothGattCharacteristic> characteristics = service.getCharacteristics();
                if (characteristics == null || characteristics.isEmpty()) {
                    Log.e(TAG, "Supported LE service " + service.getUuid() + "did not return any characteristics");
                    continue;
                }
                mAvailableCharacteristics = new HashMap<>(characteristics.size());
                for (BluetoothGattCharacteristic characteristic : characteristics) {
                    mAvailableCharacteristics.put(characteristic.getUuid(), characteristic);
                }
            }
        }

        try {
            if (mAvailableCharacteristics != null && !mAvailableCharacteristics.isEmpty()) {

                isSyncNotification = enable;

                gatt.setCharacteristicNotification(mAvailableCharacteristics.get(Profile.UUID_CHAR_NOTIFICATION), enable);
                gatt.setCharacteristicNotification(mAvailableCharacteristics.get(Profile.UUID_CHAR_REALTIME_STEPS), enable);
                gatt.setCharacteristicNotification(mAvailableCharacteristics.get(Profile.UUID_CHAR_ACTIVITY_DATA), enable);
                gatt.setCharacteristicNotification(mAvailableCharacteristics.get(Profile.UUID_CHAR_BATTERY), enable);
                gatt.setCharacteristicNotification(mAvailableCharacteristics.get(Profile.UUID_CHAR_SENSOR_DATA), enable);
            }
        } catch (NullPointerException e) {

        }
    }

    public void disconnect() {
        if (gatt != null) {
            gatt.disconnect();
        }

        isConnected = false;
        isConnecting = false;

        connectionCallback.onFail(-1, "disconnected");
    }

    public void dispose() {
        if (gatt != null) {
            gatt.close();
            gatt = null;
        }

        isConnected = false;
        isConnecting = false;

        connectionCallback.onFail(-1, "disconnected");
    }

    private boolean tryPairedDevices() {
        String mDeviceAddress = "";
        mAlreadyPaired = false;

        SharedPreferences sharedPreferences = context.getSharedPreferences(UserInfo.KEY_PREFERENCES, Context.MODE_PRIVATE);
        String btAddress = sharedPreferences.getString(UserInfo.KEY_BT_ADDRESS, "");

        if (btAddress != null) {
            if (!btAddress.equals("")) {
                //we use our previously paired device
                //mFound = true;
                mAlreadyPaired = true;
                mDeviceAddress = btAddress;
            } else {
                //we search for paired devices
                final Set<BluetoothDevice> pairedDevices = adapter.getBondedDevices();

                for (BluetoothDevice pairedDevice : pairedDevices) {
                    if (pairedDevice.getName().equals("MI") && pairedDevice.getAddress().startsWith("88:0F:10")) {
                        mDeviceAddress = pairedDevice.getAddress();
                        //mFound = true;
                        mAlreadyPaired = true;
                        break;
                    }
                }
            }

            if (mAlreadyPaired && !mDeviceAddress.equals("")) {
                mDeviceAddress = btAddress;
            } else {
                mAlreadyPaired = false;
            }
        } else {
            //we search only for paired devices
            final Set<BluetoothDevice> pairedDevices = adapter.getBondedDevices();

            for (BluetoothDevice pairedDevice : pairedDevices) {
                if (pairedDevice.getName().equals("MI") && pairedDevice.getAddress().startsWith("88:0F:10")) {
                    mDeviceAddress = pairedDevice.getAddress();
                    //mFound = true;
                    mAlreadyPaired = true;
                    break;
                }
            }
        }

        if (mDeviceAddress.equals(""))
            mAlreadyPaired = false;

        if (mAlreadyPaired) {
            //Log.i(TAG, "already paired!");
            BluetoothDevice mBluetoothMi = adapter.getRemoteDevice(mDeviceAddress);
            mBluetoothMi.connectGatt(context, false, btleGattCallback);
            //mGatt.connect();
        }

        return mAlreadyPaired;
    }

    public boolean isAlreadyPaired() {
        return mAlreadyPaired;
    }

    public boolean isConnected() {
        return isConnected && adapter.isEnabled();
    }

    public boolean isSyncNotification() {
        return isSyncNotification;
    }

    public BluetoothDevice getDevice() {
        return gatt.getDevice();
    }

    public BluetoothGatt getGatt() {
        return gatt;
    }

    public void setIo(BTCommandManager io) {
        this.io = io;
        onDataRead = io.getmQueueConsumer();
    }

    private final BluetoothGattCallback btleGattCallback = new BluetoothGattCallback() {

        @Override
        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
            super.onConnectionStateChange(gatt, status, newState);

            //Log.e(TAG, "onConnectionStateChange (2): " + newState);

            BTConnectionManager.this.gatt = gatt;

            if (status == BluetoothGatt.GATT_SUCCESS && newState == BluetoothProfile.STATE_CONNECTED) {
                gatt.discoverServices();
            } else if (status == BluetoothGatt.GATT_SUCCESS && newState == BluetoothProfile.STATE_DISCONNECTED) {
                //Log.e(TAG, "onConnectionStateChange disconnect: " + newState);
                //toggleNotifications(false);
                //disconnect();
            } else if (status != BluetoothGatt.GATT_SUCCESS) {
                gatt.disconnect();
            }
        }

        @Override
        public void onServicesDiscovered(BluetoothGatt gatt, int status) {
            super.onServicesDiscovered(gatt, status);

            //Log.e(TAG, "onServicesDiscovered (0): " + status + " paired: " + isAlreadyPaired());

            if (status == BluetoothGatt.GATT_SUCCESS) {
                stopDiscovery();

                //we update current band bluetooth MAC address
                SharedPreferences sharedPrefs = context.getSharedPreferences(UserInfo.KEY_PREFERENCES, Context.MODE_PRIVATE);
                SharedPreferences.Editor editor = sharedPrefs.edit();
                editor.putString(UserInfo.KEY_BT_ADDRESS, gatt.getDevice().getAddress());

                editor.commit();

                //we set the Gatt instance
                BTConnectionManager.this.gatt = gatt;

                isConnected = true;
                //toggleNotifications(true);
                connectionCallback.onSuccess(isAlreadyPaired());
            } else {
                //disconnect();
            }
        }

        @Override
        public void onCharacteristicRead(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic, int status) {
            super.onCharacteristicRead(gatt, characteristic, status);
            if (BluetoothGatt.GATT_SUCCESS == status) {
                if (io != null)
                    io.onSuccess(characteristic);
            } else {
                io.onFail(status, "onCharacteristicRead fail");
            }
        }

        @Override
        public void onCharacteristicWrite(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic, int status) {
            super.onCharacteristicWrite(gatt, characteristic, status);

            //if status is 0, success on sending and received
            //Log.i(TAG, "handleControlPoint got status:" + status);

            if (BluetoothGatt.GATT_SUCCESS == status) {
                io.onSuccess(characteristic);

                if (characteristic.getUuid().equals(Profile.UUID_CHAR_CONTROL_POINT)) {
                    io.handleControlPointResult(characteristic.getValue());
                }

            } else {
                io.onFail(status, "onCharacteristicWrite fail");
            }

            if (onDataRead != null)
                onDataRead.OnDataRead();
        }

        @Override
        public void onReadRemoteRssi(BluetoothGatt gatt, int rssi, int status) {
            super.onReadRemoteRssi(gatt, rssi, status);
            if (BluetoothGatt.GATT_SUCCESS == status) {
                io.onSuccess(rssi);
            } else {
                io.onFail(status, "onCharacteristicRead fail");
            }
        }

        @Override
        public void onCharacteristicChanged(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic) {
            super.onCharacteristicChanged(gatt, characteristic);
            if (io.notifyListeners.containsKey(characteristic.getUuid())) {
                io.notifyListeners.get(characteristic.getUuid()).onNotify(characteristic.getValue());
            }

            UUID characteristicUUID = characteristic.getUuid();
            if (Profile.UUID_CHAR_ACTIVITY_DATA.equals(characteristicUUID)) {
                io.handleActivityNotif(characteristic.getValue());
            }

            toggleNotifications(false);
        }
    };

    /*
     *
     *
     * DISCOVERY REGION
     *
     *
     */

    private void stopDiscovery() {
        Log.i(TAG, "Stopping discovery");
        isConnecting = false;

        //if (mScanning) {
        if (AppUtils.supportsBluetoothLE(context)) {
            stopBTLEDiscovery();
        } else {
            stopBTDiscovery();
        }

        mHandler.removeMessages(0, stopRunnable);
        mScanning = false;

        if (!mFound)
            connectionCallback.onFail(-1, "No bluetooth devices");
        //}
    }

    private void startBTDiscovery() {
        Log.i(TAG, "Starting BT Discovery");
        mHandler.removeMessages(0, stopRunnable);
        mHandler.sendMessageDelayed(getPostMessage(stopRunnable), SCAN_PERIOD);
        stopBTDiscovery();
        if (adapter.startDiscovery())
            Log.v(TAG, "starting scan");
    }

    private void startBTLEDiscovery() {
        Log.i(TAG, "Starting BTLE Discovery");
        mHandler.removeMessages(0, stopRunnable);
        mHandler.sendMessageDelayed(getPostMessage(stopRunnable), SCAN_PERIOD);
        stopBTLEDiscovery();
        if (adapter.startLeScan(mLeScanCallback))
            Log.v(TAG, "starting scan");
    }

    private void stopBTLEDiscovery() {
        if (adapter.isDiscovering())
            adapter.stopLeScan(mLeScanCallback);
    }

    private void stopBTDiscovery() {
        if (adapter.isDiscovering())
            adapter.cancelDiscovery();
    }

    private Message getPostMessage(Runnable runnable) {
        Message m = Message.obtain(mHandler, runnable);
        m.obj = runnable;
        return m;
    }
}
