"use client";

class SoundManager {
    private static instance: SoundManager;
    private audioContext: AudioContext | null = null;

    private constructor() {
        if (typeof window !== "undefined") {
            this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        }
    }

    public static getInstance(): SoundManager {
        if (!SoundManager.instance) {
            SoundManager.instance = new SoundManager();
        }
        return SoundManager.instance;
    }

    public playHover() {
        this.playTone(400, 0.05, "sine", 0.05);
    }

    public playClick() {
        this.playTone(800, 0.1, "square", 0.1);
        setTimeout(() => this.playTone(600, 0.1, "square", 0.1), 50);
    }

    public playSuccess() {
        this.playTone(600, 0.1, "sine", 0.1);
        setTimeout(() => this.playTone(800, 0.1, "sine", 0.1), 100);
        setTimeout(() => this.playTone(1200, 0.3, "sine", 0.1), 200);
    }

    private playTone(freq: number, duration: number, type: OscillatorType, volume: number) {
        if (!this.audioContext) return;

        const osc = this.audioContext.createOscillator();
        const gain = this.audioContext.createGain();

        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.audioContext.currentTime);

        gain.gain.setValueAtTime(volume, this.audioContext.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);

        osc.connect(gain);
        gain.connect(this.audioContext.destination);

        osc.start();
        osc.stop(this.audioContext.currentTime + duration);
    }
}

export const sfx = SoundManager.getInstance();
