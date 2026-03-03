import { createStore } from "/js/AlpineStore.js";

/** Browsers allow getUserMedia only in secure contexts: HTTPS or localhost. */
export function isSecureContextForMicrophone() {
    if (typeof window === "undefined" || !window.location) return false;
    const { protocol, hostname } = window.location;
    if (protocol === "https:") return true;
    if (protocol === "http:" && (hostname === "localhost" || hostname === "127.0.0.1")) return true;
    return false;
}

export const MICROPHONE_INSECURE_MESSAGE =
    "Microphone requires a secure connection. Use https:// for this server, or open the app at http://localhost:8888 (same machine).";

const model = {


    devices: [],
    selectedDevice: "",

    async init() {
        // Load selected device from localStorage if present
        const saved = localStorage.getItem('microphoneSelectedDevice');
        await this.loadDevices();
        if (saved && this.devices.some(d => d.deviceId === saved)) {
            this.selectedDevice = saved;
        }
    },

    async loadDevices() {
        // Get media devices
        const devices = await navigator.mediaDevices.enumerateDevices();
        // Filter for audio input (microphones)
        this.devices = devices.filter(d => d.kind === "audioinput" && d.deviceId);
        // Set selected device to first available, if any
        this.selectedDevice = this.devices.length > 0 ? this.devices[0].deviceId : "";
    },

    // track permission request state
    requestingPermission: false,
    permissionTimer: null,
    permissionAttempts: 0,
    
    // request microphone permission and poll for devices
    async requestPermission() {
        if (!isSecureContextForMicrophone()) {
            if (typeof window !== "undefined" && window.toastFrontendError) {
                window.toastFrontendError(MICROPHONE_INSECURE_MESSAGE, "Microphone unavailable");
            }
            return;
        }
        // set flag first so UI can update immediately
        clearTimeout(this.permissionTimer);
        this.requestingPermission = true;
        this.permissionAttempts = 0;
        
        // request permission in next tick to allow UI to update
        setTimeout(async () => {
            try {
                await navigator.mediaDevices.getUserMedia({ audio: true });
                // start polling for devices
                this.pollForDevices();
            } catch (err) {
                console.error("Microphone permission denied", err);
                if (!isSecureContextForMicrophone() && window.toastFrontendError) {
                    window.toastFrontendError(MICROPHONE_INSECURE_MESSAGE, "Microphone unavailable");
                }
                this.requestingPermission = false;
            }
        }, 0);
    },
    
    // poll for devices until found or timeout (60s)
    async pollForDevices() {
        await this.loadDevices();
        
        // check if we found devices with valid IDs
        if (this.devices.some(d => d.deviceId && d.deviceId !== "") || this.permissionAttempts >= 60) {
            this.requestingPermission = false;
            return;
        }
        
        // continue polling
        this.permissionAttempts++;
        this.permissionTimer = setTimeout(() => this.pollForDevices(), 1000);
    },

    async selectDevice(deviceId) {
        this.selectedDevice = deviceId;
        this.onSelectDevice();
    },

    async onSelectDevice() {
        localStorage.setItem('microphoneSelectedDevice', this.selectedDevice);
    },

    getSelectedDevice() {
        let device = this.devices.find(d => d.deviceId === this.selectedDevice);
        if (!device && this.devices.length > 0) {
            device = this.devices.find(d => d.deviceId === "default") || this.devices[0];
        }
        return device;
    },

    /** For UI: message to show when microphone is blocked (HTTP non-localhost). Null if secure. */
    getInsecureContextMessage() {
        return isSecureContextForMicrophone() ? null : MICROPHONE_INSECURE_MESSAGE;
    },

};

const store = createStore("microphoneSetting", model);

export { store };
