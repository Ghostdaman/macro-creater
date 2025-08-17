import customtkinter as CTK
import keyboard
import threading
import time
import pyautogui

CTK.set_appearance_mode("dark")
root = CTK.CTk()
root.geometry("450x600")
root.configure(fg_color="#1e1e1e")
root.title("Macros")
root.iconbitmap('Guillendesign-Variations-2-Script-Console.ico')


PLACEHOLDER = "No Macros Yet"
macro_settings = {}
running_macro = False
registered_hotkeys = {}


import json

CONFIG_FILE = 'config.json'

def dark_messagebox(title, message):
    popup = tk.Toplevel()
    popup.overrideredirect(True)
    popup.configure(bg="#222")
    popup.geometry("320x140+500+300")
    popup.iconbitmap('Guillendesign-Variations-2-Script-Console.ico')
    CTK.CTkLabel(popup, text=title, fg_color="#222", text_color="white", font=("Arial", 16, "bold")).pack(pady=(10,0))
    CTK.CTkLabel(popup, text=message, fg_color="#222", text_color="white", font=("Arial", 14)).pack(pady=10)
    CTK.CTkButton(popup, text="OK", command=popup.destroy).pack(pady=10)
    popup.grab_set()

def load_macros():
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            macro_settings.clear()
            macro_settings.update(data)
            return list(data.keys())
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_settings():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(macro_settings, f, indent=2)
import base64

import customtkinter as CTK

def export_macro():
    selected_macro = macrolist.get().strip()
    settings = macro_settings.get(selected_macro, {})
    if not settings:
        dark_messagebox("No Macro Selected", "Please select a macro to export.")
        return
    macro_json = json.dumps(settings)
    macro_b64 = base64.urlsafe_b64encode(macro_json.encode()).decode()

    popup = CTK.CTkToplevel(root)
    popup.overrideredirect(True)
    popup.title("Export Macro")
    popup.geometry("400x180")
    popup.configure(fg_color="#222")
    popup.attributes("-topmost", True)
    CTK.CTkLabel(popup, text="Export string:", fg_color="#222", text_color="white").pack(pady=(15, 5))
    entry = CTK.CTkEntry(popup, width=320)
    entry.insert(0, macro_b64)
    entry.configure(state="readonly")
    entry.pack(pady=5)

    def copy_to_clipboard():
        popup.clipboard_clear()
        popup.clipboard_append(macro_b64)
        popup.update()

    CTK.CTkButton(popup, text="Copy", command=copy_to_clipboard).pack(pady=10)
    CTK.CTkButton(popup, text="Exit", command=popup.destroy).pack(pady=5)

def import_macro():
    def do_import():
        macro_b64 = entry.get().strip()
        try:
            macro_json = base64.urlsafe_b64decode(macro_b64.encode()).decode()
            settings = json.loads(macro_json)
            macro_name = name_entry.get().strip()
            if not macro_name:
                dark_messagebox("No Name", "Please enter a macro name.")
                return
            settings.setdefault("keys", [])
            settings.setdefault("start_hotkey", "F6")
            settings.setdefault("stop_hotkey", "F7")
            settings.setdefault("delay", 1.0)
            macro_settings[macro_name] = settings
            for item in settings.get("keys", []):
                if item.get("type") == "mouse":
                    if "x" in item and "y" in item and ("x_pct" not in item or "y_pct" not in item):
                        screen_width = root.winfo_screenwidth()
                        screen_height = root.winfo_screenheight()
                        item["x_pct"] = item["x"] / screen_width
                        item["y_pct"] = item["y"] / screen_height
            save_settings()

            refresh_combobox(selected=macro_name)
            popup.destroy()
        except Exception as e:
            dark_messagebox("Import Error", str(e))

    popup = CTK.CTkToplevel(root)
    popup.title("Import Macro")
    popup.overrideredirect(True)
    popup.geometry("400x280")
    popup.configure(fg_color="#222")
    popup.attributes("-topmost", True)
    CTK.CTkLabel(popup, text="Paste export string:", fg_color="#222", text_color="white").pack(pady=(15, 5))
    entry = CTK.CTkEntry(popup, width=320)
    entry.pack(pady=5)
    CTK.CTkLabel(popup, text="Macro Name:", fg_color="#222", text_color="white").pack(pady=(10, 5))
    name_entry = CTK.CTkEntry(popup, width=200)
    name_entry.pack(pady=5)
    CTK.CTkButton(popup, text="Import", command=do_import).pack(pady=15)
    CTK.CTkButton(popup, text="Exit", command=popup.destroy).pack(pady=5)

