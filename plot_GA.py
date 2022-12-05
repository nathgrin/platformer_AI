
from GA import *
import matplotlib.pyplot as plt
import corner


def main():
    
    
    
    fname = "GA_out.dat"
    
    theGA = myGA()
    all_gens = theGA.read_file(fname)
    
    # print(all_gens)
    
    data_arr = [ [] for i in range(6) ]
    for gen in all_gens:
        for entry in gen:
            data_arr[0].append(entry[0])
            data_arr[-1].append(entry[2])
            for i,e in enumerate(entry[1]):
                data_arr[i+1].append(e)
    data_arr = np.array(data_arr).transpose()
    print(data_arr)
    
    figure = corner.corner(
    data_arr,
    labels=[
        r"gen",
        r"w1",
        r"w2",
        r"w3",
        r"w4",
        r"score",
    ],
    quantiles=[0.16, 0.5, 0.84],
    plot_contours=False,
    show_titles=True,
    title_kwargs={"fontsize": 12},
    )
    
    plt.show()
    
if __name__ == "__main__":
    main()