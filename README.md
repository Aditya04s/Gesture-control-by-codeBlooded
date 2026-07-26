**AI Gesture Experience v3**

A robust, multithreaded computer vision application that allows you to control your operating system entirely through hand gestures. Built with Python, OpenCV, and MediaPipe, this project uses a highly optimized, asynchronous architecture to ensure zero-latency cursor tracking, intelligent click-arming, and infinite scrolling.

✨ Features & Gestures
This system uses dynamic, distance-normalized geometric math to ensure your hand is tracked perfectly whether you are close to the camera or far away.

  ☝️ Cursor Mode (Index finger up): Moves your mouse cursor smoothly within an Active Control Region to reduce wrist strain.

  👌 Single Click (Pinch + 3 back fingers up): A quick tap and release to left-click. The 3 back fingers act as a "safety switch" to prevent accidental misfires.

  👌👌 Double Click (Double pinch + 3 back fingers up): Two quick taps to execute a double-click.

  🤏 Drag & Drop (Hold pinch + 3 back fingers up): Hold the pinch for ~0.45 seconds to lock the mouse button down. Open the pinch to drop.

  ✌️ Scroll Mode (Index & middle fingers up): Freezes the cursor in place. Moving your palm up or down infinitely scrolls the active window.

  🤙 Screenshot (Shaka / Thumb & pinky out): Triggers a 3-second UI countdown, flashes the screen, and safely saves a screenshot to the disk using a background worker thread.

  ✋ Frozen / Idle (Any unknown gesture): Instantly freezes the cursor and safely drops any active drags if the tracking is lost.

🚀 Installation & Setup (VS Code)
Follow these steps to clone the repository and set up your development environment in Visual Studio Code.

1. Clone the Repository
Open your terminal or command prompt and run:

Bash
- ```git clone https://github.com/Aditya04s/Aditya---Gesture-Control-v3.git```
- ```cd Gesture-Control-v3```

2. Open in VS Code
Open the project folder directly in VS Code:

Bash
  - ```code .```

3. Set Up the Virtual Environment
  To keep dependencies isolated, create a Python virtual environment. Open the VS Code integrated terminal (Ctrl + ` or Cmd + `) and run:

Bash
  ```python -m venv .venv```
  
  Activate the virtual environment:

  Windows (PowerShell):

PowerShell
  ```.\.venv\Scripts\Activate.ps1```
  
(Note: If you get an Execution Policy error, run Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned first).

Mac/Linux:

Bash
  - ```source .venv/bin/activate```

4. Install Dependencies
  With your '.venv' activated, install the required core modules by running:

bash
    ```pip install -r requirements.txt```


📂 Project Architecture
The codebase relies on a heavily decoupled, asynchronous design to maintain maximum camera framerates.
main.py: The core synchronous router that manages the OpenCV camera loop and UI rendering.
        
  modules/gestures.py: The geometric math engine that normalizes distances and tracks joint angles.

  modules/mouse.py: Runs on an independent background thread to execute OS-level cursor movements and clicks without blocking the camera.

  modules/worker.py: A queue-based asynchronous worker thread for heavy I/O tasks (like saving screenshots).

  modules/screenshot.py: A standalone State Machine that safely manages timers, flashes, and UI triggers.

  modules/scroll.py: Calculates dynamic delta movements to mimic physical hardware scrolling.

🕹️ Usage
To start the AI Gesture Experience, ensure your virtual environment is active and run:

```Bash
python main.py
```
Press q in the video window at any time to safely terminate the background threads and exit the application.
