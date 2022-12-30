
from GA import *
from misc_func import *
import matplotlib.pyplot as plt
import corner
from typing import Optional,Literal
import matplotlib as mpl

### MatplotlibRCs # See actually misc_func but for now ..

plt.rc('font',family='STIXGeneral',size=20) # STIX looks like latex
plt.rc('mathtext',fontset='stix')
plt.rc('figure', figsize=(1.41421356237*6.,6.) )
plt.rc('figure.subplot', right=0.96464466094,top=0.95 )
plt.rc('lines', linewidth=1.8,marker=None,markersize=8 )
plt.rc('axes', linewidth=1.5,labelsize=24,prop_cycle=plt.cycler(color=('k','r','c','darkorange','steelblue','hotpink','gold','b','maroon','darkgreen')) )
plt.rc(('xtick.major','ytick.major'), size=5.2,width=1.5)
plt.rc(('xtick.minor','ytick.minor'), size=3.2,width=1.5,visible=True)
plt.rc(('xtick','ytick'), labelsize=20, direction='in' )
plt.rc(('xtick'), top=True,bottom=True ) # For some stupid reason you have to do these separately
plt.rc(('ytick'), left=True,right=True )
plt.rc('legend',numpoints=1,scatterpoints=1,labelspacing=0.2,fontsize=18,fancybox=True,handlelength=1.5,handletextpad=0.5)
plt.rc('savefig', dpi=150,format='pdf',bbox='tight' )
plt.rc('errorbar',capsize=3.)

plt.rc('image',cmap='gist_rainbow')


# Adusted:
plt.rc('lines', markersize=6 )
plt.rc('axes', labelsize=12 )
plt.rc(('xtick','ytick'), labelsize=12 )


def make_data_from_generationlist(all_gens:list)->list:
    
    out = []
    for generation,settings in all_gens:
        
        for individual in generation:
            entry = []
            entry.append(generation.n)
            entry.extend(individual['chromosome'])
            entry.append(individual['score'])
            
            out.append(entry)
    
    return np.array(out)


def make_cornerplot(loc,all_gens):
    
    data_arr = make_data_from_generationlist(all_gens)
    
    # print(data_arr)
    
    figure = corner.corner(
    data_arr,
    labels=[ r"gen" ] + [r"w%i"%(i) for i in range(1,len(data_arr[0])-1)] +[r"score"] ,
    quantiles=[0.16, 0.5, 0.84],
    plot_contours=False,
    show_titles=True,
    title_kwargs={"fontsize": 12},
    )
    
    corner.overplot_points(figure,data_arr,c='r',alpha=0.5)
    
    plt.savefig(loc+"GA_corner.png")
    plt.show()



def text_with_autofit(
    ax: plt.Axes,
    txt: str,
    xy: tuple[float, float],
    width: float, height: float,
    *,
    transform: Optional[mpl.transforms.Transform] = None,
    ha: Literal['left', 'center', 'right'] = 'center',
    va: Literal['bottom', 'center', 'top'] = 'center',
    show_rect: bool = False,
    **kwargs,
) -> mpl.text.Annotation:
    """
    Stolen from https://codereview.stackexchange.com/questions/275079/auto-fitting-text-into-boxes-in-matplotlib
    """
    if transform is None:
        transform = ax.transData

    #  Different alignments give different bottom left and top right anchors.
    x, y = xy
    xa0, xa1 = {
        'center': (x - width / 2, x + width / 2),
        'left': (x, x + width),
        'right': (x - width, x),
    }[ha]
    ya0, ya1 = {
        'center': (y - height / 2, y + height / 2),
        'bottom': (y, y + height),
        'top': (y - height, y),
    }[va]
    a0 = xa0, ya0
    a1 = xa1, ya1

    x0, _ = transform.transform(a0)
    x1, _ = transform.transform(a1)
    # rectangle region size to constrain the text in pixel
    rect_width = x1 - x0

    fig: plt.Figure = ax.get_figure()

    props = mpl.font_manager.FontProperties()
    font = mpl.font_manager.get_font(mpl.font_manager.findfont(props))
    font.set_size(props.get_size_in_points(), fig.dpi)
    angle = 0
    font.set_text(txt, angle, flags=mpl.backends.backend_agg.get_hinting_flag())
    w, _ = font.get_width_height()
    subpixels = 64
    adjusted_size = props.get_size_in_points() * rect_width / w * subpixels
    props.set_size(adjusted_size)

    text: mpl.text.Annotation = ax.annotate(txt, xy, ha=ha, va=va, xycoords=transform, fontproperties=props, **kwargs)

    if show_rect:
        rect = mpl.patches.Rectangle(a0, width, height, fill=False, ls='--')
        ax.add_patch(rect)

    return text

def make_family_tree(all_gens):
    
    all_gens = [all_gens[0]]
    
    # Prepare data
    lengths = []
    for generation in all_gens:
        lengths.append(len(generation))
    
    fig,ax = plt.subplots( figsize=(max(lengths)*2, 3))
       
    plt.subplots_adjust(left=0., right=1., top=1., bottom=0.)
    for sp in ['left','right','top','bottom']:
        ax.spines[sp].set_visible(False)
    ax.tick_params(which='major',top=False,bottom=False,left=False,right=False)
    ax.tick_params(which='minor',top=False,bottom=False,left=False,right=False)
    
    
    
    xmin,dx = 0,10
    ymin,dy = 0,-50
    ax.set_xlim(xmin,xmin+dx*max(lengths))
    ax.set_ylim(ymin,ymin+dy*len(all_gens))
    
    for i,(generation,settings) in enumerate(all_gens):
        print(i,generation)
        scores = generation.serialize('score')
        
        order = np.argsort(scores)[::-1]
        
        print(scores)
        print(order)
        
        y = ymin+dy*(i+0.5)
        
        for j,ind in enumerate(order):
            individual = generation[ind]
            
            x = xmin+dx*(j+0.5)
            
            print(x,y)
            
            thetext = str(individual['score'])+ " " + individual['genome'] + "\n"
            thetext += individual['id']
            
            from matplotlib.textpath import TextPath
            from matplotlib.patches import PathPatch


            tp = TextPath((x,y), thetext, size=0.4)
            ax.add_patch(PathPatch(tp, color="black"))
            
            
            # text_with_autofit(ax,thetext,(x,y),dx,dy, show_rect=True)
            
            # boxprops = dict(facecolor='none', edgecolor='black', boxstyle='round,pad=0.1')
            # ax.text(x,y,the_str,size=8,ha='center',va='center',bbox=boxprops)
            
        
        
        
        
    plt.show()
    
    
    
    
    

def main():
    
    
    loc = "data/"
    fname = "GA_out.dat"
    
    theGA = myGA()
    all_gens = theGA.read_file(loc+fname)
    
    make_cornerplot(loc,all_gens)
    
    # make_family_tree(loc,all_gens)
    
    
if __name__ == "__main__":
    main()