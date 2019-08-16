package com.betomaluje.miband;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGattCharacteristic;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import com.betomaluje.miband.bluetooth.BLEAction;
import com.betomaluje.miband.bluetooth.BLETask;
import com.betomaluje.miband.bluetooth.BTCommandManager;
import com.betomaluje.miband.bluetooth.BTConnectionManager;
import com.betomaluje.miband.bluetooth.MiBandWrapper;
import com.betomaluje.miband.bluetooth.NotificationConstants;
import com.betomaluje.miband.bluetooth.WaitAction;
import com.betomaluje.miband.bluetooth.WriteAction;
import com.betomaluje.miband.colorpicker.ColorPickerDialog;
import com.betomaluje.miband.model.BatteryInfo;
import com.betomaluje.miband.model.LedColor;
import com.betomaluje.miband.model.Profile;
import com.betomaluje.miband.model.Protocol;
import com.betomaluje.miband.model.UserInfo;
import com.betomaluje.miband.model.VibrationMode;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

public class MiBand {

    private static final String TAG = "miband-android";
    private static Context context;
    private static BTCommandManager io;
    private static MiBand instance;
    private static MiBandWrapper miBandWrapper;
    private static Intent miBandService;
    private static BTConnectionManager btConnectionManager;
    private ActionCallback connectionCallback;

    public MiBand(final Context context) {
        MiBand.context = context;
        MiBand.miBandWrapper = MiBandWrapper.getInstance(context);

        ActionCallback myConnectionCallback = new ActionCallback() {
            @Override
            public void onSuccess(Object data) {
                Log.d(TAG, "Connection success, now pair: " + data);

                //only once we are paired, we create the BluetoothIO object to communicate with Mi Band
                io = new BTCommandManager(context, btConnectionManager.getGatt());
                btConnectionManager.setIo(io);

                setUserInfo(UserInfo.getSavedUser(context));
                if (connectionCallback != null)
                    connectionCallback.onSuccess(null);
            }

            @Override
            public void onFail(int errorCode, String msg) {
                Log.e(TAG, "Fail: " + msg);
                if (connectionCallback != null)
                    connectionCallback.onFail(errorCode, msg);
            }
        };

        MiBand.btConnectionManager = BTConnectionManager.getInstance(context, myConnectionCallback);
    }

    public synchronized static MiBand getInstance(Context context) {
        if (instance == null) {
            instance = new MiBand(context);
        } else {
            MiBand.context = context;
        }

        return instance;
    }

    public static void initService(Context context) {
        miBandService = new Intent(context, MiBandService.class);
        miBandService.setAction(NotificationConstants.MI_BAND_CONNECT);
        context.startService(miBandService);
    }

    public static void sendAction(final int action) {
        if (miBandWrapper == null) return;
        miBandWrapper.sendAction(action);
    }

    public static void sendAction(final int action, HashMap<String, ? extends Object> params) {
        if (miBandWrapper == null) return;
        miBandWrapper.sendAction(action, params);
    }

    public static void disconnect() {
        Log.e(TAG, "Disconnecting Mi Band...");
        if (miBandService != null)
            MiBand.context.stopService(miBandService);
        btConnectionManager.disconnect();
    }

    public static void dispose() {
        Log.e(TAG, "Disposing Mi Band...");
        if (miBandService != null)
            MiBand.context.stopService(miBandService);
        btConnectionManager.dispose();
    }

    /**
     * Android device will automatically search for nearby Mi Band, automatic connection, because the hand will have only one Mi Band,
     * currently only supports the search to case a bracelet
     *
     * @param callback
     */
    public void connect(final ActionCallback callback) {
        if (!isConnected()) {
            connectionCallback = callback;
            btConnectionManager.connect();
        } else {
            Log.e(TAG, "Already connected...");
        }
    }

    private void checkConnection() {
        if (!isConnected()) {
            Log.e(TAG, "Not connected... Waiting for new connection...");
            btConnectionManager.connect();
        }
    }

    /**
     * Checks if the connection is already done with the Mi Band
     *
     * @return if the Mi Band is connected
     */
    public boolean isConnected() {
        return btConnectionManager.isConnected();
    }

