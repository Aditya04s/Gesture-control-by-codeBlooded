"""
modules/worker.py
---------------------------------
Asynchronous Background Job Manager
"""

import threading
import queue
import time


class BackgroundWorker:
    def __init__(self):
        # Create a thread-safe Queue to pass tasks from main loop to background thread
        self.task_queue = queue.Queue()
        
        # Define the worker thread
        self.worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        
        # Flag to shut down gracefully if needed
        self.running = True
        
        # Start the background execution
        self.worker_thread.start()

    def add_task(self, task_type, action_function, *args, **kwargs):
        """Allows the main thread to safely drop off a job without waiting."""
        self.task_queue.put((task_type, action_function, args, kwargs))

    def _run_loop(self):
        """Internal background loop running continuously in its own thread."""
        while self.running:
            try:
                # Wait for a task to show up in the queue (timeout prevents hanging on exit)
                task_type, action_function, args, kwargs = self.task_queue.get(timeout=1.0)
                
                try:
                    # Execute the slow function (like mouse.screenshot) away from camera thread
                    action_function(*args, **kwargs)
                except Exception as e:
                    print(f"\n[Worker Error] Failed executing task '{task_type}': {e}")
                finally:
                    # Signal to the queue that the item is processed
                    self.task_queue.task_done()
                    
            except queue.Empty:
                # No tasks came in during the past second; loop around and check running flag
                continue

    def stop(self):
        """Stops the worker thread background loop gracefully."""
        self.running = False
        self.worker_thread.join(timeout=2.0)