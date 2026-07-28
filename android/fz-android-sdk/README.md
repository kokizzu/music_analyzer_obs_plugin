# Fret Zealot Android SDK compatibility module

This module is a focused Android 15-compatible adaptation of the Apache-2.0
[`edgetechlabs/fz-android-sdk`](https://github.com/edgetechlabs/fz-android-sdk)
core BLE API at commit `6da6d1b`.

It preserves the SDK-facing `LEDBLELib`, `LEDBLELibCallback`,
`BluetoothLeService`, and `SampleGattAttributes` surface used by the app while
omitting the obsolete support-library UI and Nordic DFU example dependencies.
The service uses direct in-process callbacks instead of the SDK's legacy global
broadcasts, and supports both the original and Fret Zealot 2 LED
characteristics.

The upstream module declares Apache-2.0. This adaptation preserves that license
and attribution; the complete terms are in [`LICENSE`](LICENSE).
