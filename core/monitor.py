import os
import time

def get_snapshot(folder_path):
    try:
        return {
            f: os.path.getmtime(os.path.join(folder_path, f))
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and not f.lower().endswith(
                ('.tmp', '.part', '.bak', '.temp', '.crdownload')
            )
        }
    except:
        return {}

def should_trigger_alert(last_snapshot, current_snapshot, last_change_time, timeout_minutes):
    if current_snapshot != last_snapshot:
        return False, current_snapshot, time.time()
    elif time.time() - last_change_time >= timeout_minutes * 60:
        return True, last_snapshot, last_change_time
    return False, last_snapshot, last_change_time
