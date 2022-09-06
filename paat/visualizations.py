import matplotlib.pyplot as plt

def autocalibration_plots(segments, file_path=None):
    fig = plt.figure(figsize=(10,3.5))
    ax1, ax2, ax3 = fig.subplots(1,3)

    xs, ys, zs = segments[:, 0], segments[:, 1], segments[:,2]
    fig.suptitle('Autocalibration diagnostic plots')


    ax1.scatter(xs, ys, s=.5)
    cir = plt.Circle((0, 0), 1, color='black',fill=False)
    ax1.add_patch(cir)
    ax1.set_xlabel('X Label')
    ax1.set_ylabel('Y Label')
    ax1.set_aspect('equal', 'box')
    ax1.set_xticks([-1, -.5, 0, .5, 1], labels=[-1, -.5, 0, .5, 1])
    ax1.set_yticks([-1, -.5, 0, .5, 1], labels=[-1, -.5, 0, .5, 1])

    ax2.scatter(xs, zs, s=.5)
    cir = plt.Circle((0, 0), 1, color='black',fill=False)
    ax2.add_patch(cir)
    ax2.set_xlabel('X Label')
    ax2.set_ylabel('Z Label')
    ax2.set_aspect('equal', 'box')
    ax2.set_xticks([-1, -.5, 0, .5, 1], labels=[-1, -.5, 0, .5, 1])
    ax2.set_yticks([-1, -.5, 0, .5, 1], labels=[-1, -.5, 0, .5, 1])

    ax3.scatter(ys, zs, s=.5)
    cir = plt.Circle((0, 0), 1, color='black',fill=False)
    ax3.add_patch(cir)
    ax3.set_xlabel('Y Label')
    ax3.set_ylabel('Z Label')
    ax3.set_aspect('equal', 'box')
    ax3.set_xticks([-1, -.5, 0, .5, 1], labels=[-1, -.5, 0, .5, 1])
    ax3.set_yticks([-1, -.5, 0, .5, 1], labels=[-1, -.5, 0, .5, 1])

    fig.tight_layout()

    if file_path:
        plt.savefig(file_path)
    else:
        plt.show()
