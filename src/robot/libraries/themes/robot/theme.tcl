# Copyright 2024 Robot Framework Foundation

source [file join [file dirname [info script]] system_detection.tcl]

option add *tearOff 0

# Returns the color palette for the dark theme
proc get_dark_colors {} {
    return [list \
        -fg             "#E8E8E8" \
        -bg             "#2D2D30" \
        -disabledfg     "#A0A0A0" \
        -disabledbg     "#3E3E42" \
        -selectfg       "#FFFFFF" \
        -selectbg       "#0078D7" \
        -accent         "#1DE9B6" \
        -accenthover    "#64FFDA" \
        -accentpressed  "#00BFA5" \
        -border         "#3F3F46" \
        -inputbg        "#333337" \
        -focusborder    "#111111" \
        -troughbg       "#444444" \
        -activebg       "#3E3E42" \
        -buttonbg       "#00CED1" \
        -buttonfg       "#000000" \
        -notebookbg     "#252526" \
        -notebookfg     "#CCCCCC" \
        -notebookactive "#333333" \
        -scrollbarhover "#3E3E42" \
        -scalepressed   "#555555" \
        -scrollbartroughbg "#333337" \
    ]
}

# Returns the color palette for the light theme
proc get_light_colors {} {
    return [list \
        -fg             "#202020" \
        -bg             "#F5F5F5" \
        -disabledfg     "#A0A0A0" \
        -disabledbg     "#E6E6E6" \
        -selectfg       "#FFFFFF" \
        -selectbg       "#0078D7" \
        -accent         "#1DE9B6" \
        -accenthover    "#64FFDA" \
        -accentpressed  "#00BFA5" \
        -border         "#DFDFDF" \
        -inputbg        "#FFFFFF" \
        -focusborder    "#111111" \
        -troughbg       "#E0E0E0" \
        -activebg       "#E6E6E6" \
        -buttonbg       "#00CED1" \
        -buttonfg       "#000000" \
        -notebookbg     "#EAEAEA" \
        -notebookfg     "#333333" \
        -notebookactive "#F0F0F0" \
        -scrollbarhover "#D0D0D0" \
        -scalepressed   "#D0D0D0" \
        -scrollbartroughbg "#E0E0E0" \
    ]
}

