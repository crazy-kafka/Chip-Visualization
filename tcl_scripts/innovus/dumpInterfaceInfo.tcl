proc get_interface_info {port_name} {
    set port_col [get_ports $port_name -exact]
    set direction [get_property $port_col direction]
    puts "Collecting $port_name ($direction) information"
	if {$direction == "inout"} {
        puts "Inout port $port_name is ignored"
		return 0
    }
    set unit 1
	set x [get_property $port_col x_coordinate]
	set y [get_property $port_col y_coordinate]
	if {$x == ""} {set x 0}
	if {$y == ""} {set y 0}
    set port_x [expr $x / $unit]
    set port_y [expr $y / $unit]


    if {$direction == "in"} {
        set path_col [report_timing -collection -from $port_col]
        if {[sizeof_collection $path_col] == 0} {puts "Invalid $port_name"; return 0}
        if {[get_property $path_col required] == "INFINITY"} {puts "Unconstraint path from $port_name"; return 0}

        set clk_name [get_object_name [index_collection [get_property $path_col endpoint_clock] 0]]
        if {$clk_name == ""} {puts "Invalid $port_name"; return 0}
        set clk_period [get_property [get_clocks $clk_name -filter {period != "NA"}] period]


        set arrival [get_property $path_col arrival]
        set input_reg_clock_latency [get_property $path_col endpoint_clock_latency]
        set input_clock_latency [get_property $path_col startpoint_clock_latency]
        set slack [get_property $path_col slack]
        set input_delay [get_property $path_col startpoint_input_delay_value]
        set end_point_col [get_property $path_col endpoint]
        set reg_x [get_property $end_point_col x_coordinate]
        if {$reg_x == ""} {set reg_x 0} else {set reg_x [expr $reg_x/$unit]}
        set reg_y [get_property $end_point_col y_coordinate]
        if {$reg_y == ""} {set reg_y 0} else {set reg_y [expr $reg_y/$unit]}
        set path_delay [expr $arrival-$input_clock_latency-$input_delay]
        set clock_latency $input_reg_clock_latency
        set reg_name [get_object_name [get_cells -of_objects [get_property $path_col endpoint]]]
        if {$reg_name == ""} {
            set reg_name "port-[get_object_name [get_property $path_col endpoint]]"
        }
    } elseif {$direction == "out"} {
        set path_col [report_timing -collection -to $port_col]
        if {[sizeof_collection $path_col] == 0} {puts "Invalid $port_name"; return 0}
        if {[get_property $path_col required] == "INFINITY"} {puts "Unconstraint path from $port_name"; return 0}


        set clk_name [get_object_name [index_collection [get_property $path_col startpoint_clock] 0]]
        if {$clk_name == ""} {puts "Invalid $port_name"; return 0}
        set clk_period [get_property [get_clocks $clk_name -filter {period != "NA"}] period]


        set arrival [get_property $path_col arrival]
        set output_reg_clock_latency [get_property $path_col startpoint_clock_latency]
        set output_clock_latency [get_property $path_col endpoint_clock_latency]
        set slack [get_property $path_col slack]
        set output_delay [get_property $path_col endpoint_output_delay_value]
        set start_point_col [get_property $path_col startpoint]
        set reg_x [get_property $start_point_col x_coordinate]
        if {$reg_x == ""} {set reg_x 0} else {set reg_x [expr $reg_x/$unit]}
		set reg_y [get_property $start_point_col y_coordinate]
		if {$reg_y == ""} {set reg_y 0} else {set reg_y [expr $reg_y/$unit]}
		set reg_name [get_object_name [get_cells -of_object [get_property $path_col startpoint]]]
        if {$reg_name == ""} {
            set path_delay [expr $arrival-$output_reg_clock_latency-$output_delay]
        } else {
            set path_delay [expr $arrival-$output_reg_clock_latency]
        }
        set clock_latency $output_reg_clock_latency
        if {$reg_name == ""} {
            set reg_name "port-[get_object_name [get_property $path_col endpoint]]"
        }
    } elseif {$direction == "inout"} {
        puts "Inout port $port_name is ignored"
    }
    set manhattan_distance [expr abs($port_x-$reg_x)+abs($port_y-$reg_y)]
    if {$manhattan_distance == 0} {
        puts "port name: $port_name $path_col"
    }

    set period [get_property $path_col period]
	set clk_period [lsort -real -unique $clk_period]
	set cycle_ratio 0.00
	if {$clk_period != 0} {
		set cycle_ratio [format %.2f [expr $path_delay / $period] ]
	}

    set port_info [dict create]
    dict set port_info direction $direction
    dict set port_info port_x $port_x
    dict set port_info port_y $port_y
    dict set port_info reg_x $reg_x
    dict set port_info reg_y $reg_y
    dict set port_info path_delay $path_delay
    dict set port_info clock_latency $clock_latency
    dict set port_info manhattan_distance $manhattan_distance
    dict set port_info clk_name $clk_name
    dict set port_info clk_period $clk_period
    dict set port_info mcp [expr $period / $clk_period]
	dict set port_info cycle_ratio $cycle_ratio
    dict set port_info reg_name $reg_name

    return $port_info
}

proc dump_interface_info_csv {ports_name {out_file ""}} {
    if {$out_file == ""} {
        set out_file "[get_object_name [get_design]].interface_info.csv"
    }
    set info_types [list \
        port_name \
        direction \
        port_x \
        port_y \
        reg_x \
        reg_y \
        path_delay \
        clock_latency \
        manhattan_distance \
        clk_name \
        clk_period \
        mcp \
		cycle_ratio \
        reg_name \
        ]
    set fh [open $out_file "w"]
    puts $fh [join $info_types ","]
    foreach port $ports_name {
        set port_info [get_interface_info $port]
        if {$port_info == 0} {continue}
        set to_puts [list $port]
        foreach type [lrange $info_types 1 end] {
            lappend to_puts [dict get $port_info $type]
        }
        puts $fh [join $to_puts ","]
    }
    close $fh
}