    /**
     * Pairs with Mi Band, for practical purposes unknown, mismatch can also do other operation.
     */
    public void pair() {
        Log.d(TAG, "Pairing...");

        ActionCallback ioCallback = new ActionCallback() {

            @Override
            public void onSuccess(Object data) {
                BluetoothGattCharacteristic characteristic = (BluetoothGattCharacteristic) data;
                //Log.d(TAG, "pair result " + Arrays.toString(characteristic.getValue()));
                if (characteristic.getValue().length == 1 && characteristic.getValue()[0] == 2) {
                    Log.d(TAG, "Pairing success!");

                    setUserInfo(UserInfo.getSavedUser(context));

                    //setUserInfo(null);
                    if (connectionCallback != null)
                        connectionCallback.onSuccess(null);
                } else {
                    if (connectionCallback != null)
                        connectionCallback.onFail(-1, "failed to pair with Mi Band");
                }
            }

            @Override
            public void onFail(int errorCode, String msg) {
                if (connectionCallback != null)
                    connectionCallback.onFail(errorCode, msg);
            }
        };

        MiBand.io.writeAndRead(Profile.UUID_CHAR_PAIR, Protocol.PAIR, ioCallback);
    }

    /**
     * Signal strength reading and the connected device RSSI value
     *
     * @param callback
     */
    public void readRssi(ActionCallback callback) {
        checkConnection();
        MiBand.io.readRssi(callback);
    }

    /**
     * Read band battery information
     */
    public void getBatteryInfo(final ActionCallback callback) {
        checkConnection();

        ActionCallback ioCallback = new ActionCallback() {
            @Override
            public void onSuccess(Object data) {
                BluetoothGattCharacteristic characteristic = (BluetoothGattCharacteristic) data;
                Log.d(TAG, "getBatteryInfo result " + Arrays.toString(characteristic.getValue()));
                if (characteristic.getValue().length == 10) {
                    BatteryInfo info = BatteryInfo.fromByteData(characteristic.getValue());
                    callback.onSuccess(info);
                } else {
                    callback.onFail(-1, "result format wrong!");
                }
            }

            @Override
            public void onFail(int errorCode, String msg) {
                callback.onFail(errorCode, msg);
            }
        };
        MiBand.io.readCharacteristic(Profile.UUID_CHAR_BATTERY, ioCallback);
    }

    /**
     * Let band vibrate
     */
    public void startVibration(VibrationMode mode) {
        checkConnection();

        //TODO see if new firmware or not

        byte[] protocal;
        switch (mode) {
            case VIBRATION_WITH_LED:
                protocal = Protocol.VIBRATION_WITH_LED;
                break;
            case VIBRATION_UNTIL_CALL_STOP:
                protocal = Protocol.VIBRATION_UNTIL_CALL_STOP;
                break;
            case VIBRATION_WITHOUT_LED:
                protocal = Protocol.VIBRATION_WITHOUT_LED;
                break;
            case VIBRATION_NEW_FIRMWARE:
                protocal = Protocol.VIBRATION_NEW_FIRMWARE;
                break;
            default:
                return;
        }

        final List<BLEAction> list = new ArrayList<>();
        list.add(new WriteAction(Profile.UUID_SERVICE_VIBRATE, Profile.UUID_CHAR_ALERT_LEVEL, protocal));

        queue(list);
    }

