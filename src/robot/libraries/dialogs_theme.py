import tkinter as tk
from tkinter import ttk
import platform
import subprocess


def detect_system_mode() -> str:
    """Detect if the system is using light or dark mode. Returns 'light' or 'dark'."""
    system = platform.system()

    # macOS detection
    if system == "Darwin":
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True, check=False
            ).stdout.strip()

            if result == "Dark":
                return "dark"

            # Alternative method with osascript
            result = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to tell appearance preferences to return dark mode'],
                capture_output=True, text=True, check=False
            ).stdout.strip()

            if result == "true":
                return "dark"
            return "light"
        except Exception:
            return "light"

    # Windows detection
    elif system == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return "light" if value else "dark"
        except Exception:
            return "light"

    # Linux detection
    elif system == "Linux":
        try:
            # Check GNOME Color-Scheme
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True, text=True, check=False
            ).stdout.strip()

            if "dark" in result.lower():
                return "dark"

            # Check GTK Theme
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                capture_output=True, text=True, check=False
            ).stdout.strip()

            if "dark" in result.lower():
                return "dark"

            return "light"
        except Exception:
            return "light"

    # Default for other platforms
    return "light"


class RobotTheme:
    @staticmethod
    def get_dark_colors():
        return {
            "fg": "#E8E8E8",
            "bg": "#2D2D30",
            "disabledfg": "#A0A0A0",
            "disabledbg": "#3E3E42",
            "selectfg": "#FFFFFF",
            "selectbg": "#0078D7",
            "accent": "#2AC9C0",
            "accenthover": "#64DDD0",
            "accentpressed": "#259F9C",
            "border": "#3F3F46",
            "inputbg": "#333337",
            "focusborder": "#111111",
            "troughbg": "#444444",
            "activebg": "#3E3E42",
            "buttonbg": "#00CED1",
            "buttonfg": "#000000",
            "notebookbg": "#252526",
            "notebookfg": "#CCCCCC",
            "notebookactive": "#333333",
            "scrollbarhover": "#3E3E42",
            "scalepressed": "#555555",
            "scrollbartroughbg": "#333337"
        }

    @staticmethod
    def get_light_colors():
        return {
            "fg": "#202020",
            "bg": "#F5F5F5",
            "disabledfg": "#A0A0A0",
            "disabledbg": "#E6E6E6",
            "selectfg": "#FFFFFF",
            "selectbg": "#0078D7",
            "accent": "#2AC9C0",
            "accenthover": "#64DDD0",
            "accentpressed": "#259F9C",
            "border": "#DFDFDF",
            "inputbg": "#FFFFFF",
            "focusborder": "#111111",
            "troughbg": "#E0E0E0",
            "activebg": "#E6E6E6",
            "buttonbg": "#00CED1",
            "buttonfg": "#000000",
            "notebookbg": "#EAEAEA",
            "notebookfg": "#333333",
            "notebookactive": "#F0F0F0",
            "scrollbarhover": "#D0D0D0",
            "scalepressed": "#D0D0D0",
            "scrollbartroughbg": "#E0E0E0"
        }

    @staticmethod
    def get_material_colors():
        return {
            "fg": "#000000",
            "bg": "#FFFFFF",
            "disabledfg": "#9E9E9E",
            "disabledbg": "#F5F5F5",
            "selectfg": "#FFFFFF",
            "selectbg": "#6200EE",
            "accent": "#6200EE",
            "accenthover": "#3700B3",
            "accentpressed": "#1A00A0",
            "border": "#E0E0E0",
            "inputbg": "#FFFFFF",
            "focusborder": "#2962FF",
            "troughbg": "#E0E0E0",
            "activebg": "#F5F5F5",
            "buttonbg": "#BB86FC",
            "buttonfg": "#000000",
            "notebookbg": "#EAEAEA",
            "notebookfg": "#333333",
            "notebookactive": "#F0F0F0",
            "scrollbarhover": "#D0D0D0",
            "scalepressed": "#D0D0D0",
            "scrollbartroughbg": "#E0E0E0"
        }

    @staticmethod
    def create_robot_theme(style, colors):
        """Create a robot theme with the given colors."""
        # Configure base style
        style.configure(".",
                        background=colors["bg"],
                        foreground=colors["fg"],
                        troughcolor=colors["bg"],
                        focuscolor=colors["accent"],
                        selectbackground=colors["selectbg"],
                        selectforeground=colors["selectfg"],
                        insertcolor=colors["fg"],
                        insertwidth=1,
                        fieldbackground=colors["inputbg"],
                        borderwidth=1,
                        relief="flat")

        # Map states for base style
        style.map(".",
                 foreground=[("disabled", colors["disabledfg"])],
                 background=[("disabled", colors["disabledbg"])])

        # Frame styles
        style.configure("TFrame",
                        background=colors["bg"],
                        borderwidth=0,
                        padding=3)

        # Label styles
        style.configure("TLabel",
                        background=colors["bg"],
                        foreground=colors["fg"])

        # Button styles
        style.configure("TButton",
                       background=colors["buttonbg"],
                       foreground=colors["buttonfg"],
                       relief="flat",
                       borderwidth=1,
                       padding=3,
                       focuscolor=colors["focusborder"],
                       anchor="center")

        style.map("TButton",
                 background=[("active", colors["accenthover"]),
                             ("pressed", colors["accentpressed"]),
                             ("disabled", colors["disabledbg"])],
                 foreground=[("disabled", colors["disabledfg"])],
                 relief=[("pressed", "flat")],
                 focuscolor=[("focus", colors["focusborder"])])

        # Entry styles
        style.configure("TEntry",
                       fieldbackground=colors["inputbg"],
                       foreground=colors["fg"],
                       insertcolor=colors["fg"],
                       borderwidth=1,
                       padding=3,
                       relief="solid")

        # Treeview styles
        style.configure("Treeview",
                       background=colors["inputbg"],
                       fieldbackground=colors["inputbg"],
                       foreground=colors["fg"],
                       borderwidth=1,
                       relief="solid")

        style.map("Treeview",
                 background=[("selected", colors["accent"])],
                 foreground=[("selected", colors["selectfg"])])

        # Combobox styles
        style.configure("TCombobox",
                       fieldbackground=colors["inputbg"],
                       foreground=colors["fg"],
                       padding=3,
                       borderwidth=1)

        style.map("TCombobox",
                 fieldbackground=[("readonly", colors["bg"])],
                 selectbackground=[("readonly", colors["accent"])])

        # Checkbutton styles
        style.configure("TCheckbutton",
                       background=colors["bg"],
                       foreground=colors["fg"])

        style.map("TCheckbutton",
                 background=[("active", colors["activebg"])],
                 foreground=[("disabled", colors["disabledfg"])])

        # Radiobutton styles
        style.configure("TRadiobutton",
                       background=colors["bg"],
                       foreground=colors["fg"])

        style.map("TRadiobutton",
                 background=[("active", colors["activebg"])],
                 foreground=[("disabled", colors["disabledfg"])])

        # Notebook styles
        style.configure("TNotebook",
                       background=colors["bg"],
                       borderwidth=0,
                       padding=2)

        style.configure("TNotebook.Tab",
                       background=colors["notebookbg"],
                       foreground=colors["notebookfg"],
                       padding=(10, 5),
                       borderwidth=1,
                       relief="flat")

        style.map("TNotebook.Tab",
                 background=[("selected", colors["bg"]), ("active", colors["notebookactive"])],
                 foreground=[("selected", colors["accent"])])

        # Progressbar styles
        style.configure("TProgressbar",
                       background=colors["accent"],
                       troughcolor=colors["troughbg"],
                       borderwidth=0)

        # Labelframe styles
        style.configure("TLabelframe",
                       background=colors["bg"],
                       foreground=colors["fg"],
                       borderwidth=1,
                       relief="groove")

        style.configure("TLabelframe.Label",
                       background=colors["bg"],
                       foreground=colors["fg"])

        # Scrollbar styles
        style.configure("TScrollbar",
                       background=colors["bg"],
                       troughcolor=colors["scrollbartroughbg"],
                       borderwidth=0,
                       arrowcolor=colors["accent"],
                       relief="flat")

        style.map("TScrollbar",
                 background=[("hover", colors["accent"]), ("pressed", colors["accentpressed"])],
                 troughcolor=[("hover", colors["scrollbarhover"])],
                 arrowcolor=[("hover", colors["accenthover"]), ("pressed", colors["accentpressed"])])

        # Spinbox styles
        style.configure("TSpinbox",
                       fieldbackground=colors["inputbg"],
                       foreground=colors["fg"],
                       borderwidth=1)

        # Scale styles
        style.configure("TScale",
                       background=colors["bg"],
                       troughcolor=colors["troughbg"],
                       borderwidth=0)

        style.map("TScale",
                 background=[("active", colors["activebg"])],
                 troughcolor=[("pressed", colors["scalepressed"])])

    @staticmethod
    def apply_theme_to_tk_widgets(root, colors):
        """Apply colors to standard Tk widgets."""
        root.option_add("*Menu.selectColor", colors["fg"])
        root.option_add("*Menu.background", colors["bg"])
        root.option_add("*Menu.foreground", colors["fg"])
        root.option_add("*Menu.activeBackground", colors["selectbg"])
        root.option_add("*Menu.activeForeground", colors["selectfg"])
        root.option_add("*tearOff", 0)  # Disable tear-off menus

        # Set color palette for standard tk widgets
        root.tk_setPalette(
            background=colors["bg"],
            foreground=colors["fg"],
            highlightColor=colors["accent"],
            selectBackground=colors["selectbg"],
            selectForeground=colors["selectfg"],
            activeBackground=colors["accent"],
            activeForeground=colors["selectfg"]
        )

    @classmethod
    def set_theme(cls, root: tk.Tk, mode: str = "auto") -> ttk.Style:
        """Apply the theme to the given Tk root. Returns the ttk.Style object."""
        style = ttk.Style()

        # Detect theme mode if auto
        if mode == "auto":
            mode = detect_system_mode()

        # Apply appropriate theme
        if mode == "dark":
            colors = cls.get_dark_colors()
        elif mode == "material":
            colors = cls.get_material_colors()
        else:  # Default to light
            mode = "light"
            colors = cls.get_light_colors()

        theme_name = f"robot_theme_{mode}"

        if theme_name not in style.theme_names():
            style.theme_create(theme_name, parent="clam", settings={
                ".": {
                    "configure": {
                        "background": colors["bg"],
                        "foreground": colors["fg"],
                        "troughcolor": colors["bg"],
                        "focuscolor": colors["accent"],
                        "selectbackground": colors["selectbg"],
                        "selectforeground": colors["selectfg"],
                        "insertcolor": colors["fg"],
                        "insertwidth": 1,
                        "fieldbackground": colors["inputbg"],
                        "borderwidth": 1,
                        "relief": "flat"
                    },
                    "map": {
                        "foreground": [("disabled", colors["disabledfg"])],
                        "background": [("disabled", colors["disabledbg"])]
                    }
                },
                "TFrame": {
                    "configure": {
                        "background": colors["bg"],
                        "borderwidth": 0,
                        "padding": 3
                    }
                },
                "TLabel": {
                    "configure": {
                        "background": colors["bg"],
                        "foreground": colors["fg"]
                    }
                },
                "TButton": {
                    "configure": {
                        "background": colors["buttonbg"],
                        "foreground": colors["buttonfg"],
                        "relief": "flat",
                        "borderwidth": 1,
                        "padding": 3,
                        "focuscolor": colors["focusborder"],
                        "anchor": "center"
                    },
                    "map": {
                        "background": [("active", colors["accenthover"]),
                                       ("pressed", colors["accentpressed"]),
                                       ("disabled", colors["disabledbg"])],
                        "foreground": [("disabled", colors["disabledfg"])],
                        "relief": [("pressed", "flat")],
                        "focuscolor": [("focus", colors["focusborder"])]
                    }
                },
                "TEntry": {
                    "configure": {
                        "fieldbackground": colors["inputbg"],
                        "foreground": colors["fg"],
                        "insertcolor": colors["fg"],
                        "borderwidth": 1,
                        "padding": 3,
                        "relief": "solid"
                    }
                },
                "Treeview": {
                    "configure": {
                        "background": colors["inputbg"],
                        "fieldbackground": colors["inputbg"],
                        "foreground": colors["fg"],
                        "borderwidth": 1,
                        "relief": "solid"
                    },
                    "map": {
                        "background": [("selected", colors["accent"])],
                        "foreground": [("selected", colors["selectfg"])]
                    }
                },
                "TCombobox": {
                    "configure": {
                        "fieldbackground": colors["inputbg"],
                        "foreground": colors["fg"],
                        "padding": 3,
                        "borderwidth": 1
                    },
                    "map": {
                        "fieldbackground": [("readonly", colors["bg"])],
                        "selectbackground": [("readonly", colors["accent"])]
                    }
                },
                "TCheckbutton": {
                    "configure": {
                        "background": colors["bg"],
                        "foreground": colors["fg"]
                    },
                    "map": {
                        "background": [("active", colors["activebg"])],
                        "foreground": [("disabled", colors["disabledfg"])]
                    }
                },
                "TRadiobutton": {
                    "configure": {
                        "background": colors["bg"],
                        "foreground": colors["fg"]
                    },
                    "map": {
                        "background": [("active", colors["activebg"])],
                        "foreground": [("disabled", colors["disabledfg"])]
                    }
                },
                "TNotebook": {
                    "configure": {
                        "background": colors["bg"],
                        "borderwidth": 0,
                        "padding": 2
                    }
                },
                "TNotebook.Tab": {
                    "configure": {
                        "background": colors["notebookbg"],
                        "foreground": colors["notebookfg"],
                        "padding": (10, 5),
                        "borderwidth": 1,
                        "relief": "flat"
                    },
                    "map": {
                        "background": [("selected", colors["bg"]), ("active", colors["notebookactive"])],
                        "foreground": [("selected", colors["accent"])]
                    }
                },
                "TProgressbar": {
                    "configure": {
                        "background": colors["accent"],
                        "troughcolor": colors["troughbg"],
                        "borderwidth": 0
                    }
                },
                "TLabelframe": {
                    "configure": {
                        "background": colors["bg"],
                        "foreground": colors["fg"],
                        "borderwidth": 1,
                        "relief": "groove"
                    }
                },
                "TLabelframe.Label": {
                    "configure": {
                        "background": colors["bg"],
                        "foreground": colors["fg"]
                    }
                },
                "TScrollbar": {
                    "configure": {
                        "background": colors["bg"],
                        "troughcolor": colors["scrollbartroughbg"],
                        "borderwidth": 0,
                        "arrowcolor": colors["accent"],
                        "relief": "flat"
                    },
                    "map": {
                        "background": [("hover", colors["accent"]), ("pressed", colors["accentpressed"])],
                        "troughcolor": [("hover", colors["scrollbarhover"])],
                        "arrowcolor": [("hover", colors["accenthover"]), ("pressed", colors["accentpressed"])]
                    }
                },
                "TSpinbox": {
                    "configure": {
                        "fieldbackground": colors["inputbg"],
                        "foreground": colors["fg"],
                        "borderwidth": 1
                    }
                },
                "TScale": {
                    "configure": {
                        "background": colors["bg"],
                        "troughcolor": colors["troughbg"],
                        "borderwidth": 0
                    },
                    "map": {
                        "background": [("active", colors["activebg"])],
                        "troughcolor": [("pressed", colors["scalepressed"])]
                    }
                }
            })
        if style.theme_use() != theme_name:
            style.theme_use(theme_name)
            cls.apply_theme_to_tk_widgets(root, colors)

        return style


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Robot Framework Theme Demo")

    # Set the theme
    RobotTheme.set_theme(root)  # Auto-detect theme
    # Or explicitly set: RobotTheme.set_theme(root, "dark")

    # Create a demo interface with various widgets
    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Robot Framework Theme").pack(pady=10)

    # Buttons
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X, pady=5)
    ttk.Button(btn_frame, text="Normal Button").pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Disabled Button", state="disabled").pack(side=tk.LEFT, padx=5)

    # Entry
    entry_frame = ttk.Frame(main_frame)
    entry_frame.pack(fill=tk.X, pady=5)
    ttk.Label(entry_frame, text="Entry:").pack(side=tk.LEFT, padx=5)
    ttk.Entry(entry_frame).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    # Checkbox and Radio
    check_frame = ttk.Frame(main_frame)
    check_frame.pack(fill=tk.X, pady=5)
    ttk.Checkbutton(check_frame, text="Check 1").pack(side=tk.LEFT, padx=5)
    ttk.Checkbutton(check_frame, text="Check 2").pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(check_frame, text="Radio 1", value=1).pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(check_frame, text="Radio 2", value=2).pack(side=tk.LEFT, padx=5)

    # Combobox
    combo_frame = ttk.Frame(main_frame)
    combo_frame.pack(fill=tk.X, pady=5)
    ttk.Label(combo_frame, text="Combo:").pack(side=tk.LEFT, padx=5)
    combo = ttk.Combobox(combo_frame, values=["Option 1", "Option 2", "Option 3"])
    combo.pack(side=tk.LEFT, padx=5)
    combo.current(0)

    # Notebook
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True, pady=5)

    tab1 = ttk.Frame(notebook)
    ttk.Label(tab1, text="Tab 1 Content").pack(pady=10)
    ttk.Scale(tab1, from_=0, to=100).pack(fill=tk.X, padx=20, pady=10)

    tab2 = ttk.Frame(notebook)
    ttk.Progressbar(tab2, length=200, mode='determinate', value=75).pack(pady=20)

    notebook.add(tab1, text="Tab 1")
    notebook.add(tab2, text="Tab 2")

    # Treeview
    tree_frame = ttk.Frame(main_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

    tree = ttk.Treeview(tree_frame, columns=("col1", "col2"), show="headings", height=4)
    tree.heading("col1", text="Column 1")
    tree.heading("col2", text="Column 2")
    tree.column("col1", width=100)
    tree.column("col2", width=100)

    for i in range(5):
        tree.insert("", "end", values=(f"Item {i}", f"Value {i}"))

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

    # Insert a theme switcher
    theme_var = tk.StringVar(value="auto")
    def on_theme_change(event):
        RobotTheme.set_theme(root, theme_var.get())

    theme_box = ttk.Combobox(main_frame, textvariable=theme_var,
                             values=["auto", "light", "dark", "material"], state="readonly")
    theme_box.pack(side=tk.LEFT, padx=5)
    theme_box.bind('<<ComboboxSelected>>', on_theme_change)

    # Start the main loop
    root.mainloop()