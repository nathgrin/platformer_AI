
from GA import *
import matplotlib.pyplot as plt
import corner


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

def main():
    
    
    
    fname = "GA_out.dat"
    
    theGA = myGA()
    all_gens = theGA.read_file(fname)
    
    data_arr = make_data_from_generationlist(all_gens)
    
    print(data_arr)
    
    figure = corner.corner(
    data_arr,
    labels=[ r"gen" ] + [r"w%i"%(i) for i in range(1,len(data_arr[0])-1)] +[r"score"] ,
    quantiles=[0.16, 0.5, 0.84],
    plot_contours=False,
    show_titles=True,
    title_kwargs={"fontsize": 12},
    )
    
    corner.overplot_points(figure,data_arr,c='r',alpha=0.5)
    
    plt.savefig("GAout.png")
    plt.show()
    
if __name__ == "__main__":
    main()