def printMN():
    MacroName = name.get().strip()
    if not MacroName:
        dark_messagebox("No Name To Save", "Please Give Your Macro A Name")
        return



    existing = load_macros()
    if MacroName in existing:
        dark_messagebox("Duplicate Name", f'"{MacroName}" already exists!')
        return

    macro_settings[MacroName] = {
        "delay": 1.0, "x": 0, "y": 0,
        "keys": [],
        "start_hotkey": "F6",
        "stop_hotkey": "F7"
    }
    save_settings()
    refresh_combobox(selected=MacroName)
    name.delete(0, 'end')

def Delete():
    selected_macro = macrolist.get().strip()
    items = load_macros()

    if not items or selected_macro not in items:
        dark_messagebox("No Selection", "Please select a macro to delete")
        return

    if selected_macro in macro_settings:
        unregister_hotkeys(selected_macro)
        del macro_settings[selected_macro]
        save_settings()

    refresh_combobox()

def refresh_combobox(selected=None):
    items = load_macros()
    for macro_name in list(registered_hotkeys.keys()):
        unregister_hotkeys(macro_name)
    if items:
        macrolist.configure(values=items, state="normal")
        chosen = selected if selected in items else items[0]
        macrolist.set(chosen)
        on_macro_selected(chosen)
        register_hotkeys(chosen)
    else:
        macrolist.set(PLACEHOLDER)
        macrolist.configure(values=[PLACEHOLDER], state="disabled")
        on_macro_selected(PLACEHOLDER)


def pick_location_for_macro(macro_name):
    overlay = tk.Toplevel(root)
    overlay.attributes("-fullscreen", True)
    overlay.attributes("-alpha", 0.3)
    overlay.configure(bg="black")
    overlay.lift()
    overlay.focus_force()

    msg = tk.Label(overlay, text="Click anywhere to set location\nPress ESC to cancel",
                   font=("Arial", 24), fg="white", bg="black")
    msg.pack(expand=True)

    def on_click(event):
        macro_settings.setdefault(macro_name, {})
        macro_settings[macro_name]["x"] = event.x_root
        macro_settings[macro_name]["y"] = event.y_root
        save_settings()
        overlay.destroy()
        refresh_combobox(selected=macro_name)

    def on_escape(event):
        overlay.destroy()

    overlay.bind("<Button-1>", on_click)
    overlay.bind("<Escape>", on_escape)

