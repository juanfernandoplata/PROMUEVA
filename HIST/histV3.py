import tkinter as tk
from tkinter import ttk
from time import sleep

class WeightedStats:
    def __init__( this, values, weights ):
        this.values = values
        this.weights = weights
    
    def mean( this ):
        m = 0.0
        for i in range( len( this.values ) ):
            m += this.values[ i ] * this.weights[ i ]
        return m / sum( this.weights )
    
    def std( this ):
        m = this.mean()
        s = 0.0
        for i in range( len( this.values ) ):
            s += this.weights[ i ] * ( abs( this.values[ i ] - m ) ** 2 )
        return ( s / sum( this.weights ) ) ** ( 1 / 2 )

    def pm( this, K = 1, a = 1.6 ):
        p = 0.0
        for i in range( len( this.values ) ):
            for j in range( len( this.values ) ):
                p += ( ( this.weights[ i ] ** ( 1 + a ) ) * this.weights[ j ] ) * abs( this.values[ i ] - this.values[ j ] )
        return K * p

class Histogram:
    def where_id_is( this, id ):
        for i in range( this.bins ):
            if( this.bin_ids[ i ] == id ):
                return i
        return None

    def on_press( this, event ):
        this.selected_bin = this.canvas.find_withtag( "current" )
        if( len( this.selected_bin ) > 0 and this.selected_bin[ 0 ] != this.histogram_frame ):
            this.selected_bin = this.selected_bin[ 0 ]
            this.bin_on_click = this.canvas.coords( this.selected_bin )
            this.mouse_on_click = ( event.x, event.y )
        else:
            this.selected_bin = None
    
    def on_move_press( this, event ):
        bin_index = this.where_id_is( this.selected_bin )
        if( bin_index != None and
            this.bin_on_click[ 1 ] - ( this.mouse_on_click[ 1 ] - event.y ) < this.canvas_height - this.hmargin_to_plot and
            this.bin_on_click[ 1 ] - ( this.mouse_on_click[ 1 ] - event.y ) > this.hmargin_to_plot
        ):
            dif = this.bin_on_click[ 3 ] - ( this.bin_on_click[ 1 ] - ( this.mouse_on_click[ 1 ] - event.y ) )
            n = round( dif / this.height_unit )
            this.canvas.coords( this.selected_bin, this.bin_on_click[ 0 ], this.bin_on_click[ 3 ] - n * this.height_unit, *this.bin_on_click[ 2 : 4 ] )
            this.active_weights[ bin_index ] = n
            this.update_stats()

    def update_stats( this ):
        stats = WeightedStats( this.active_values, this.active_weights )
        if( sum( this.active_weights ) > 0 ):
            mean = stats.mean()
            std = stats.std()
            #print( mean )
            this.mean_display.config( text = f"MEAN = {mean:.1f}" )
            this.std_display.config( text = f"STD = {std:.1f}" )
        else:
            this.mean_display.config( text = f"MEAN = UNDEFINED" )
            this.std_display.config( text = f"STD = UNDEFINED" )
        pm = stats.pm()
        this.pm_display.config( text = f"PM = {pm:.1f}" )

    def animation_routine( this, animation, select ):
        this.set_weights( animation[ select ] )
        this.update_stats()
        if( select < len( animation ) - 1 ):
            this.main.after( 1500, this.animation_routine, animation, select + 1 )
        else:
            this.animation_running = False

    def define_animations( this ):
        this.animations = []
        this.animations.append(
            [ [ 10, 0, 0, 0, 5, 0, 0, 0, 5, 0 ],
              [ 10, 0, 0, 0, 4, 1, 0, 1, 4, 0 ],
              [ 10, 0, 0, 0, 3, 1, 2, 1, 3, 0 ],
              [ 10, 0, 0, 0, 2, 1, 4, 1, 2, 0 ],
              [ 10, 0, 0, 0, 1, 1, 6, 1, 1, 0 ],
              [ 10, 0, 0, 0, 0, 1, 8, 1, 0, 0 ],
              [ 10, 0, 0, 0, 0, 0, 10, 0, 0, 0 ] ]
        )
        this.animations.append(
            [ [ 10, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
              [ 10, 0, 0, 0, 0, 0, 0, 0, 0, 10 ] ]
        )

    def init_histogram( this ):
        this.yspace = this.canvas_height - 2 * this.hmargin_to_plot
        this.xspace = this.canvas_width - 2 * this.wmargin_to_plot
        this.height_unit = this.yspace / this.max_freq
        this.bin_width = this.xspace / this.bins
        this.histogram_frame = this.canvas.create_rectangle(
            this.wmargin_to_frame,
            this.hmargin_to_frame,
            this.canvas_width - this.wmargin_to_frame,
            this.canvas_height - this.hmargin_to_frame,
            fill = "white"
        )
        this.yaxis_text_ids = []
        this.yaxis_line_ids = []
        hbase = this.hmargin_to_frame + this.canvas_height * 0.05
        for i in range( this.max_freq + 1 ):
            this.yaxis_text_ids.append(
                this.canvas.create_text(
                    ( this.wmargin_to_frame - this.bin_width * 0.8, hbase + this.height_unit * i ),
                    text = f"{ this.max_freq - i }"
                ) # ESTANDARIZAR MEJOR
            )
            this.yaxis_line_ids.append(
                this.canvas.create_line(
                    this.wmargin_to_frame - this.bin_width * 0.1,
                    hbase + this.height_unit * i,
                    this.wmargin_to_frame,
                    hbase + this.height_unit * i
                )
            )
        this.bin_ids = []
        this.standby_values = [ 0 for _ in range( this.bins ) ]
        this.standby_weights = [ 0 for _ in range( this.bins ) ]
        this.active_values = [ 0 for _ in range( this.bins ) ]
        this.active_weights = [ 0 for _ in range( this.bins ) ]
        for i in range( this.bins ):
            this.bin_ids.append(
                this.canvas.create_rectangle(
                    this.wmargin_to_plot + i * this.xspace / this.bins,
                    this.canvas_height - this.hmargin_to_plot - this.height_unit,
                    this.wmargin_to_plot + ( i + 1 ) * this.xspace / this.bins,
                    this.canvas_height - this.hmargin_to_plot,
                    fill = "blue"
                )
            )
            this.active_weights[ i ] = 1.0
            this.active_values[ i ] = 1.0 / ( this.bins * 2 ) + i / this.bins

    def prepare_animation( this ):
        if( not this.animation_running ):
            this.animation_running = True
            this.reset( this.canvas_width, this.canvas_width )
            animation = this.animations[ this.animation_select.current() ]
            this.set_weights( animation[ 0 ] )
            this.update_stats()
            this.main.after( 1500, this.animation_routine, animation, 1 )

    def __init__( this, main, width, height, bins = 10, max_freq = 10 ):
        this.define_animations()
        this.animation_running = False

        this.canvas_width = width
        this.canvas_height = height
        this.wmargin_to_frame = this.canvas_width * 0.1
        this.hmargin_to_frame = this.canvas_height * 0.1
        this.wmargin_to_plot = this.canvas_width * 0.15
        this.hmargin_to_plot = this.canvas_height * 0.15
        this.bins = bins
        this.max_freq = max_freq
        this.canvas = tk.Canvas(
            main,
            width = this.canvas_width,
            height = this.canvas_height
        )
        this.canvas.bind( "<Button-1>", this.on_press )
        this.canvas.bind( "<B1-Motion>", this.on_move_press )
        this.init_histogram()

#        this.mean_display = tk.Label( this.main, background = "white", borderwidth = 1, relief = "solid" )
#        this.std_display = tk.Label( this.main, background = "white", borderwidth = 1, relief = "solid" )
#        this.pm_display = tk.Label( this.main, background = "white", borderwidth = 1, relief = "solid" )

        this.animation_run = tk.Button( this.canvas, text = "Animate: ", command = this.prepare_animation )
        this.animation_select = ttk.Combobox( this.canvas, width = 8 )
        this.animation_select[ "values" ] = ( "Axiom-1", "Axiom-2", "Axiom-3" )
        this.animation_select[ "state" ] = "readonly"
        this.animation_select.current( 0 )

#        this.mean_display.place( x = 500, y = 500 * 0.1 )
#        this.std_display.place( x = 500, y = 500 * 0.1 + 20 )
#        this.pm_display.place( x = 500, y = 500 * 0.1 + 40 )
        
        this.animation_run.place(
            x = this.wmargin_to_frame,
            y = this.canvas_height - this.hmargin_to_frame * 0.5
        )
        this.animation_select.place(
            x = this.wmargin_to_frame + 70,
            y = this.canvas_height - this.hmargin_to_frame * 0.5
        )

        this.update_stats()
    
    def reset( this, width, height, bins = 10, max_freq = 10 ):
        this.canvas_width = width
        this.canvas_height = height
        this.wmargin_to_frame = this.canvas_width * 0.1
        this.hmargin_to_frame = this.canvas_height * 0.1
        this.wmargin_to_plot = this.canvas_width * 0.15
        this.hmargin_to_plot = this.canvas_height * 0.15
        this.bins = bins
        this.max_freq = max_freq

        this.canvas.delete( "all" )
        this.canvas.config( width = this.canvas_width, height = this.canvas_height )
        
        this.init_histogram()
    
    def set_weights( this, weights ):
        for i in range( this.bins ):
            this.active_weights[ i ] = weights[ i ]
            #bin_index = this.where_id_is( this.bin_ids[ i ] )
            bin_coords = this.canvas.coords( this.bin_ids[ i ] )
            this.canvas.coords(
                this.bin_ids[ i ],
                bin_coords[ 0 ],
                bin_coords[ 3 ] - weights[ i ] * this.height_unit,
                *bin_coords[ 2 : 4 ]
            )


class App:
    def __init__( this ): # PERMITIR QUE EL TAMAÑO DE LA VENTANA SEA VARIABLE (DEFINIDO POR EL USUARIO)
        this.main = tk.Tk()
        this.main.geometry( "800x500" )
        
        this.histogram = Histogram( this.main, 500, 500 )
        this.histogram.canvas.place( x = 0, y = 0 )
        # QUITAR
        """
        this.histogram.canvas.place( x = 0, y = 0 )
        this.mean_display.place( x = 500, y = 500 * 0.1 )
        this.std_display.place( x = 500, y = 500 * 0.1 + 20 )
        this.pm_display.place( x = 500, y = 500 * 0.1 + 40 )
        this.animation_run.place( x = 500 * 0.1, y = 460 )
        this.animation_select.place( x = 500 * 0.1 + 70, y = 462 )
        """

app = App()
app.main.mainloop()