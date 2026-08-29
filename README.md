# ECG-Signal-Processing-Heart-Rate-Variability-Analysis
A Python project that processes electrocardiogram (ECG) signals from scratch — filtering noise, detecting heartbeats, calculating heart rate, and analyzing heart rate variability (HRV).
Overview
This project takes a raw ECG signal and walks it through a complete signal-processing pipeline: cleaning up noise with a digital filter, finding the R-peaks that mark each heartbeat, computing the heart rate, and measuring how much the beat-to-beat timing varies (HRV). Everything is done in Python using NumPy, SciPy, and Matplotlib.

I built this to learn how the math behind biomedical signal processing actually works — not just calling library functions, but understanding why a Butterworth filter has a flat passband, why we normalize to the Nyquist frequency, and what it means when successive RR intervals change by 20 milliseconds.

Motivation
I've always been curious about how wearable devices like smartwatches can look at a noisy electrical signal and turn it into a heart rate number on a screen. When I started learning Python and signal processing, I wanted to try building a simplified version of that pipeline myself.

This project was my way of connecting concepts from math (standard deviation, RMS), physics (frequency filtering), and programming (array operations, data visualization) into something that actually does something real. It also helped me appreciate how much careful engineering goes into medical devices — even this simplified version has a lot of moving parts.

Features
ECG Loading — Uses SciPy's built-in electrocardiogram dataset (no external downloads needed)
Bandpass Filtering — 3rd-order Butterworth filter (0.5–45 Hz) to remove baseline wander and high-frequency noise
R-Peak Detection — Finds heartbeats using scipy.signal.find_peaks with tuned height and distance thresholds
Heart Rate Calculation — Computes instantaneous and average BPM from RR intervals
HRV Analysis — Calculates two standard time-domain metrics:
SDNN — overall heart rate variability
RMSSD — beat-to-beat variability
Portfolio-Quality Visualization — Three-panel plot with:
Raw vs. filtered ECG comparison
R-peak detection with vertical drop-lines
RR interval tachogram with mean line and ±1 SD band
Technologies Used
Tool	What I Used It For
Python 3	Core programming language
NumPy	Array math — slicing signals, computing intervals, standard deviation
SciPy	Butterworth filter design (butter, sosfilt), peak detection (find_peaks), sample ECG dataset
Matplotlib	All plots and visualization
How the Pipeline Works
Here's what the code does, step by step:


Raw ECG Signal (360 Hz, ~5 min)
        │
        ▼
┌─────────────────────┐
│  Extract 10s slice  │   Grab samples from 30s to 40s
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Butterworth Filter │   Bandpass 0.5–45 Hz (3rd order)
│                     │   Removes baseline drift + high-freq noise
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  R-Peak Detection   │   scipy.signal.find_peaks
│                     │   height > 60% of max, min distance 0.3s
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  RR Intervals       │   Time gaps between consecutive R-peaks
└────────┬────────────┘
         │
         ▼
┌────────┴────────────┐
│  Heart Rate (BPM)   │   60 / RR_interval for each beat
│  HRV: SDNN, RMSSD   │   Variability of the RR intervals
└─────────────────────┘
Key Concepts
Why a Butterworth filter? It has a "maximally flat" frequency response in the passband, meaning it doesn't create ripples that could distort the ECG waveform shape. Other filters (like Chebyshev) can be sharper but introduce distortion.

Why 0.5–45 Hz?

Below 0.5 Hz: baseline wander from breathing and electrode movement
Above 45 Hz: muscle noise (EMG) and power-line interference (50/60 Hz)
The actual ECG signal content (P-wave, QRS complex, T-wave) lives in between
What is SDNN? The standard deviation of all RR intervals. It tells you the overall spread — how much the timing varies across the entire recording.

What is RMSSD? Root mean square of successive differences between RR intervals. Instead of comparing each interval to the mean, it compares each interval to the one right before it. This captures rapid, beat-to-beat changes.