def show_popup(message, duration=5000, fade_ms=1000):
    popup = tk.Toplevel(root)
    popup.overrideredirect(True)
    popup.attributes("-topmost", True)
    popup.configure(bg="#222")
    label = tk.Label(popup, text=message, font=("Arial", 12, "bold"), fg="white", bg="#222", padx=20, pady=10)
    label.pack()
    popup.update_idletasks()
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    width = popup.winfo_width()
    height = popup.winfo_height()
    x = screen_width - width - 20
    y = screen_height - height - 60
    popup.geometry(f"{width}x{height}+{x}+{y}")
    popup.attributes("-alpha", 1.0)

    def fade_out(step=0):
        alpha = max(0, 1.0 - step / 20)
        popup.attributes("-alpha", alpha)
        if alpha > 0:
            popup.after(fade_ms // 20, lambda: fade_out(step + 1))
        else:
            popup.destroy()

    popup.after(duration, fade_out)

def run_macro(macro_name):
    global running_macro
    if running_macro:
        return
    running_macro = True
    show_popup("Macro Started")

    def macro_loop():
        global running_macro
        settings = macro_settings.get(macro_name, {})
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        while running_macro:
            for item in settings.get("keys", []):
                if not running_macro:
                    break
                if item.get("type") == "mouse":
                    x = int(item["x_pct"] * screen_width)
                    y = int(item["y_pct"] * screen_height)
                    button = item.get("button", "left")
                    pyautogui.click(x, y, button=button)
                    time.sleep(item.get("delay", 1.0))
                else:
                    key = item["key"]
                    delay = item["delay"]
                    keyboard.press_and_release(key)
                    time.sleep(delay)
    threading.Thread(target=macro_loop, daemon=True).start()

def test_macro():
    selected_macro = macrolist.get().strip()
    settings = macro_settings.get(selected_macro, {})
    if not settings or not settings.get("keys"):
        dark_messagebox("No Steps", "No steps recorded for this macro.")
        return

    overlay = tk.Toplevel(root)
    overlay.attributes("-fullscreen", True)
    overlay.attributes("-alpha", 0.3)
    overlay.configure(bg="black")
    overlay.lift()
    overlay.focus_force()

    mouse_offset = 30
    key_offset = 0.08

    mouse_count = 0
    key_count = 0
    for idx, item in enumerate(settings["keys"]):
        if item.get("type") == "mouse":
            x, y = item["x"], item["y"]
            lbl = tk.Label(
                overlay,
                text=f"{idx + 1}\n{item.get('button', 'left').capitalize()}\n",
                font=("Arial", 14, "bold"),
                fg="yellow",
                bg="black"
            )
            lbl.place(x=x, y=y + mouse_count * mouse_offset, anchor="center")
            mouse_count += 1
        else:
            key = item["key"]
            lbl = tk.Label(
                overlay,
                text=f"{idx + 1}\nKey: {key}\n",
                font=("Arial", 14, "bold"),
                fg="yellow",
                bg="black"
            )
            lbl.place(relx=0.5, rely=0.1 + key_count * key_offset, anchor="center")
            key_count += 1

    overlay.bind("<Escape>", lambda e: overlay.destroy())
    overlay.bind("<Button-1>", lambda e: overlay.destroy())

def stop_macro():
    global running_macro
    running_macro = False
    show_popup("Macro Stopped")
import tkinter as tk

def show_popup(message, duration=5000, fade_ms=1000):
    popup = tk.Toplevel(root)
    popup.overrideredirect(True)
    popup.attributes("-topmost", True)
    popup.configure(bg="#222")
    label = tk.Label(popup, text=message, font=("Arial", 12, "bold"), fg="white", bg="#222", padx=20, pady=10)
    label.pack()
    popup.update_idletasks()
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    width = popup.winfo_width()
    height = popup.winfo_height()
    x = screen_width - width - 20
    y = screen_height - height - 60
    popup.geometry(f"{width}x{height}+{x}+{y}")
    popup.attributes("-alpha", 1.0)

    def fade_out(step=0):
        alpha = max(0, 1.0 - step / 20)
        popup.attributes("-alpha", alpha)
        if alpha > 0:
            popup.after(fade_ms // 20, lambda: fade_out(step + 1))
        else:
            popup.destroy()

    popup.after(duration, fade_out)

def register_hotkeys(macro_name):
    """Register start/stop hotkeys for a macro"""
    settings = macro_settings.get(macro_name)
    if not settings:
        return

    start_key = settings.get("start_hotkey", "F6")
    stop_key = settings.get("stop_hotkey", "F7")

    unregister_hotkeys(macro_name)

    keyboard.add_hotkey(start_key, lambda: run_macro(macro_name))
    keyboard.add_hotkey(stop_key, stop_macro)

    registered_hotkeys[macro_name] = (start_key, stop_key)

def unregister_hotkeys(macro_name):
    if macro_name in registered_hotkeys:
        start_key, stop_key = registered_hotkeys[macro_name]
        try:
            keyboard.remove_hotkey(start_key)
            keyboard.remove_hotkey(stop_key)
        except KeyError:
            pass
        del registered_hotkeys[macro_name]

def show_click_locations():
    selected_macro = macrolist.get().strip()
    settings = macro_settings.get(selected_macro, {})
    if not settings or not settings.get("keys"):
        dark_messagebox("No Clicks", "No mouse clicks recorded for this macro.")
        return

    overlay = tk.Toplevel(root)
    overlay.attributes("-fullscreen", True)
    overlay.attributes("-alpha", 0.3)
    overlay.configure(bg="black")
    overlay.lift()
    overlay.focus_force()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    for idx, item in enumerate(settings["keys"]):
        if item.get("type") == "mouse":
            if "x_pct" in item and "y_pct" in item:
                x = int(item["x_pct"] * screen_width)
                y = int(item["y_pct"] * screen_height)
            else:
                x = item.get("x", 0)
                y = item.get("y", 0)
            lbl = tk.Label(overlay, text=str(idx + 1), font=("Arial", 12, "bold"),
                           fg="red", bg="black")
            lbl.place(x=x, y=y, anchor="center")

    overlay.bind("<Escape>", lambda e: overlay.destroy())
    overlay.bind("<Button-1>", lambda e: overlay.destroy())

def on_macro_selected(selected_macro):
    for widget in options_frame.winfo_children():
        widget.destroy()

    if selected_macro == PLACEHOLDER:
        return

    settings = macro_settings.setdefault(selected_macro, {
        "delay": 1.0, "x": 0, "y": 0, "keys": [],
        "start_hotkey": "F6", "stop_hotkey": "F7"
    })

    CTK.CTkButton(options_frame, text="Export Macro", command=export_macro).pack(pady=5)
    CTK.CTkLabel(options_frame, text="Add New Key:").pack()
    key_entry = CTK.CTkEntry(options_frame, placeholder_text="Type a key")
    key_entry.pack(pady=2)

    key_delay_entry = CTK.CTkEntry(options_frame, placeholder_text="Delay (sec)")
    key_delay_entry.pack(pady=2)

    def add_key():
        key = key_entry.get().strip()
        try:
            delay = float(key_delay_entry.get().strip())
        except:
            delay = 1.0
        if key:
            settings["keys"].append({"key": key, "delay": delay})
            save_settings()
            on_macro_selected(selected_macro)
    CTK.CTkButton(options_frame, text="Add Key", command=add_key).pack(pady=5)
    delay_label = CTK.CTkLabel(options_frame, text=f"Click Delay: {settings['delay']:.2f}s")
    delay_label.pack()
    def update_delay(val):
        settings["delay"] = float(val)
        delay_label.configure(text=f"Click Delay: {settings['delay']:.2f}s")
        save_settings()
    delay_slider = CTK.CTkSlider(options_frame, from_=0.1, to=240.0, number_of_steps=50, command=update_delay)
    delay_slider.set(settings["delay"])
    delay_slider.pack(pady=5)

    def record_mouse_click():
        root.iconify()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        def on_click(event, button_type):
            settings["keys"].append({
                "type": "mouse",
                "x_pct": event.x_root / screen_width,
                "y_pct": event.y_root / screen_height,
                "button": button_type,
                "delay": settings.get("delay", 1.0)
            })
            save_settings()

        def on_cancel(event=None):
            overlay.destroy()
            root.deiconify()
            on_macro_selected(selected_macro)

        overlay = tk.Toplevel(root)
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 0.3)
        overlay.configure(bg="black")
        overlay.lift()
        overlay.focus_force()
        msg = tk.Label(overlay, text="Left/Right click to record multiple\nPress ESC when done",
                       font=("Arial", 24), fg="white", bg="black")
        msg.pack(expand=True)
        overlay.bind("<Button-1>", lambda e: on_click(e, "left"))
        overlay.bind("<Button-3>", lambda e: on_click(e, "right"))
        overlay.bind("<Escape>", on_cancel)

    CTK.CTkButton(options_frame, text="Record Mouse Click", command=record_mouse_click).pack(pady=5)
    CTK.CTkButton(options_frame, text="Show Click Locations", command=show_click_locations).pack(pady=5)
    CTK.CTkButton(options_frame, text="Test Macro", command=test_macro).pack(pady=5)
    CTK.CTkLabel(options_frame, text="Current Keys:").pack(pady=5)

    drag_data = {"start_idx": None, "target_idx": None}

    def on_drag_start(event, idx):
        drag_data["start_idx"] = idx

    def on_drag_motion(event):
        x, y = event.x_root, event.y_root
        for i, label in enumerate(label_widgets):
            lx, ly = label.winfo_rootx(), label.winfo_rooty()
            lw, lh = label.winfo_width(), label.winfo_height()
            if lx <= x <= lx + lw and ly <= y <= ly + lh:
                drag_data["target_idx"] = i
                break

    def on_drag_drop(event):
        start = drag_data.get("start_idx")
        target = drag_data.get("target_idx")
        if start is not None and target is not None and start != target:
            item = settings["keys"].pop(start)
            settings["keys"].insert(target, item)
            save_settings()
            on_macro_selected(selected_macro)
        drag_data["start_idx"] = None
        drag_data["target_idx"] = None

    label_widgets = []

    for idx, item in enumerate(settings.get("keys", [])):
        frame = CTK.CTkFrame(options_frame, fg_color="#2e2e2e")
        frame.pack(fill="x", padx=5, pady=2)
        if item.get("type") == "mouse":
            if "x_pct" in item and "y_pct" in item:
                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()
                x = int(item["x_pct"] * screen_width)
                y = int(item["y_pct"] * screen_height)
            else:
                x = item.get("x", 0)
                y = item.get("y", 0)
            button_type = item.get("button", "left")
            label_text = f"{idx + 1}. Mouse {button_type.capitalize()} Click @ ({x}, {y})"
        else:
            label_text = f"{idx + 1}. Key: {item['key']}"
        label = CTK.CTkLabel(frame, text=label_text)
        label.pack(side="left", padx=5)
        label_widgets.append(label)
        label.bind("<Button-1>", lambda e, i=idx: on_drag_start(e, i))
        label.bind("<B1-Motion>", on_drag_motion)
        label.bind("<ButtonRelease-1>", on_drag_drop)

        delay_var = tk.StringVar(value=str(item["delay"]))
        delay_entry = CTK.CTkEntry(frame, textvariable=delay_var, width=60)
        delay_entry.pack(side="left", padx=5)

        def save_delay(i=idx, var=delay_var):
            try:
                settings["keys"][i]["delay"] = float(var.get())
                save_settings()
            except ValueError:
                pass

        CTK.CTkButton(frame, text="Save", width=40,
                      command=lambda i=idx, var=delay_var: save_delay(i, var)).pack(side="left", padx=2)

        def delete_key(i=idx):
            del settings["keys"][i]
            save_settings()
            on_macro_selected(selected_macro)

        CTK.CTkButton(frame, text="X", width=30, fg_color="red",
                      command=lambda i=idx: delete_key(i)).pack(side="right", padx=2)

    CTK.CTkLabel(options_frame, text="Hotkeys:").pack(pady=5)
    start_entry = CTK.CTkEntry(options_frame, placeholder_text="Start Hotkey")
    start_entry.insert(0, settings["start_hotkey"])
    start_entry.pack(pady=2)
    stop_entry = CTK.CTkEntry(options_frame, placeholder_text="Stop Hotkey")
    stop_entry.insert(0, settings["stop_hotkey"])
    stop_entry.pack(pady=2)

    def save_hotkeys():
        settings["start_hotkey"] = start_entry.get().strip()
        settings["stop_hotkey"] = stop_entry.get().strip()
        register_hotkeys(selected_macro)
        save_settings()
        dark_messagebox("Hotkeys Updated", f"Start: {settings['start_hotkey']} | Stop: {settings['stop_hotkey']}")
    CTK.CTkButton(options_frame, text="Save Hotkeys", command=save_hotkeys).pack(pady=5)

    CTK.CTkButton(options_frame, text=f"Start Macro ({settings['start_hotkey']})",
                  command=lambda: run_macro(selected_macro)).pack(pady=5)
    CTK.CTkButton(options_frame, text=f"Stop Macro ({settings['stop_hotkey']})",
                  command=stop_macro, fg_color="red").pack(pady=5)


name = CTK.CTkEntry(master=root, placeholder_text="Macro Name")
name.pack()
submit = CTK.CTkButton(master=root, text="Submit Name",
                       bg_color="transparent", fg_color="transparent",
                       hover_color="black", command=printMN)
CTK.CTkButton(root, text="Import Macro", command=import_macro, hover_color="black", bg_color="transparent", fg_color="transparent").pack(pady=5)
submit.pack()
macrolist = CTK.CTkComboBox(master=root, values=load_macros(),
                            justify='center', command=on_macro_selected)
macrolist.set(PLACEHOLDER)
macrolist.configure(values=[PLACEHOLDER], state="disabled")
macrolist.pack()
delete = CTK.CTkButton(master=root, text="Delete Current Macro",
                       bg_color="transparent", fg_color="transparent",
                       hover_color="black", command=Delete)
delete.pack()

options_frame = CTK.CTkScrollableFrame(root, fg_color="transparent")
options_frame.pack(fill="both", expand=True, padx=10, pady=10)

if load_macros():
    refresh_combobox()



root.mainloop()
