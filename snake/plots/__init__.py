import pylab

def fullscreen():

    mng = pylab.get_current_fig_manager() #TkAgg
    mng.resize(*mng.window.maxsize())