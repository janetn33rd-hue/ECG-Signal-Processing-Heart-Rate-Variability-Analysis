import numpy as np
from scipy.datasets import electrocardiogram
from scipy.signal import butter, sosfilt, find_peaks
import matplotlib.pyplot as plt

ecg_signal = electrocardiogram()
fs = 360  

print(f"Full ECG signal: {len(ecg_signal)} samples at {fs} Hz "
      f"({len(ecg_signal) / fs:.1f} seconds)")



start_time = 30      
duration = 10         
start_sample = int(start_time * fs)     
end_sample = int((start_time + duration) * fs)

ecg_slice = ecg_signal[start_sample:end_sample]


time = np.arange(len(ecg_slice)) / fs + start_time

print(f"Extracted slice: {len(ecg_slice)} samples "
      f"({start_time}s to {start_time + duration}s)")




filter_order = 3         
low_cutoff = 0.5         
high_cutoff = 45.0       
nyquist = fs / 2.0        


low_normalized = low_cutoff / nyquist
high_normalized = high_cutoff / nyquist

sos = butter(
    N=filter_order,
    Wn=[low_normalized, high_normalized],
    btype='bandpass',
    output='sos'
)

ecg_filtered = sosfilt(sos, ecg_slice)

print(f"Applied {filter_order}rd-order Butterworth bandpass filter "
      f"({low_cutoff}–{high_cutoff} Hz)")

min_peak_height = 0.6 * np.max(ecg_filtered)
min_peak_distance = int(0.3 * fs)  # 0.3 seconds → samples

r_peak_indices, peak_properties = find_peaks(
    ecg_filtered,
    height=min_peak_height,
    distance=min_peak_distance
)


r_peak_times = time[r_peak_indices]
r_peak_amplitudes = ecg_filtered[r_peak_indices]

print(f"Detected {len(r_peak_indices)} R-peaks")

if len(r_peak_indices) >= 2:

    rr_intervals = np.diff(r_peak_indices) / fs  


    instantaneous_bpm = 60.0 / rr_intervals
    average_bpm = np.mean(instantaneous_bpm)

    print(f"R-R intervals (s):   {rr_intervals}")
    print(f"Instantaneous BPM:   {np.round(instantaneous_bpm, 1)}")
    print(f"Average heart rate:  {average_bpm:.1f} BPM")
else:
    average_bpm = None
    print("WARNING: Not enough R-peaks detected to compute heart rate.")

if len(r_peak_indices) >= 2:
    rr_intervals_ms = rr_intervals * 1000.0
    sdnn = np.std(rr_intervals_ms, ddof=1)

    successive_diffs = np.diff(rr_intervals_ms)
    rmssd = np.sqrt(np.mean(successive_diffs ** 2))

    mean_rr = np.mean(rr_intervals_ms)
    mean_hr = 60000.0 / mean_rr

    print(f"\nSDNN:  {sdnn:.2f} ms")
    print(f"RMSSD: {rmssd:.2f} ms")
else:
    rr_intervals_ms = None
    sdnn = rmssd = mean_rr = mean_hr = None
    print("WARNING: Not enough R-peaks to compute HRV.")

plt.style.use('seaborn-v0_8-whitegrid')


COLOR_RAW = '#FF6B6B'       
COLOR_SIGNAL = '#2C73D2'   
COLOR_PEAK = '#EE4B2B'     
COLOR_PEAK_EDGE = '#8B0000' 

fig, axes = plt.subplots(
    3, 1,
    figsize=(14, 10),
    gridspec_kw={'height_ratios': [3, 3, 2]}
)

fig.suptitle(
    "ECG Signal Processing & Heart Rate Variability Analysis\n"
    f"10-Second Segment  •  {filter_order}rd-Order Butterworth Bandpass "
    f"({low_cutoff}–{high_cutoff} Hz)  •  Avg HR: {average_bpm:.0f} BPM",
    fontsize=14,
    fontweight='bold',
    y=0.98
)

