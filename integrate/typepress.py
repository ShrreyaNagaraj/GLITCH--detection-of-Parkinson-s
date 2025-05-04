import tkinter as tk
from tkinter import messagebox
import pandas as pd
import numpy as np
import time
from pynput import keyboard
from threading import Timer

class FingerTappingAnalyzer:
    def __init__(self, dataset_path, result_label, root):
        self.tap_times = []
        self.test_duration = 10  # seconds
        self.dataset = pd.read_csv(dataset_path)  # Load the dataset from the local path
        print(f"Dataset loaded with {len(self.dataset)} samples.")

        # Print dataset columns to verify and adjust the column names
        print("Columns in dataset:", self.dataset.columns)

        # Set defaults for missing columns if necessary
        if 'std_tap_time' not in self.dataset.columns:
            self.mean_std_tap_time = 0  # Default value or handle as needed
        else:
            self.mean_std_tap_time = self.dataset['std_tap_time'].mean()
        
        if 'cv_tap_time' not in self.dataset.columns:
            self.mean_cv_tap_time = 0  # Default value or handle as needed
        else:
            self.mean_cv_tap_time = self.dataset['cv_tap_time'].mean()

        if 'fatigue_index' not in self.dataset.columns:
            self.mean_fatigue_index = 0  # Default value or handle as needed
        else:
            self.mean_fatigue_index = self.dataset['fatigue_index'].mean()
        
        # Store the result_label and root to update the GUI later
        self.result_label = result_label
        self.root = root

    def start_test(self):
        """Conduct the finger tapping test"""
        self.tap_times = []
        self.test_duration = 10  # seconds

        # Start countdown in Tkinter window
        self.update_label("Test starting in:")
        self.countdown(3)

    def countdown(self, count):
        """Handle the countdown for starting the test"""
        if count > 0:
            self.update_label(f"{count}...")
            self.root.after(1000, self.countdown, count - 1)  # Call countdown recursively
        else:
            self.update_label("GO! Start tapping the spacebar!")
            self.start_tapping_test()

    def start_tapping_test(self):
        """Start the actual tapping test"""
        self.tap_times = []
        start_time = time.time()

        # Initialize the listener to capture spacebar taps
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        # Set a timer to stop the test after the specified duration
        self.timer = Timer(self.test_duration, self.stop_listener)
        self.timer.start()

    def on_press(self, key):
        """Handle key presses and record spacebar taps"""
        try:
            if key == keyboard.Key.space:
                self.tap_times.append(time.time())
        except AttributeError:
            pass

    def stop_listener(self):
        """Stop the listener after the test duration"""
        self.listener.stop()
        self.analyze_results()

    def analyze_results(self):
        """Analyze the tapping patterns and show results"""
        if len(self.tap_times) < 2:
            self.update_label("Not enough taps recorded.")
            return
        
        # Calculate intervals between consecutive taps
        intervals = np.diff(self.tap_times)

        # Calculate metrics
        metrics = {
            'mean_tap_time': float(np.mean(intervals)),
            'std_tap_time': float(np.std(intervals)),
            'cv_tap_time': float(np.std(intervals) / np.mean(intervals)),
            'fatigue_index': self._calculate_fatigue_index(intervals),
            'rhythm_score': self._calculate_rhythm_score(intervals),
            'num_taps': len(self.tap_times)
        }

        # Calculate risk score based on heuristics
        risk_score = self.calculate_risk(metrics)

        # Display the result
        risk_text = self.get_risk_text(risk_score)
        result_message = f"Risk Assessment: {risk_text}\nTap Times: {metrics['num_taps']}\nMean Tap Time: {metrics['mean_tap_time']:.4f}s"
        self.update_label(result_message)

    def calculate_risk(self, metrics):
        """Assign risk score based on heuristic analysis"""
        risk_score = 0
        
        if metrics['std_tap_time'] > self.mean_std_tap_time + 0.02:
            risk_score += 10
        
        if metrics['cv_tap_time'] > self.mean_cv_tap_time + 0.05:
            risk_score += 15
        
        if metrics['fatigue_index'] > self.mean_fatigue_index + 0.03:
            risk_score += 25
        
        return min(risk_score, 100)

    def _calculate_fatigue_index(self, intervals):
        """Calculate fatigue index by comparing first and last third of intervals"""
        if len(intervals) < 6:
            return 0
        first_third = intervals[:len(intervals)//3]
        last_third = intervals[-len(intervals)//3:]
        return float((np.mean(last_third) - np.mean(first_third)) / np.mean(first_third))

    def _calculate_rhythm_score(self, intervals):
        """Calculate rhythm consistency score"""
        if len(intervals) < 2:
            return 0
        cv = np.std(intervals) / np.mean(intervals)
        score = max(0, min(100, 100 * (1 - cv)))
        return float(score)

    def get_risk_text(self, risk_score):
        """Determine the risk level based on the score"""
        if risk_score <= 30:
            return "Low risk"
        elif risk_score <= 60:
            return "Moderate risk"
        else:
            return "High risk"

    def update_label(self, text):
        """Update the text of the result label"""
        self.result_label.config(text=text)


class App:
    def __init__(self, root, analyzer):
        self.root = root
        self.root.title("Finger Tapping Analyzer")
        self.analyzer = analyzer

        # Create the UI components
        self.label = tk.Label(root, text="Finger Tapping Risk Detection", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.start_button = tk.Button(root, text="Start Test", command=self.start_test)
        self.start_button.pack(pady=20)

        self.result_label = tk.Label(root, text="Results will be displayed here.", font=("Helvetica", 12))
        self.result_label.pack(pady=10)

        # Pass the result_label and root to the analyzer
        self.analyzer.result_label = self.result_label
        self.analyzer.root = self.root

    def start_test(self):
        # Disable the start button during the test
        self.start_button.config(state=tk.DISABLED)
        
        # Start the test via the analyzer
        self.analyzer.start_test()

    def run(self):
        self.root.mainloop()


# Create the Tkinter root window
root = tk.Tk()

# Load the dataset and create the analyzer
analyzer = FingerTappingAnalyzer("database.csv", None, root)
app = App(root, analyzer)

# Start the Tkinter event loop
app.run()
