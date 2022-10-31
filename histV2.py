import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WeightedStats:
    def __init__( this, values, weights ):
        this.values = values
        this.weights = weights
        this.stats_vector = [ 0 for _ in range( 6 ) ] # MODIFICAR EN FUNCION DE NUMERO DE METRICAS
    
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
    
    def spread( this ):
        s = 0
        l = float( "inf" )
        h = -float( "inf" )
        for i in range( len( this.weights ) ):
            if( this.weights[ i ] > 0 ):
                if( this.values[ i ] < l ):
                    l = this.values[ i ]
                if( this.values[ i ] > h ):
                    h = this.values[ i ]
        if( l != float( "inf" ) and h != -float( "inf" ) ):
            s = h - l
        return s / 1.0
    
    def coverage( this ):
        c = 0
        a = 1.0 / len( this.weights )
        for i in range( len( this.weights ) ):
            if( this.weights[ i ] == 0 ):
                c += a
        return c / len( this.weights )
    
    def region( this ):
        r = 0
        i = 0
        while( i < len( this.weights ) ):
            while( i < len( this.weights ) and this.weights[ i ] == 0 ):
                i += 1
            r += 1
            i += 1
        return r

    def gen_stats_vector( this ):
        this.stats_vector[ 0 ] = this.mean()
        this.stats_vector[ 1 ] = this.std()
        this.stats_vector[ 2 ] = this.pm()
        this.stats_vector[ 3 ] = this.spread()
        this.stats_vector[ 4 ] = this.coverage()
        this.stats_vector[ 5 ] = this.region()

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
            this.mean_display.config( text = f"MEAN = {mean:.2f}" )
            this.std_display.config( text = f"STD = {std:.2f}" )
        else:
            this.mean_display.config( text = f"MEAN = UNDEFINED" )
            this.std_display.config( text = f"STD = UNDEFINED" )
        pm = stats.pm()
        this.pm_display.config( text = f"PM = {pm:.1f}" )

    def init_histogram( this ):
        this.yspace = this.canvas_height - 2 * this.hmargin_to_plot
        this.xspace = this.canvas_width - 2 * this.wmargin_to_plot
        this.height_unit = this.yspace / this.max_freq
        this.bin_width = this.xspace / this.bins
        this.histogram_frame = this.canvas.create_rectangle( this.wmargin_to_frame,
                                                        this.hmargin_to_frame,
                                                        this.canvas_width - this.wmargin_to_frame,
                                                        this.canvas_height - this.hmargin_to_frame,
                                                        fill = "white" )
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
            this.bin_ids.append( this.canvas.create_rectangle( this.wmargin_to_plot + i * this.xspace / this.bins,
                                          this.canvas_height - this.hmargin_to_plot - this.height_unit,
                                          this.wmargin_to_plot + ( i + 1 ) * this.xspace / this.bins,
                                          this.canvas_height - this.hmargin_to_plot,
                                          fill = "blue" ) )
            this.active_weights[ i ] = 1.0
            this.active_values[ i ] = 1.0 / ( this.bins * 2 ) + i / this.bins

    def __init__( this, app, width, height, bins = 10, max_freq = 10 ):
        this.mean_display = app.mean_display
        this.std_display = app.std_display
        this.pm_display = app.pm_display
        this.canvas_width = width
        this.canvas_height = height
        this.wmargin_to_frame = this.canvas_width * 0.1
        this.hmargin_to_frame = this.canvas_height * 0.1
        this.wmargin_to_plot = this.canvas_width * 0.15
        this.hmargin_to_plot = this.canvas_height * 0.15
        this.bins = bins
        this.max_freq = max_freq
        this.canvas = tk.Canvas( app.main,
                                 width = this.canvas_width,
                                 height = this.canvas_height )
        this.canvas.bind( "<Button-1>", this.on_press )
        this.canvas.bind( "<B1-Motion>", this.on_move_press )
        this.init_histogram()
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
    def define_animations( this ):
        this.animations = []
        
        this.animations.append(
            [ [ 10, 0, 0, 5, 0, 0, 0, 0, 0, 5 ],
              [ 10, 0, 0, 0, 5, 0, 0, 0, 5, 0 ],
              [ 10, 0, 0, 0, 0, 5, 0, 5, 0, 0 ],
              [ 10, 0, 0, 0, 0, 0, 10, 0, 0, 0 ] ]
        )
        """
        this.animations.append(
            [ [ 10, 0, 0, 0, 5, 0, 0, 0, 5, 0 ],
              [ 10, 0, 0, 0, 4, 1, 0, 1, 4, 0 ],
              [ 10, 0, 0, 0, 3, 2, 0, 2, 3, 0 ],
              [ 10, 0, 0, 0, 2, 3, 0, 3, 2, 0 ],
              [ 10, 0, 0, 0, 1, 4, 0, 4, 1, 0 ],
              [ 10, 0, 0, 0, 0, 5, 0, 5, 0, 0 ],
              [ 10, 0, 0, 0, 0, 4, 2, 4, 0, 0 ],
              [ 10, 0, 0, 0, 0, 3, 4, 3, 0, 0 ],
              [ 10, 0, 0, 0, 0, 2, 6, 2, 0, 0 ],
              [ 10, 0, 0, 0, 0, 1, 8, 1, 0, 0 ],
              [ 10, 0, 0, 0, 0, 0, 10, 0, 0, 0 ] ]
        )
        
        this.animations.append(
            [ [ 10, 0, 0, 0, 5, 0, 0, 0, 5, 0 ],
              [ 10, 0, 0, 0, 4, 1, 0, 1, 4, 0 ],
              [ 10, 0, 0, 0, 3, 1, 2, 1, 3, 0 ],
              [ 10, 0, 0, 0, 2, 1, 4, 1, 2, 0 ],
              [ 10, 0, 0, 0, 1, 1, 6, 1, 1, 0 ],
              [ 10, 0, 0, 0, 0, 1, 8, 1, 0, 0 ],
              [ 10, 0, 0, 0, 0, 0, 10, 0, 0, 0 ] ]
        )
        """
        """
        this.animations.append(
            [ [ 10, 0, 0, 0, 0, 3, 0, 0, 0, 6 ],
              [ 10, 0, 0, 0, 0, 2, 1, 0, 0, 6 ],
              [ 10, 0, 0, 0, 0, 1, 1, 1, 0, 6 ],
              [ 10, 0, 0, 0, 0, 0, 1, 2, 0, 6 ],
              [ 10, 0, 0, 0, 0, 0, 0, 3, 0, 6 ] ]
        )
        """
        this.animations.append(
            [ [ 10, 0, 0, 0, 3, 0, 0, 0, 0, 6 ],
              [ 10, 0, 0, 0, 0, 3, 0, 0, 0, 6 ],
              [ 10, 0, 0, 0, 0, 0, 3, 0, 0, 6 ],
              [ 10, 0, 0, 0, 0, 0, 0, 3, 0, 6 ] ]
        )
        this.animations.append(
            [ [ 6, 0, 0, 0, 0, 8, 0, 0, 0, 6 ],
              [ 6, 0, 0, 0, 4, 0, 4, 0, 0, 6 ],
              [ 6, 0, 0, 4, 0, 0, 0, 4, 0, 6 ],
              [ 6, 0, 4, 0, 0, 0, 0, 0, 4, 6 ],
              [ 6, 4, 0, 0, 0, 0, 0, 0, 0, 10 ],
              [ 10, 0, 0, 0, 0, 0, 0, 0, 0, 10 ] ]
        )

    def animation_routine( this, animation, select ):
        this.histogram.set_weights( animation[ select ] )
        this.histogram.update_stats()
        stats = WeightedStats( this.histogram.active_values, this.histogram.active_weights )
        stats.gen_stats_vector()
        #print( stats.stats_vector )
        for i in range( len( stats.stats_vector ) ):
            this.stats_progressions[ i ][ select ] = stats.stats_vector[ i ]
        if( select < len( animation ) - 1 ):
            this.main.after( 1500, this.animation_routine, animation, select + 1 )
        else:
            this.animation_running = False

    def prepare_animation( this ):
        if( not this.animation_running ):
            this.animation_running = True
            this.histogram.reset( this.histogram.canvas_width, this.histogram.canvas_width )
            animation = this.animations[ this.animation_select.current() ]
            this.last_animation_size = len( animation )
            this.histogram.set_weights( animation[ 0 ] )
            this.histogram.update_stats()
            stats = WeightedStats( this.histogram.active_values, this.histogram.active_weights )
            stats.gen_stats_vector()
            for i in range( len( stats.stats_vector ) ):
                this.stats_progressions[ i ][ 0 ] = stats.stats_vector[ i ]
            this.main.after( 1500, this.animation_routine, animation, 1 )

    def plot_progressions( this ):
        if( not this.animation_running ):
            progs = this.stats_progressions[ this.progression_select.current() ]
            fig = Figure( figsize = ( 5, 5 ), dpi = 50 )
            progs_plot = fig.add_subplot( 111 )
            progs_plot.plot( progs[ : this.last_animation_size ] )

            canvas = FigureCanvasTkAgg( fig, master = this.main )
            canvas.draw()

            canvas.get_tk_widget().place( x = 505, y = 500 * 0.1 + 150 )

    def __init__( this ): # PERMITIR QUE EL TAMAÑO DE LA VENTANA SEA VARIABLE (DEFINIDO POR EL USUARIO)
        this.define_animations()
        this.stats_progressions = [ [ 0 for _ in range( 20 ) ] for _ in range( 6 ) ] # HAY QUE MODIFICAR SEGUN NUMERO DE METRICAS
        this.last_animation_size = 0
        this.animation_running = False
        this.main = tk.Tk()
        this.main.geometry( "800x500" )
        this.mean_display = tk.Label( this.main, background = "white", borderwidth = 1, relief = "solid" )
        this.std_display = tk.Label( this.main, background = "white", borderwidth = 1, relief = "solid" )
        this.pm_display = tk.Label( this.main, background = "white", borderwidth = 1, relief = "solid" )
        this.histogram = Histogram( this, 500, 500 )
        this.animation_run = tk.Button( this.main, text = "Animate: ", command = this.prepare_animation )
        this.animation_select = ttk.Combobox( this.main, width = 8 )
        this.animation_select[ "values" ] = ( "Axiom-1", "Axiom-2", "Axiom-3" )
        this.animation_select[ "state" ] = "readonly"
        this.animation_select.current( 0 )
        this.view_progressions = tk.Button( this.main, text = "Plot: ", command = this.plot_progressions )
        this.progression_select = ttk.Combobox( this.main, width = 10 )
        this.progression_select[ "values" ] = ( "MEAN", "STD", "PM", "SPD", "COV", "REG" )
        this.progression_select[ "state" ] = "readonly"
        this.progression_select.current( 0 )

        this.histogram.canvas.place( x = 0, y = 0 )
        this.mean_display.place( x = 505, y = 500 * 0.1 )
        this.std_display.place( x = 505, y = 500 * 0.1 + 25 )
        this.pm_display.place( x = 505, y = 500 * 0.1 + 50 )
        this.animation_run.place( x = 500 * 0.1, y = 460 )
        this.animation_select.place( x = 500 * 0.1 + 70, y = 460 )
        this.view_progressions.place( x = 505, y = 500 * 0.1 + 100 )
        this.progression_select.place( x = 505 + 45, y = 500 * 0.1 + 100 )

app = App()
app.main.mainloop()