# Create a theme with the given name and colors
proc create_robot_theme {theme_name colors_array} {
    array set colors $colors_array

    ttk::style theme create $theme_name -parent clam -settings {
        # Frame styles
        ttk::style configure TFrame \
            -background $colors(-bg) \
            -borderwidth 0

        # Label styles
        ttk::style configure TLabel \
            -background $colors(-bg) \
            -foreground $colors(-fg)

        # Button styles without images
        ttk::style layout TButton {
            Button.border -children {
                Button.focus -children {
                    Button.padding -children {
                        Button.label
                    }
                }
            }
        }

        # Button configuration
        ttk::style configure TButton \
            -background $colors(-buttonbg) \
            -foreground $colors(-buttonfg) \
            -relief flat \
            -borderwidth 1 \
            -padding {6 4} \
            -focuscolor $colors(-focusborder) \
            -anchor center \
            -cornerradius 4

        # Button mapping for states
        ttk::style map TButton \
            -background [list active $colors(-accenthover) pressed $colors(-accentpressed) disabled $colors(-disabledbg)] \
            -foreground [list disabled $colors(-disabledfg)] \
            -relief [list {pressed !disabled} flat] \
            -focuscolor [list focus $colors(-focusborder)]

        # Alternative focus highlighter
        ttk::style configure TButton.Focus -relief solid -highlightcolor $colors(-focusborder) -highlightthickness 1

        # Entry styles
        ttk::style configure TEntry \
            -fieldbackground $colors(-inputbg) \
            -foreground $colors(-fg) \
            -insertcolor $colors(-fg) \
            -borderwidth 1 \
            -padding {3 3} \
            -relief solid

        # Treeview styles
        ttk::style configure Treeview \
            -background $colors(-inputbg) \
            -fieldbackground $colors(-inputbg) \
            -foreground $colors(-fg) \
            -borderwidth 1 \
            -padding {3 3} \
            -relief solid

        ttk::style map Treeview \
            -background [list selected $colors(-accent)] \
            -foreground [list selected $colors(-selectfg)]

        # Combobox styles
        ttk::style configure TCombobox \
            -fieldbackground $colors(-inputbg) \
            -foreground $colors(-fg) \
            -padding 5 \
            -cornerradius 4 \
            -borderwidth 1

        ttk::style map TCombobox \
            -fieldbackground [list readonly $colors(-bg)] \
            -selectbackground [list readonly $colors(-accent)]

        # Checkbutton styles
        ttk::style configure TCheckbutton \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -indicatorcolor $colors(-accent)

        ttk::style map TCheckbutton \
            -background [list active $colors(-activebg)] \
            -foreground [list disabled $colors(-disabledfg)]

        # Radiobutton styles
        ttk::style configure TRadiobutton \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -indicatorcolor $colors(-accent)

        ttk::style map TRadiobutton \
            -background [list active $colors(-activebg)] \
            -foreground [list disabled $colors(-disabledfg)]

        # Notebook styles
        ttk::style configure TNotebook \
            -background $colors(-bg) \
            -borderwidth 0 \
            -padding 2

        ttk::style configure TNotebook.Tab \
            -background $colors(-notebookbg) \
            -foreground $colors(-notebookfg) \
            -padding {10 5} \
            -borderwidth 1 \
            -relief flat \
            -cornerradius 4

        ttk::style map TNotebook.Tab \
            -background [list selected $colors(-bg) active $colors(-notebookactive)] \
            -foreground [list selected $colors(-accent)] \
            -expand [list selected {0 0 2 0}]

        # Progressbar styles
        ttk::style configure TProgressbar \
            -background $colors(-accent) \
            -troughcolor $colors(-troughbg) \
            -borderwidth 0

        # Labelframe styles
        ttk::style configure TLabelframe \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -borderwidth 1 \
            -relief groove

        ttk::style configure TLabelframe.Label \
            -background $colors(-bg) \
            -foreground $colors(-fg)

        # Scrollbar styles
        ttk::style configure TScrollbar \
            -background $colors(-bg) \
            -troughcolor $colors(-scrollbartroughbg) \
            -borderwidth 0 \
            -arrowcolor $colors(-accent)

        ttk::style map TScrollbar \
            -background [list hover $colors(-accent) pressed $colors(-accentpressed)] \
            -troughcolor [list hover $colors(-scrollbarhover)]

        # Spinbox styles
        ttk::style configure TSpinbox \
            -fieldbackground $colors(-inputbg) \
            -foreground $colors(-fg) \
            -arrowcolor $colors(-fg) \
            -borderwidth 1

        # Scale styles
        ttk::style configure TScale \
            -background $colors(-bg) \
            -troughcolor $colors(-troughbg) \
            -sliderrelief flat \
            -sliderlength 15 \
            -borderwidth 0

        ttk::style map TScale \
            -background [list active $colors(-activebg)] \
            -troughcolor [list pressed $colors(-scalepressed)]
    }
}

# Common theming function to reduce code duplication
proc apply_theme_colors {colors_list} {
    # Convert list back to array
    array set colors $colors_list

    ttk::style configure . \
        -background $colors(-bg) \
        -foreground $colors(-fg) \
        -troughcolor $colors(-bg) \
        -focuscolor $colors(-accent) \
        -selectbackground $colors(-selectbg) \
        -selectforeground $colors(-selectfg) \
        -insertcolor $colors(-fg) \
        -insertwidth 1 \
        -fieldbackground $colors(-inputbg) \
        -borderwidth 1 \
        -relief flat

    # Set the palette for regular tk widgets
    tk_setPalette background [ttk::style lookup . -background] \
        foreground [ttk::style lookup . -foreground] \
        highlightColor [ttk::style lookup . -focuscolor] \
        selectBackground [ttk::style lookup . -selectbackground] \
        selectForeground [ttk::style lookup . -selectforeground] \
        activeBackground $colors(-accent) \
        activeForeground $colors(-selectfg)

    ttk::style map . \
        -foreground [list disabled $colors(-disabledfg)] \
        -background [list disabled $colors(-disabledbg)]

    # Menu color configuration
    option add *Menu.selectcolor $colors(-fg)
    option add *Menu.background $colors(-bg)
    option add *Menu.foreground $colors(-fg)
    option add *Menu.activeBackground $colors(-selectbg)
    option add *Menu.activeForeground $colors(-selectfg)
}

# Create both themes on load
create_robot_theme "robot_light" [get_light_colors]
create_robot_theme "robot_dark" [get_dark_colors]

proc set_theme {{mode "auto"}} {
    # In auto mode, detect the system mode
    if {$mode eq "auto"} {
        set mode [detect_system_mode]
    }

    if {$mode eq "dark"} {
        ttk::style theme use "robot_dark"
        array set colors [get_dark_colors]
        apply_theme_colors [array get colors]
    } elseif {$mode eq "light"} {
        ttk::style theme use "robot_light"
        array set colors [get_light_colors]
        apply_theme_colors [array get colors]
    }
}