    /**
     * Vibrate "times" times. Each iteration will start vibrator "on_time" milliseconds (up to 500, will be truncated if larger), and then stop it "off_time" milliseconds (no limit here).
     *
     * @param times   : the amount of times to vibrate
     * @param onTime  : the time in milliseconds that each vibration will last (maximum of 500 milliseconds). Preferably more than 100 milliseconds
     * @param offTime : the time in milliseconds that each cycle will last
     */
    public synchronized void customVibration(final int times, final int onTime, final int offTime) {
        final int newOnTime = Math.min(onTime, 500);

        List<BLEAction> list = new ArrayList<>();

        for (int i = 1; i <= times; i++) {

            list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, Protocol.VIBRATION_UNTIL_CALL_STOP));
            list.add(new WaitAction(newOnTime));
            list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, Protocol.STOP_VIBRATION));
            list.add(new WaitAction(offTime));
        }

        queue(list);
    }

    /**
     * Stops a vibration
     */
    public void stopVibration() {
        checkConnection();

        //MiBand.io.writeCharacteristic(Profile.UUID_CHAR_CONTROL_POINT, Protocol.STOP_VIBRATION, null);

        final List<BLEAction> list = new ArrayList<>();
        list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, Protocol.STOP_VIBRATION));

        queue(list);
    }

    public void setNormalNotifyListener(NotifyListener listener) {
        MiBand.io.setNotifyListener(Profile.UUID_CHAR_NOTIFICATION, listener);
    }

    /**
     * Sets the listener for steps in real time. Use {@link MiBand#enableRealtimeStepsNotify} to start it and {@link MiBand#disableRealtimeStepsNotify} to stop it.
     *
     * @param listener
     */
    public void setRealtimeStepsNotifyListener(final RealtimeStepsNotifyListener listener) {
        checkConnection();

        MiBand.io.setNotifyListener(Profile.UUID_CHAR_REALTIME_STEPS, new NotifyListener() {

            @Override
            public void onNotify(byte[] data) {
                Log.d(TAG, Arrays.toString(data));
                if (data.length == 4) {
                    int steps = data[3] << 24 | (data[2] & 0xFF) << 16 | (data[1] & 0xFF) << 8 | (data[0] & 0xFF);
                    listener.onNotify(steps);
                }
            }
        });
    }

    /**
     * Starts listening to step count in real time
     */
    public void enableRealtimeStepsNotify() {
        checkConnection();

        //MiBand.io.writeCharacteristic(Profile.UUID_CHAR_CONTROL_POINT, Protocol.ENABLE_REALTIME_STEPS_NOTIFY, null);

        final List<BLEAction> list = new ArrayList<>();
        list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, Protocol.ENABLE_REALTIME_STEPS_NOTIFY));

        final BLETask task = new BLETask(list);

        queue(list);
    }

    /**
     * Stops listening to step count in real time
     */
    public void disableRealtimeStepsNotify() {
        checkConnection();

        //MiBand.io.writeCharacteristic(Profile.UUID_CHAR_CONTROL_POINT, Protocol.DISABLE_REALTIME_STEPS_NOTIFY, null);

        final List<BLEAction> list = new ArrayList<>();
        list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, Protocol.DISABLE_REALTIME_STEPS_NOTIFY));

        queue(list);
    }

    /**
     * Sets the led light color. Flashes the LED's by default
     *
     * @param color : the given {@link LedColor} color
     */
    public void setLedColor(LedColor color) {
        setLedColor(color, true);
    }

    /**
     * Sets the led light color.
     *
     * @param color      : the given {@link LedColor} color
     * @param quickFlash : <b>true</b> if you want the band's LED's to flash, <b>false</b> otherwise
     */
    public void setLedColor(LedColor color, boolean quickFlash) {
        byte[] protocal;
        switch (color) {
            case RED:
                protocal = Protocol.COLOR_RED;
                break;
            case BLUE:
                protocal = Protocol.COLOR_BLUE;
                break;
            case GREEN:
                protocal = Protocol.COLOR_GREEN;
                break;
            case ORANGE:
                protocal = Protocol.COLOR_ORANGE;
                break;
            case TEST:
                protocal = Protocol.COLOR_TEST;
                break;
            default:
                return;
        }

        protocal[protocal.length - 1] = quickFlash ? (byte) 1 : (byte) 0;

        setColor(protocal);
    }

    /**
     * Sets the LED color. Flashes the LED's by default
     *
     * @param rgb : an <b>int</b> that represents the rgb value (use {@link ColorPickerDialog} to select a value)
     */
    public void setLedColor(int rgb) {
        setLedColor(rgb, true);
    }

    /**
     * Sets the LED color.
     *
     * @param rgb        : an <b>int</b> that represents the rgb value (use {@link ColorPickerDialog} to select a value)
     * @param quickFlash : <b>true</b> if you want the band's LED's to flash, <b>false</b> otherwise
     */
    public void setLedColor(int rgb, boolean quickFlash) {
        byte[] colors = convertRgb(rgb, quickFlash);
        setColor(colors);
    }

    /**
     * Actually sends the color to the Mi Band
     *
     * @param color
     */
    private void setColor(byte[] color) {
        checkConnection();

        final List<BLEAction> list = new ArrayList<>();
        list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, color));

        queue(list);
    }

    private byte[] convertRgb(int rgb) {
        return convertRgb(rgb, true);
    }

    private byte[] convertRgb(int rgb, boolean quickFlash) {
        final int red = ((rgb >> 16) & 0x0ff) / 42;
        final int green = ((rgb >> 8) & 0x0ff) / 42;
        final int blue = ((rgb) & 0x0ff) / 42;

        return new byte[]{14, (byte) red, (byte) green, (byte) blue, quickFlash ? (byte) 1 : (byte) 0};
    }

    /**
     * Sends a custom notification to the Mi Band
     */
    public synchronized void setLedColor(final int flashTimes, final int flashColour, final int flashDuration) {

        final List<BLEAction> list = new ArrayList<>();

        byte[] colors = convertRgb(flashColour);
        byte[] protocalOff = {14, colors[0], colors[1], colors[2], 0};

        for (int i = 1; i <= flashTimes; i++) {
            list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, colors));
            list.add(new WaitAction(flashDuration));
            list.add((new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, protocalOff)));
            list.add(new WaitAction(flashDuration));
        }

        queue(list);
    }

    public synchronized void notifyBand(final int flashColour) {
        List<BLEAction> list = new ArrayList<>();

        byte[] colors = convertRgb(flashColour);
        list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, Protocol.VIBRATION_WITHOUT_LED));
        list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, colors));
        queue(list);
    }

    private void queue(List<BLEAction> list) {
        final BLETask task = new BLETask(list);

        try {
            io.queueTask(task);
        } catch (NullPointerException ignored) {

        }
    }

    /**
     * Notifies the Mi Band with vibration and colour.
     * Vibrate and flashes the colour "times" times. Each iteration will start "on_time" milliseconds (up to 500, will be truncated if larger), and then stop it "off_time" milliseconds (no limit here).
     *
     * @param times       : the amount of times to vibrate
     * @param onTime      : the time in milliseconds that each vibration will last (maximum of 500 milliseconds). Preferably more than 100 milliseconds
     * @param offTime     : the time in milliseconds that each cycle will last
     * @param flashColour int value of the colour to flash
     */
    public synchronized void notifyBand(final int times, final int onTime, final int offTime, final int flashColour) {
        //final int newOnTime = Math.min(onTime, 500);

        final List<BLEAction> list = new ArrayList<>();

        byte[] colors = convertRgb(flashColour);

        list.add(new WaitAction(150));
        list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, Protocol.VIBRATION_WITHOUT_LED));
        list.add(new WaitAction(300));
        list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, colors));

        /*
        for (int i = 1; i <= times; i++) {
            //vibration part
            list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, Protocol.VIBRATION_WITHOUT_LED));
            //list.add(new WaitAction(newOnTime));
            //list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, Protocol.STOP_VIBRATION));
            list.add(new WaitAction(offTime));
        }
        */

        queue(list);
    }

    /**
     * Sets up the user information. If there's no UserInfo provided, we create one by default
     *
     * @param userInfo
     */
    public void setUserInfo(UserInfo userInfo) {
        checkConnection();

        BluetoothDevice device = btConnectionManager.getDevice();

        if (userInfo == null) {
            userInfo = UserInfo.getDefault(device.getAddress(), context);
        }

        final List<BLEAction> list = new ArrayList<>();
        list.add(new WriteAction(Profile.UUID_CHAR_USER_INFO, userInfo.getData()));

        queue(list);
    }

    public void setUserInfo(int gender, int age, int height, int weight, String alias) {
        UserInfo user = UserInfo.create(btConnectionManager.getDevice().getAddress(), gender, age, height, weight, alias, 0);
        //MiBand.io.writeCharacteristic(Profile.UUID_CHAR_USER_INFO, user.getData(), null);

        final List<BLEAction> list = new ArrayList<>();
        list.add(new WriteAction(Profile.UUID_CHAR_USER_INFO, user.getData()));

        queue(list);
    }

    /**
     * Your Mi Band will do crazy things (LED flashing, vibrate).
     * Note: This will remove bonding information on the Mi Band, which might confused Android.
     * So before you connect next time remove your Mi Band via Settings, Bluetooth.
     */
    public void selfTest() {
        checkConnection();

        //MiBand.io.writeCharacteristic(Profile.UUID_CHAR_TEST, Protocol.SELF_TEST, null);

        final List<BLEAction> list = new ArrayList<>();
        list.add(new WriteAction(Profile.UUID_CHAR_TEST, Protocol.SELF_TEST));

        queue(list);
    }

    public void startListeningSync(ActionCallback actionCallback) {
        btConnectionManager.toggleNotifications(true);
        final List<BLEAction> list = new ArrayList<>();
        list.add(new WriteAction(Profile.UUID_CHAR_CONTROL_POINT, Protocol.FETCH_DATA, actionCallback));

        queue(list);
    }

    public void stopListeningSync() {
        btConnectionManager.toggleNotifications(false);
    }

    public boolean isSyncNotification() {
        return btConnectionManager.isSyncNotification();
    }
}
