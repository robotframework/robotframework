# Copyright 2024 Robot Framework Foundation

# Helper procedure to safely execute a command
proc safe_exec {cmd} {
    if {[catch {set result [eval $cmd]} err]} {
        return ""
    } else {
        return $result
    }
}

# Detects the system display mode (Dark or Light)
proc detect_system_mode {} {
    global tcl_platform

    # macOS detection
    if {$tcl_platform(os) eq "Darwin"} {
        # Try defaults command method
        set result [safe_exec {exec defaults read -g AppleInterfaceStyle}]

        if {$result eq "Dark"} {
            return "dark"
        } elseif {$result eq "Light"} {
            return "light"
        }

        # Try alternative method with osascript
        set result [safe_exec {exec osascript -e {tell application "System Events" to tell appearance preferences to return dark mode}}]

        if {$result eq "true"} {
            return "dark"
        } elseif {$result ne ""} {
            return "light"
        }

        return "light"
    } elseif {$tcl_platform(platform) eq "windows"} {  # Windows detection
        # Try to load the registry package
        if {[safe_exec {package require registry}] eq ""} {
            return "light"
        }

        # Read the registry value
        set regValue [safe_exec {registry get {HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize} AppsUseLightTheme}]

        if {$regValue eq ""} {
            return "light"
        }

        if {$regValue == 0} {
            return "dark"
        } else {
            return "light"
        }
    } elseif {$tcl_platform(os) eq "Linux" || [string match "*linux*" $tcl_platform(os)]} {  # Linux detection
        # Check GNOME Color-Scheme
        set result [safe_exec {exec gsettings get org.gnome.desktop.interface color-scheme}]

        if {$result ne ""} {
            if {[string match "*dark*" $result]} {
                return "dark"
            } else {
                return "light"
            }
        }

        # Check GTK Theme
        set result [safe_exec {exec gsettings get org.gnome.desktop.interface gtk-theme}]

        if {$result ne ""} {
            if {[string match "*dark*" $result] || [string match "*Dark*" $result]} {
                return "dark"
            } else {
                return "light"
            }
        }

        return "light"
    } else {  # Other platforms
        return "light"
    }
}