Installation & Usage
Prerequisites
Python 3.8 or newer
pip (Python package manager)
Setup
bash

# Clone the repository
git clone https://github.com/YOUR_USERNAME/ecg-signal-processing.git
cd ecg-signal-processing
# Install dependencies
pip install numpy scipy matplotlib
# SciPy's dataset module needs 'pooch' to download the ECG data
pip install pooch
# Run the script
python ecg_analysis.py
The script will:

Download the ECG dataset automatically (first run only, ~1 MB)
Print signal info, detected peaks, heart rate, and HRV metrics to the terminal
Save a plot as ecg_analysis_output.png
Display the plot in a window
Example Terminal Output

Full ECG signal: 108000 samples at 360 Hz (300.0 seconds)
Extracted slice: 3600 samples (30s to 40s)
Applied 3rd-order Butterworth bandpass filter (0.5–45.0 Hz)
Detected 18 R-peaks
R-R intervals (s):   [0.544 0.511 0.517 0.514 0.519 ...]
Average heart rate:  111.0 BPM
SDNN:  24.54 ms
RMSSD: 18.02 ms
Example Results
The script produces a three-panel figure:

Panel	What It Shows
Top	Raw ECG (faint red) overlaid with filtered ECG (blue) — you can see the filter removing drift and noise
Middle	Filtered ECG with detected R-peaks marked as red triangles, plus vertical drop-lines showing the rhythm
Bottom	RR interval tachogram — each dot is one beat-to-beat interval, with the mean (dashed line) and ±1 standard deviation band (shaded)
The HRV metrics (SDNN, RMSSD, mean HR, mean RR) are displayed in a text box on the tachogram panel.

Limitations
Being honest about what this project can't do:

Short recording window — 10 seconds is enough for RMSSD but not ideal for SDNN, which is typically computed over 5-minute or 24-hour recordings. My SDNN values shouldn't be compared to clinical reference ranges.
No artifact rejection — Real ECG signals can have ectopic beats, motion artifacts, and missed detections. This project assumes the signal is clean and doesn't try to identify or remove bad beats.
Simple peak detection — I used fixed thresholds (60% of max, 0.3s minimum distance). A more robust approach would use adaptive thresholds, template matching, or the Pan-Tompkins algorithm.
Single lead only — Clinical ECGs use 12 leads; this dataset is a single-lead recording.
No frequency-domain HRV — I only implemented time-domain metrics (SDNN, RMSSD). A more complete analysis would include power spectral density and LF/HF ratio.
Future Improvements
Things I'd like to add if I continue working on this:

 Pan-Tompkins algorithm for more robust R-peak detection
 Frequency-domain HRV — compute PSD and extract LF/HF power ratio
 Longer analysis windows — process the full 5-minute recording in sliding windows
 Poincaré plot — scatter plot of each RR interval vs. the next one (a standard HRV visualization)
 Interactive controls — let the user adjust filter cutoffs and peak detection thresholds with sliders
 Support for real ECG files — load .edf or .csv files from PhysioNet databases
 Artifact detection — flag and exclude ectopic or missed beats before computing HRV
What I Learned
How digital filters work — the relationship between filter order, cutoff frequency, and the Nyquist theorem
Why second-order sections (SOS) are more numerically stable than transfer function coefficients
How peak detection algorithms balance sensitivity (finding all real peaks) vs. specificity (not finding false ones)
That "heart rate variability" isn't just noise — it's a meaningful physiological signal
How to make matplotlib plots that actually look good and communicate clearly

⚠️ Disclaimer
This is a student educational project, not a medical device or diagnostic tool.

The signal processing, peak detection, and HRV calculations in this project are simplified implementations for learning purposes. They have not been validated against clinical standards and should never be used to make medical decisions, diagnose conditions, or replace professional medical advice.

If you have concerns about your heart health, please consult a qualified healthcare professional.

