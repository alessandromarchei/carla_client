
#================================================
# ===           CARLA emulator client         ===
# ===   -----------------------------------   ===
# ===       Basic dialog implementation       ===
#================================================

class BasicDialog(object):

    # Place dialog window at screen center
    def center_window(self, parent):
        parent.update_idletasks()
        width = parent.winfo_width()
        height = parent.winfo_height()
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        parent.geometry(f"{width}x{height}+{x}+{y}")


