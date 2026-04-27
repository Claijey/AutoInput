# AutoInput - The Ultimate Multi-Tool Utility ⚡

**AutoInput** is a polished, lightweight automation application designed in Python. Built cleanly over `CustomTkinter`, it packs together heavy-duty features inside a tabbed, beautifully minimal dark-mode interface:

- 🔤 **Spammer:** Fire text and send instantly. Controlled delay.  
- 🖱️ **Clicker (CPS/Interval):** Sub-microsecond precision clicking (up to 100+ CPS) without lag or missing bursts. Perfect for Left, Right, or Middle clicks.
- ⏎ **Holder:** Directly binds physical key-down routines to effectively mimic actual holding; works across nearly all applications and games. 
- 🚶 **Anti-AFK:** Generates zero-net-movement walking cycles (W → S → A → D) inside games to keep servers from kicking you for inactivity. 

## ⚙ Customizable Hotkeys 

Forget hardcoded restrictions. Hit the `⚙ Settings` button anywhere on the app to completely decouple your inputs. Any trigger mechanism uses raw key detection — just click "Press a key...", tap your desired mapping, and your entire application's interface changes to reflect your setup instantly.

### Portable "Settings.json"

When you adjust your app hotkeys, it saves flawlessly into a local `settings.json`. Copy the executable alongside this JSON file onto a flash drive and take your personalized macros to any PC. 

## Installation

You do not need Python or any development environment to run AutoInput!

1. Head to the **Releases** tab in GitHub (or check the `/dist` directory if downloaded raw).
2. Download `AutoInput.exe` and double click. 
3. You're set!

> Alternatively, to build from source:
```bash
# Clone the repository
git clone https://github.com/your-username/auto-input.git
cd auto-input

# Set up environment
python -m venv venv
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Run
python main.py

# Or build via PyInstaller
pyinstaller main.spec --noconfirm
```

## Stack

- **Python 3**
- [**CustomTkinter**](https://github.com/TomSchimansky/CustomTkinter) for the modern aesthetics.
- **PyAutoGUI, Keyboard, and ctypes** for unhindered direct OS manipulation. 
- **PyInstaller** for EXE compilation.

---
*Built with ❤️.*