axes[0].plot(time, ecg_slice, color=COLOR_RAW, alpha=0.4, linewidth=0.7,
             label='Raw ECG', zorder=1)
axes[0].plot(time, ecg_filtered, color=COLOR_SIGNAL, linewidth=1.0,
             label='Filtered ECG', zorder=2)
axes[0].set_ylabel('Amplitude (mV)', fontsize=11)
axes[0].set_xlabel('Time (s)', fontsize=11)
axes[0].set_title('Bandpass Filtering: Raw vs. Cleaned Signal', fontsize=12,
                   fontweight='semibold', pad=8)
axes[0].legend(loc='upper right', fontsize=9, framealpha=0.9)
axes[0].set_xlim(time[0], time[-1])

axes[1].plot(time, ecg_filtered, color=COLOR_SIGNAL, linewidth=1.0,
             label='Filtered ECG', zorder=1)

axes[1].scatter(r_peak_times, r_peak_amplitudes,
                color=COLOR_PEAK, edgecolors=COLOR_PEAK_EDGE, s=80, zorder=3,
                marker='v', linewidths=0.8,
                label=f'R-peaks (n = {len(r_peak_indices)})')

for t_peak in r_peak_times:
    axes[1].axvline(t_peak, color=COLOR_PEAK, alpha=0.15, linewidth=0.8,
                    zorder=0)

axes[1].set_ylabel('Amplitude (mV)', fontsize=11)
axes[1].set_xlabel('Time (s)', fontsize=11)
axes[1].set_title('R-Peak Detection via scipy.signal.find_peaks', fontsize=12,
                   fontweight='semibold', pad=8)
axes[1].legend(loc='upper right', fontsize=9, framealpha=0.9)
axes[1].set_xlim(time[0], time[-1])

if rr_intervals_ms is not None:
    beat_numbers = np.arange(1, len(rr_intervals_ms) + 1)

    axes[2].plot(beat_numbers, rr_intervals_ms, color=COLOR_SIGNAL,
                 linewidth=1.2, marker='o', markersize=6,
                 markerfacecolor=COLOR_SIGNAL, markeredgecolor='white',
                 markeredgewidth=1.2, label='RR Interval', zorder=2)

    axes[2].axhline(mean_rr, color='gray', linestyle='--', linewidth=1.0,
                    alpha=0.7, label=f'Mean: {mean_rr:.0f} ms', zorder=1)


    axes[2].fill_between(
        beat_numbers,
        mean_rr - sdnn, mean_rr + sdnn,
        color=COLOR_SIGNAL, alpha=0.1,
        label=f'±1 SD (SDNN = {sdnn:.1f} ms)', zorder=0
    )

    axes[2].set_ylabel('RR Interval (ms)', fontsize=11)
    axes[2].set_xlabel('Beat Number', fontsize=11)
    axes[2].set_title('RR Interval Tachogram & Variability', fontsize=12,
                       fontweight='semibold', pad=8)
    axes[2].legend(loc='upper right', fontsize=9, framealpha=0.9)
    axes[2].set_xticks(beat_numbers) 
    hrv_textbox = (
        f"Heart Rate:  {average_bpm:.1f} BPM\n"
        f"Mean RR:     {mean_rr:.0f} ms\n"
        f"SDNN:        {sdnn:.1f} ms\n"
        f"RMSSD:       {rmssd:.1f} ms"
    )
    axes[2].text(
        0.02, 0.05, hrv_textbox,
        transform=axes[2].transAxes,
        fontsize=9, fontfamily='monospace',
        verticalalignment='bottom',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow',
                  edgecolor='#CCCCCC', alpha=0.95)
    )
plt.tight_layout(rect=[0, 0, 1, 0.94])

plt.savefig('ecg_analysis_output.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("\nPlot saved to 'ecg_analysis_output.png'")
plt.show()