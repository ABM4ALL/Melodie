from scipy.stats import lognorm
import numpy as np
import matplotlib.pyplot as plt


mean = 0
dist1 = lognorm(0.2, loc=mean)
dist2 = lognorm(0.5, loc=mean)
dist3 = lognorm(0.8, loc=mean)
dist4 = lognorm(1.1,loc=mean)
dist5 = lognorm(1.4,loc=mean)
x = np.linspace(0,6,200)


def save_fig(fig, fig_name):
    fig.savefig(fig_name + ".png", dpi=200, format="PNG")
    plt.close(fig)

def plot_lognomal(values_dict):
    figure = plt.figure(figsize=(12, 6), dpi=200, frameon=False)
    ax = figure.add_axes((0.1, 0.15, 0.8, 0.75))

    for key, values in values_dict.items():
        generation_list = list(range(len(values)))
        ax.plot(generation_list, values, label=key)

    ax.legend()

    fig_name = "lognormal_distribution"
    save_fig(figure, fig_name)



#
# values_dict = {
#     "sigma_1": dist1.pdf(x),
#     "sigma_2": dist2.pdf(x),
#     "sigma_3": dist3.pdf(x),
#     "sigma_4": dist4.pdf(x),
#     "sigma_5": dist5.pdf(x),
# }
# plot_lognomal(values_dict)

# l = [(1, 2), (3, 1), (2, 5)]
# l_rev = sorted(l, key=lambda x: x[1], reverse=True)
print([round(0.4 + 0.1 * i, 1) for i in range(0, 10)])